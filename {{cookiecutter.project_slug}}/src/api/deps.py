from __future__ import annotations

from ..core.config import settings
from ..repository.redis_repo import RedisRepository
from ..services.tasks_service import TasksService


def get_redis_repo() -> RedisRepository:
    """Return a Redis repository instance."""
    return RedisRepository(url=settings.redis.url)


def get_tasks_service(repo: RedisRepository | None = None) -> TasksService:
    """Return a TasksService with provided repository."""
    return TasksService(repo or get_redis_repo())


__all__ = ["get_redis_repo", "get_tasks_service"]
