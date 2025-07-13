import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator, List, Optional

@dataclass
class Span:
    name: str
    start: float
    end: Optional[float] = None

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

tracer = DummyTracer()

__all__ = ["tracer", "DummyTracer", "Span"]
