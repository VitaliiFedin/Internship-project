from fastapi import APIRouter, Depends
from app.schemas.user_schemas import *
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.services.user_services import *
from app.db import models
from app.services.user_services import add_user, get_users
from typing import List

user = APIRouter()


@user.post('/users/add', response_model=UserSignupRequest)
async def post_user(user_in: UserSignupRequest, session: AsyncSession = Depends(get_session)):
    new_user = add_user(session=session, obj_in=user_in)
    session.add(new_user)
    await session.commit()
    return new_user


@user.get('/users')
async def get_all_users(session: AsyncSession = Depends(get_session)):
    all_users = await get_users(session)
    return all_users


@user.get('/users/{user_id}')
async def get_user232(user_id: int, session: AsyncSession = Depends(get_session)):
    _user = await session.execute(select(models.User).filter(models.User.id == user_id))
    return _user.scalars().all()

