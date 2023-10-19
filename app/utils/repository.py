from abc import abstractmethod, ABC
from datetime import datetime, timedelta
from typing import Union, Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_pagination import Params, paginate
from jose import jwt
from pydantic import ValidationError
from sqlalchemy import select
from starlette import status

from app.config import JWTConfig
from app.core.exception import NoSuchId, EmailExist, PhoneExist, ForbiddenToUpdate, \
    ForbiddenToDelete
from app.core.security import get_password_hash, verify_password
from app.db import models
from app.db.database import async_session
from app.schemas.token_schemas import TokenPayload, UserAuth
from app.schemas.user_schemas import UserSignupRequest, UserUpdateRequest, User

settings = JWTConfig()
reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)


class AbstractRepository(ABC):
    @abstractmethod
    async def get_one_user(self):
        raise NotImplementedError

    @abstractmethod
    async def get_all_users(self):
        raise NotImplementedError

    @abstractmethod
    async def create_new_user(self):
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self):
        raise NotImplementedError

    @abstractmethod
    async def update_user(self):
        raise NotImplementedError

    @abstractmethod
    async def check_email(self):
        raise NotImplementedError

    @abstractmethod
    async def check_phone(self):
        raise NotImplementedError

    @abstractmethod
    async def get_user_id(self):
        raise NotImplementedError

    @abstractmethod
    async def get_all_users_paginated(self):
        raise NotImplementedError

    @abstractmethod
    async def get_current_user_dependency(self):
        raise NotImplementedError


class SQLAlchemyRepository(ABC):
    model = None

    async def check_email(self, obj_in: User):
        async with async_session() as session:
            email_check = await session.execute(select(models.User).where(models.User.email == obj_in.email))
            email_check = email_check.scalar()
            if email_check:
                raise EmailExist

    async def check_phone(self, obj_in: User):
        async with async_session() as session:
            phone_check = await session.execute(select(models.User).where(models.User.phone == obj_in.phone))
            phone_check = phone_check.scalar()
            if phone_check:
                raise PhoneExist

    async def get_user_id(self, user_id: int):
        async with async_session() as session:
            result = await session.execute(select(models.User).filter(models.User.id == user_id))
            result = result.scalar()
            if not result:
                raise NoSuchId
            return result

    async def get_one_user(self, user_id: int):
        async with async_session() as session:
            result = await self.get_user_id(user_id)
        return result

    async def get_all_users(self, params: Params = Depends()):
        async with async_session() as session:
            result = await session.execute(select(self.model))
            result = result.scalars().all()
            return paginate(result, params)

    async def create_new_user(self, obj_in: UserSignupRequest):
        async with async_session() as session:
            await self.check_email(obj_in)
            await self.check_phone(obj_in)
            _user = self.model(
                email=obj_in.email,
                firstname=obj_in.firstname,
                lastname=obj_in.lastname,
                city=obj_in.city,
                hashed_password=get_password_hash(obj_in.hashed_password),
                phone=obj_in.phone
            )
            session.add(_user)
            await session.commit()
            return _user

    async def delete_user(self, user_id: int, current_user: User):
        async with async_session() as session:
            result = await self.get_user_id(user_id)
            if current_user.id != result.id:
                raise ForbiddenToDelete
            user_to_show = result
            await session.delete(result)
            await session.commit()
            return user_to_show

    async def update_user(self, user_id: int, current_user: User, obj_in=UserUpdateRequest):
        async with async_session() as session:
            result = await session.execute(select(self.model).filter(self.model.id == user_id))
            result = result.scalar()
            if not result:
                raise NoSuchId
            if current_user.id != result.id:
                raise ForbiddenToUpdate
            for key, value in obj_in.model_dump(exclude_unset=True).items():
                setattr(result, key, value)
                if key == 'hashed_password':
                    setattr(result, 'hashed_password', get_password_hash(obj_in.hashed_password))
                await session.commit()
            return result


class AbstractRepositoryJWT(ABC):
    @abstractmethod
    async def get_current_user(self):
        raise NotImplementedError

    @abstractmethod
    async def create_access_token(self):
        raise NotImplementedError

    @abstractmethod
    async def create_refresh_token(self):
        raise NotImplementedError

    @abstractmethod
    async def create_user(self):
        raise NotImplementedError

    @abstractmethod
    async def login(self):
        raise NotImplementedError


class JWTRepository(AbstractRepositoryJWT):
    model = None

    def __init__(self, form_data=OAuth2PasswordRequestForm):
        self.form_data = form_data

    async def get_current_user(self, token: str = Depends(reuseable_oauth)):
        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.algorithm]
            )
            token_data = TokenPayload(**payload)
            print(token_data)

            if datetime.fromtimestamp(token_data.exp) < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except(jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        async with async_session() as session:
            db = await session.execute(select(self.model).filter(self.model.email == token_data.sub))
            db = db.scalar()
            if db is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Could not find user",
                )
            return db

    async def create_access_token(self, subject: Union[str, Any], expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode = {"exp": expires_delta, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, settings.algorithm)
        return encoded_jwt

    async def create_refresh_token(self, subject: Union[str, Any], expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_minutes)

        to_encode = {"exp": expires_delta, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, settings.jwt_refresh_secret_key, settings.algorithm)
        return encoded_jwt

    async def create_user(self, data: UserAuth):
        async with async_session() as session:
            email_check = await session.execute(select(self.model).where(self.model.email == data.email))
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

    async def login(self, form_data: OAuth2PasswordRequestForm = Depends()):
        async with async_session() as session:
            email_check = await session.execute(select(self.model).filter(self.model.email == form_data.username))
            email_check = email_check.scalar()
            if email_check is None:
                raise EmailExist
            user = await session.execute(select(self.model).filter(self.model.email == form_data.username))
            user = user.scalar()
            hashed_pass = user.hashed_password
            if not verify_password(form_data.password, hashed_pass):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect email or password"
                )

        return {
            "access_token": await self.create_access_token(user.email),
            "refresh_token": await self.create_refresh_token(user.email),
        }


class AbstractRepositoryCompany(ABC):
    @abstractmethod
    async def get_one_company(self):
        raise NotImplementedError

    @abstractmethod
    async def get_all_companies(self):
        raise NotImplementedError

    @abstractmethod
    async def create_new_company(self):
        raise NotImplementedError

    @abstractmethod
    async def delete_company(self):
        raise NotImplementedError

    @abstractmethod
    async def update_company(self):
        raise NotImplementedError

    @abstractmethod
    async def get_company_by_id(self):
        raise NotImplementedError

    @abstractmethod
    async def check_phone(self):
        raise NotImplementedError

    @abstractmethod
    async def make_admin(self):
        raise NotImplementedError

    @abstractmethod
    async def remove_admin(self):
        raise NotImplementedError

    @abstractmethod
    async def get_all_admins(self):
        raise NotImplementedError

class AbstractRepositoryAction(ABC):
    @abstractmethod
    async def invite_user(self):
        raise NotImplementedError

    @abstractmethod
    async def all_invitations(self):
        raise NotImplementedError

    @abstractmethod
    async def cancel_invitation(self):
        raise NotImplementedError

    @abstractmethod
    async def accept_invitation(self):
        raise NotImplementedError

    @abstractmethod
    async def request_to_join_company(self):
        raise NotImplementedError

    @abstractmethod
    async def all_requests(self):
        raise NotImplementedError

    @abstractmethod
    async def decline_request_to_join_company(self):
        raise NotImplementedError

    @abstractmethod
    async def all_request_to_company(self):
        raise NotImplementedError

    @abstractmethod
    async def company_all_invitations(self):
        raise NotImplementedError

    @abstractmethod
    async def company_response(self):
        raise NotImplementedError

    @abstractmethod
    async def company_kick_user(self):
        raise NotImplementedError

    @abstractmethod
    async def user_leave_company(self):
        raise NotImplementedError

    @abstractmethod
    async def get_all_members(self):
        raise NotImplementedError


class AbstractRepositoryQuizz(ABC):
    @abstractmethod
    async def create_quizz(self):
        raise NotImplementedError

    @abstractmethod
    async def get_all_quizzes(self):
        raise NotImplementedError

    @abstractmethod
    async def update_quizz(self):
        raise NotImplementedError

    @abstractmethod
    async def delete_quizz(self):
        raise NotImplementedError


class AbstractRepositoryRedis(ABC):
    @abstractmethod
    async def save_to_redis(self):
        raise NotImplementedError

    @abstractmethod
    async def read_from_redis(self):
        raise NotImplementedError