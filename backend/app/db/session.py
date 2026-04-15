from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


class DatabaseSingleton:
    _engine = None
    _session_factory = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            settings = get_settings()
            cls._engine = create_async_engine(settings.async_database_url, pool_pre_ping=True)
        return cls._engine

    @classmethod
    def get_session_factory(cls):
        if cls._session_factory is None:
            cls._session_factory = async_sessionmaker(bind=cls.get_engine(), class_=AsyncSession, expire_on_commit=False)
        return cls._session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = DatabaseSingleton.get_session_factory()
    async with session_factory() as session:
        yield session
