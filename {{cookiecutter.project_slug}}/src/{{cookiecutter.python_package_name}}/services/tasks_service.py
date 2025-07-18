from __future__ import annotations

"""Service providing task queueing and metric collection."""

from datetime import UTC, datetime
from typing import Any, Dict, List, Tuple, cast
from uuid import uuid4

import json
import psutil

try:
    import GPUtil  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    GPUtil = None  # type: ignore[assignment]

GPU_AVAILABLE: bool = GPUtil is not None

import asyncio

from ..repository.redis_repo import RedisRepository
from ..core.logging_config import get_logger
from ..utils import (
    TASKS_STREAM_NAME,
    DEAD_LETTER_STREAM_NAME,
    statsd_client,
    tracer,
)

log = get_logger(__name__)


class TasksService:
    """Service handling task enqueueing and metrics reporting."""

    def __init__(self, repo: RedisRepository) -> None:
        """Initialize the service with a repository instance."""
        self.repo = repo
        self.cpu_samples: List[float] = []
        self.mem_samples: List[float] = []
        self.gpu_load_samples: List[float] = []
        self.gpu_mem_samples: List[float] = []

    @staticmethod
    def _calculate_metrics(values: List[float]) -> Tuple[float, float, float]:
        """Return average, min and max for provided values."""
        with tracer.start_as_current_span("расчет_метрик"):
            if not values:
                return 0.0, 0.0, 0.0

            avg = sum(values) / len(values)
            return avg, min(values), max(values)

    async def enqueue_task(self, payload: Dict[str, Any]) -> str:
        """Serialize payload and push it to Redis."""
        with tracer.start_as_current_span("постановка_задачи"):
            message = {
                "task_id": str(uuid4()),
                "timestamp": datetime.now(UTC).isoformat(),
                "payload": json.dumps(payload),
                "trace_context": json.dumps({"trace_id": "", "span_id": ""}),
            }
            attempts = 0
            while attempts < 3:
                try:
                    result = await self.repo.add_to_stream(
                        TASKS_STREAM_NAME, message
                    )
                except Exception as exc:  # pragma: no cover - network errors
                    attempts += 1
                    log.error(
                        "Failed to enqueue task (attempt %s)",
                        attempts,
                        exc_info=exc,
                    )
                    if attempts >= 3:
                        try:
                            await self.repo.add_to_stream(
                                DEAD_LETTER_STREAM_NAME, message
                            )
                        except Exception as dead_exc:  # pragma: no cover - network errors
                            log.error(
                                "Failed to enqueue to dead-letter", exc_info=dead_exc
                            )
                        return ""
                    await asyncio.sleep(2 ** (attempts - 1))
                    continue
                else:
                    await self._record_usage()
                    return result

            return ""


    async def _record_usage(self) -> None:
        """Record CPU, memory and GPU usage to StatsD."""
        with tracer.start_as_current_span("запись_использования"):
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            self.cpu_samples.append(cpu)
            self.mem_samples.append(mem)

            cpu_avg, cpu_min, cpu_max = self._calculate_metrics(self.cpu_samples)
            mem_avg, mem_min, mem_max = self._calculate_metrics(self.mem_samples)

            await statsd_client.gauge("cpu.avg", cpu_avg)
            await statsd_client.gauge("cpu.min", cpu_min)
            await statsd_client.gauge("cpu.max", cpu_max)
            await statsd_client.gauge("mem.avg", mem_avg)
            await statsd_client.gauge("mem.min", mem_min)
            await statsd_client.gauge("mem.max", mem_max)

        if GPU_AVAILABLE and GPUtil is not None:
            try:
                gpus = cast(List[Any], GPUtil.getGPUs())  # pyright: ignore[reportUnknownMemberType]
            except Exception:
                gpus = []

            if gpus:
                loads = [float(getattr(g, "load", 0)) * 100 for g in gpus]
                mems = [float(getattr(g, "memoryUtil", 0)) * 100 for g in gpus]
                avg_load = sum(loads) / len(loads)
                avg_mem = sum(mems) / len(mems)
                self.gpu_load_samples.append(avg_load)
                self.gpu_mem_samples.append(avg_mem)
                gl_avg, gl_min, gl_max = self._calculate_metrics(self.gpu_load_samples)
                gm_avg, gm_min, gm_max = self._calculate_metrics(self.gpu_mem_samples)
                await statsd_client.gauge("gpu.load.avg", gl_avg)
                await statsd_client.gauge("gpu.load.min", gl_min)
                await statsd_client.gauge("gpu.load.max", gl_max)
                await statsd_client.gauge("gpu.mem.avg", gm_avg)
                await statsd_client.gauge("gpu.mem.min", gm_min)
                await statsd_client.gauge("gpu.mem.max", gm_max)


__all__ = ["TasksService"]
