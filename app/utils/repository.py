from abc import abstractmethod, ABC

from fastapi import Depends
from fastapi_pagination import Params, paginate
from sqlalchemy import select

from app.core.security import get_password_hash
from app.db import models
from app.db.database import async_session
from app.schemas.user_schemas import UserSignupRequest, UserUpdateRequest, User
from app.core.exception import NoSuchId, EmailExist, PhoneExist


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

    async def delete_user(self, user_id: int):
        async with async_session() as session:
            result = await self.get_user_id(user_id)
            user_to_show = result
            await session.delete(result)
            await session.commit()
            return user_to_show

    async def update_user(self, user_id: int, obj_in=UserUpdateRequest):
        async with async_session() as session:
            result = await session.execute(select(self.model).filter(self.model.id == user_id))
            result = result.scalar()
            await self.check_phone(obj_in)
            if not result:
                raise NoSuchId
            for key, value in obj_in.model_dump(exclude_unset=True).items():
                setattr(result, key, value)
                await session.commit()
            return result
