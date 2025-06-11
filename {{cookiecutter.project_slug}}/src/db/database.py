from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from name.core.config import settings

async_engine = create_async_engine(str(settings.db.assembled_database_url), echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # Important for async code, so objects are accessible after commit.
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_sync_database_url(db_url: str) -> str:
    if "+asyncpg" in db_url:
        return db_url.replace("+asyncpg", "")
    elif "+aiosqlite" in db_url:
        return db_url.replace("+aiosqlite", "")
    return db_url


SYNC_DATABASE_URL = get_sync_database_url(str(settings.db.assembled_database_url))

sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

SessionLocalSync = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


def get_sync_session() -> Generator[Session, None, None]:
    db_session = SessionLocalSync()
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.close()
