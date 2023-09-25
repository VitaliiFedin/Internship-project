from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.db import models
from app.schemas.user_schemas import *


def add_user(session: AsyncSession, obj_in: UserSignupRequest) -> User:
    _user = models.User(
        email=obj_in.email,
        firstname=obj_in.firstname,
        lastname=obj_in.lastname,
        city=obj_in.city,
        hashed_password=obj_in.hashed_password,
        phone=obj_in.phone
    )
    session.add(_user)
    return _user
