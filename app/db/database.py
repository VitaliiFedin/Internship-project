from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@web/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

Model = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
