from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import get_password_hash
from app.db import models
from app.schemas.user_schemas import *


def add_user(session: AsyncSession, obj_in: UserSignupRequest) -> User:
    _user = models.User(
        email=obj_in.email,
        firstname=obj_in.firstname,
        lastname=obj_in.lastname,
        city=obj_in.city,
        hashed_password=get_password_hash(obj_in.hashed_password),
        phone=obj_in.phone
    )
    session.add(_user)
    return _user


async def get_users(session: AsyncSession):
    result = await session.execute(select(models.User))
    return result.scalars().all()

