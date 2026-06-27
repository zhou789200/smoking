from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declared_attr, DeclarativeBase
from app.config import settings

# Detect if PostgreSQL or SQLite for engine options
_is_pg = "postgresql" in settings.DATABASE_URL

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=5 if _is_pg else None,
    max_overflow=10 if _is_pg else None,
    pool_pre_ping=_is_pg,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
