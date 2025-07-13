import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator, List

from ..core.config import settings

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    provider = TracerProvider(
        resource=Resource.create({SERVICE_NAME: "simplemspy"})
    )
    jaeger_exporter = JaegerExporter(
        collector_endpoint=f"http://{settings.jaeger.host}:{settings.jaeger.port}/api/traces"
    )
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    trace.set_tracer_provider(provider)
    _otel_tracer = trace.get_tracer(__name__)
    USE_OTEL = True
except Exception:  # pragma: no cover - fallback when opentelemetry not installed
    USE_OTEL = False


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
        start_time = time.time()
        with _otel_tracer.start_as_current_span(name):
            span = Span(name=name, start=start_time)
            self.spans.append(span)
            try:
                yield span
            finally:
                span.end = time.time()


def _get_tracer() -> DummyTracer:
    if USE_OTEL:
        return OtelTracer()
    return DummyTracer()


tracer = _get_tracer()

__all__ = ["DummyTracer", "Span", "tracer"]
