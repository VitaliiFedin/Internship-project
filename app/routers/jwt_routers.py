from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi_pagination import Page, Params
from sqlalchemy import select
from starlette import status

from app.core.exception import EmailExist
from app.core.jwt import create_access_token, create_refresh_token
from app.core.security import get_password_hash, verify_password
from app.db.database import async_session
from app.db import models
from app.schemas.token_schemas import TokenSchema, UserAuth, UserOut, SystemUser
from app.repositories.users import UsersRepository
from fastapi.security import OAuth2PasswordRequestForm
from app.core.deps import get_current_user
from fastapi import FastAPI, Body, Depends




jwt = APIRouter()


@jwt.post('/signup', response_model=UserOut)
async def create_user(data: UserAuth):
    async with async_session() as session:
        email_check = await session.execute(select(models.User).where(models.User.email == data.email))
        email_check = email_check.scalar()
        if email_check:
            raise EmailExist
        _user = models.User(
            email=data.email,
            hashed_password=get_password_hash(data.hashed_password)
        )
        session.add(_user)
        await session.commit()
        return _user


@jwt.post('/login', response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    async with async_session() as session:
        email_check = await session.execute(select(models.User).filter(models.User.email == form_data.username))
        email_check = email_check.scalar()
        if email_check is None:
            raise EmailExist
        user = await session.execute(select(models.User).filter(models.User.email == form_data.username))
        user = user.scalar()
        hashed_pass = user.hashed_password
        if not verify_password(form_data.password, hashed_pass):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }


@jwt.get('/me', summary='Get details of currently logged in user', response_model=UserOut)
async def get_me(user: SystemUser = Depends(get_current_user)):
    return user
