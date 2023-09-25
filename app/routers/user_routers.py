from fastapi import APIRouter, Depends
from app.schemas.user_schemas import *
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.services.user_services import *
from app.db import models
from app.services.user_services import add_user

user = APIRouter()

"""
@user.post('/users', response_model=UserSignupRequest)
async def get_all_users(user: UserSignupRequest, session: AsyncSession = Depends(get_session)):
    new_user = models.User(**user.model_dump())
    session.add(new_user)
    await session.commit()

    return new_user
"""


@user.post('/users', response_model=UserSignupRequest)
async def post_user(user_in: UserSignupRequest, session: AsyncSession = Depends(get_session)):
    new_user = add_user(session=session, obj_in=user_in)
    session.add(new_user)
    await session.commit()
    return new_user

"""
@user.post('/users2', response_model=UserSignupRequest)
async def add_user(obj_in: UserSignupRequest, session: AsyncSession = Depends(get_session)) -> User:
    _user = models.User(
                 email=obj_in.email,
                 firstname=obj_in.firstname,
                 lastname=obj_in.lastname,
                 city=obj_in.city,
                 hashed_password=obj_in.hashed_password,
                 phone=obj_in.phone
                 )
    session.add(_user)
    await session.commit()
    return _user
"""