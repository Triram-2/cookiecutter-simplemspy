"""Simplified tracing utilities with optional OpenTelemetry integration."""

# pyright: reportMissingImports=false, reportUnknownMemberType=false, reportUnknownVariableType=false

import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generator, List, Any

from ..core.config import settings

if TYPE_CHECKING:  # pragma: no cover - optional dependency typing
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

try:
    from opentelemetry import trace as ot_trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    provider = TracerProvider(
        resource=Resource.create({SERVICE_NAME: settings.jaeger.service_name})
    )
    endpoint = settings.jaeger.endpoint or (
        f"http://{settings.jaeger.host}:{settings.jaeger.port}/api/traces"
    )
    jaeger_exporter = JaegerExporter(collector_endpoint=endpoint)
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    ot_trace.set_tracer_provider(provider)
    _otel_tracer: Any = ot_trace.get_tracer(__name__)
    use_otel = True
except Exception as exc:
    # If OpenTelemetry initialization fails, fall back to a dummy tracer and
    # log the reason to stderr so that tracing issues are visible in logs.
    import sys

    print(f"OpenTelemetry disabled: {exc}", file=sys.stderr)
    use_otel = False


@dataclass
class Span:
    name: str
    start: float
    end: float | None = None


class DummyTracer:
    """Very small tracer storing spans in memory."""

    def __init__(self) -> None:
        self.spans: List[Span] = []

    @contextmanager
    def start_as_current_span(self, name: str) -> Generator[Span, None, None]:
        """Start and record a span."""
        span = Span(name=name, start=time.time())
        self.spans.append(span)
        try:
            yield span
        finally:
            span.end = time.time()


class OtelTracer(DummyTracer):
    """Wrapper around OpenTelemetry tracer that also stores spans."""

    def __init__(self) -> None:
        super().__init__()

    @contextmanager
    def start_as_current_span(self, name: str) -> Generator[Span, None, None]:
        """Start a span using OpenTelemetry."""
        start_time = time.time()
        with _otel_tracer.start_as_current_span(name):
            span = Span(name=name, start=start_time)
            self.spans.append(span)
            try:
                yield span
            finally:
                span.end = time.time()


def _get_tracer() -> DummyTracer:
    if use_otel:
        return OtelTracer()
    return DummyTracer()


tracer = _get_tracer()


def shutdown_tracer() -> None:
    """Flush pending spans and shutdown the provider."""
    if use_otel:
        try:
            ot_trace.get_tracer_provider().shutdown()  # type: ignore[attr-defined]
        except Exception:
            pass

__all__ = ["DummyTracer", "Span", "tracer", "shutdown_tracer"]
