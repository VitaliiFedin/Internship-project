from abc import abstractmethod, ABC

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db import models
from app.db.database import async_session
from app.schemas.user_schemas import UserSignupRequest, UserUpdateRequest
from app.core.exception import no_such_id, email_already_exist, phone_already_exist
from app.services.user_services import check_email, check_phone, get_user_id


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


class SQLAlchemyRepository(ABC):
    model = None

    async def get_one_user(self, user_id: int):
        async with async_session() as session:

            result = await get_user_id(user_id)
        return result

    async def get_all_users(self):
        async with async_session() as session:
            result = await session.execute(select(self.model))
            return result.scalars().all()

    async def create_new_user(self, obj_in: UserSignupRequest):
        async with async_session() as session:
            await check_email(obj_in)
            await check_phone(obj_in)
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
            result = await get_user_id(user_id)
            user_to_show = result
            await session.delete(result)
            await session.commit()
            return user_to_show

    async def update_user(self, user_id: int, obj_in=UserUpdateRequest):
        async with async_session() as session:
            result = await session.execute(select(self.model).filter(self.model.id == user_id))
            result = result.scalar()
            await check_phone(obj_in)
            if not result:
                no_such_id()
            for key, value in obj_in.model_dump(exclude_unset=True).items():
                setattr(result, key, value)
                await session.commit()
            return result
