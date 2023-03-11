from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import Config

engine = create_async_engine(Config.DB_URL)


@asynccontextmanager
async def get_session():
    try:
        async_session = async_sessionmaker(engine, class_=AsyncSession)

        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()
