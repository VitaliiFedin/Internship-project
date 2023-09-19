from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db/postgres"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

Model = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all())


# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
