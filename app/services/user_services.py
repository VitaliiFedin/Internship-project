from sqlalchemy import select

from app.core.exception import email_already_exist, phone_already_exist, no_such_id
from app.db import models
from app.db.database import async_session
from app.schemas.user_schemas import *


async def check_email(obj_in: User):
    async with async_session() as session:
        email_check = await session.execute(select(models.User).where(models.User.email == obj_in.email))
        email_check = email_check.scalar()
        if email_check:
            email_already_exist()


async def check_phone(obj_in: User):
    async with async_session() as session:
        phone_check = await session.execute(select(models.User).where(models.User.phone == obj_in.phone))
        phone_check = phone_check.scalar()
        if phone_check:
            phone_already_exist()


async def get_user_id(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(models.User).filter(models.User.id == user_id))
        result = result.scalar()
        if not result:
            no_such_id()
        return result
