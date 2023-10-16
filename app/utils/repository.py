from abc import abstractmethod, ABC
from datetime import datetime, timedelta
from typing import Union, Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_pagination import Params, paginate
from jose import jwt
from pydantic import ValidationError
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import text
from starlette import status

from app.config import JWTConfig
from app.core.exception import NoSuchId, EmailExist, PhoneExist, ForbiddenToUpdate, \
    ForbiddenToDelete, ForbiddenToUpdateCompany, ForbiddenToDeleteCompany, ForbiddenToProceed, InvitationNotFound, \
    RequestNotFound
from app.core.security import get_password_hash, verify_password
from app.db import models
from app.db.database import async_session
from app.schemas.action_schemas import InvitationRequest, AnswerResponse
from app.schemas.company_schemas import CompanyCreate, CompanyUpdate, Company
from app.schemas.quizz_schemas import CreateQuizz, UpdateQuizz
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


class CompanyRepository(AbstractRepositoryCompany):
    model = None

    async def check_phone(self, model_to_use: Company):
        async with async_session() as session:
            phone_check = await session.execute(select(self.model).where(self.model.phone == model_to_use.phone))
            phone_check = phone_check.scalar()
            if phone_check:
                raise PhoneExist

    async def get_company_by_id(self, company_id: int, current_user: User):
        async with async_session() as session:
            result = await session.execute(select(self.model).filter(self.model.id == company_id).where(
                or_(self.model.is_visible == True, self.model.owner == current_user.id)))

            result = result.scalar()
            if not result:
                raise NoSuchId
            return result

    async def get_one_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            result = await self.get_company_by_id(company_id, current_user)
        return result

    async def get_all_companies(self, current_user: User, params: Params = Depends()):
        async with async_session() as session:
            result = await session.execute(
                select(self.model).where(or_(self.model.is_visible == True, self.model.owner == current_user.id)))
            result = result.scalars().all()
            return paginate(result, params)

    async def delete_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            company_to_delete = await self.get_company_by_id(company_id, current_user)
            if not company_to_delete:
                raise NoSuchId
            if company_to_delete.owner != current_user.id:
                raise ForbiddenToDeleteCompany
            company_to_show = company_to_delete
            await session.delete(company_to_delete)
            await session.commit()
            return company_to_show

    async def create_new_company(self, model_to_use: CompanyCreate, current_user: User):
        async with async_session() as session:
            await self.check_phone(model_to_use)
            company = self.model(
                name=model_to_use.name,
                title=model_to_use.title,
                description=model_to_use.description,
                city=model_to_use.city,
                phone=model_to_use.phone,
                is_visible=model_to_use.is_visible,
                owner=current_user.id
            )
            session.add(company)
            await session.commit()
            return company

    async def update_company(self, company_id: int, model: CompanyUpdate, current_user: User):
        async with async_session() as session:
            company = await session.execute(select(self.model).filter(self.model.id == company_id))
            company = company.scalar()
            if not company:
                raise NoSuchId
            if company.owner != current_user.id:
                raise ForbiddenToUpdateCompany
            for key, value in model.model_dump(exclude_unset=True).items():
                setattr(company, key, value)
                await session.commit()
            return company

    async def make_admin(self, company_id: int, user_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(models.Company.id == company_id, models.Company.owner == current_user.id))
            company = company.scalar()
            if not company:
                raise ForbiddenToProceed
            user = await session.execute(
                select(models.User).filter(models.User.id == user_id))
            user = user.scalar()
            if not user:
                raise NoSuchId
            if user.id in company.member_ids:
                administrator = models.Administrator(company=company, user=user)
                session.add(administrator)
                await session.commit()
                return {"message": "Administrator appointed"}
            else:
                raise HTTPException(status_code=400, detail="User is not a member of the company")

    async def remove_admin(self, company_id: int, user_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(self.model.id == company_id, self.model.owner == current_user.id))
            company = company.scalar()
            if not company:
                raise ForbiddenToProceed
            user = await session.execute(
                select(models.User).filter(models.User.id == user_id))
            user = user.scalar()
            if not user:
                raise NoSuchId
            administrator = await session.execute(
                select(models.Administrator).filter(models.Administrator.company_id == company_id,
                                                    models.Administrator.user_id == user_id))
            administrator = administrator.scalar()
            if administrator:
                await session.delete(administrator)
                await session.commit()
                return {"message": "Administrator removed"}
            raise HTTPException(status_code=404, detail="Administrator not found")

    async def get_all_admins(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(self.model.id == company_id, self.model.owner == current_user.id))
            company = company.scalar()
            if not company:
                raise ForbiddenToProceed
            admins = await session.execute(
                select(models.Administrator).filter(models.Administrator.company_id == company_id))
            admins = admins.scalars().all()
            return {'Admins': admins}


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


class ActionRepository(AbstractRepositoryAction):
    model = None

    async def invite_user(self, company_id: int, invitation: InvitationRequest, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(models.Company.id == company_id, models.Company.owner == current_user.id))
            company = company.scalar()
            if not company:
                raise ForbiddenToProceed

            invited_user = await session.execute(select(models.User).filter(models.User.id == invitation.user_id))
            invited_user = invited_user.scalar()
            if not invited_user:
                raise NoSuchId
            action = self.model(
                user_id=invited_user.id,
                company_id=company_id,
                action="invite")
            session.add(action)
            await session.commit()
            return {"message": "Invitation sent successfully"}

    async def all_invitations(self, current_user: User):
        async with async_session() as session:
            actions = await session.execute(
                select(self.model).filter(self.model.user_id == current_user.id, self.model.action == 'invite'))
            actions = actions.scalars().all()
            if not actions:
                raise HTTPException(status_code=404, detail="No invitations")
            return {'Invitations': actions}

    async def all_requests(self, current_user: User):
        async with async_session() as session:
            actions = await session.execute(
                select(self.model).filter(self.model.user_id == current_user.id, self.model.action == 'request'))
            actions = actions.scalars().all()
            if not actions:
                raise HTTPException(status_code=404, detail="No requests")
            return {'Requests': actions}

    async def cancel_invitation(self, company_id: int, user_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(models.Company.id == company_id, models.Company.owner == current_user.id))
            company = company.scalar()
            if not company:
                raise ForbiddenToProceed
            invitation = await session.execute(
                select(self.model).filter(self.model.user_id == user_id, self.model.company_id == company_id,
                                          self.model.action == 'invite'))
            invitation = invitation.scalar()
            if invitation:
                await session.delete(invitation)
                await session.commit()
                return {"message": "Invitation canceled"}
            else:
                raise InvitationNotFound

    async def accept_invitation(self, company_id: int, current_user: User, answer: AnswerResponse):
        async with async_session() as session:
            invitation = await session.execute(
                select(self.model).filter(self.model.user_id == current_user.id, self.model.company_id == company_id,
                                          self.model.action == 'invite'))
            invitation = invitation.scalar()
            if not invitation:
                raise InvitationNotFound
            if answer.accept == True:
                await session.delete(invitation)
                company = await session.execute(select(models.Company).filter(models.Company.id == company_id))
                company = company.scalar()
                if not company:
                    raise NoSuchId
                if company.member_ids is None:
                    company.member_ids = []
                company.member_ids.append(current_user.id)
                await session.commit()
                return {'Invitation': 'Accepted'}
            else:
                await session.delete(invitation)
                await session.commit()
                return {'Invitation': 'Declined'}

    async def request_to_join_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(select(models.Company).filter(models.Company.id == company_id))
            company = company.scalar()
            if company.owner == current_user.id or current_user.id in company.member_ids:
                raise HTTPException(status_code=400, detail="You are already a member or owner of this company")
            existing_request = await session.execute(
                select(self.model).filter(self.model.user_id == current_user.id, self.model.company_id == company_id,
                                          self.model.action == 'request'))
            existing_request = existing_request.scalar()
            if existing_request:
                raise HTTPException(status_code=400, detail="You already have a pending request to join this company")

            existing_request_from_company = await session.execute(
                select(self.model).filter(self.model.user_id == current_user.id, self.model.company_id == company_id,
                                          self.model.action == 'invite'))
            existing_request_from_company = existing_request_from_company.scalar()
            if existing_request_from_company:
                raise HTTPException(status_code=400, detail="You already have been invited to join this company")
            request = self.model(
                user_id=current_user.id,
                company_id=company_id,
                action='request'
            )
            session.add(request)
            await session.commit()
            return {'message': 'Request to join sent'}

    async def decline_request_to_join_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            request = await session.execute(
                select(self.model).filter(self.model.company_id == company_id, self.model.user_id == current_user.id,
                                          self.model.action == 'request'))
            request = request.scalar()
            if not request:
                raise RequestNotFound
            await session.delete(request)
            await session.commit()
            return {'Request': 'deleted'}

    async def all_request_to_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(models.Company.id == company_id, models.Company.owner == current_user.id))
            company = company.scalar()
            if not company:
                raise ForbiddenToProceed
            request = await session.execute(
                select(self.model).filter(self.model.company_id == company_id, self.model.action == 'request'))
            request = request.scalars().all()
            if not request:
                raise RequestNotFound
            return {'Requests': request}

    async def company_all_invitations(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(models.Company.id == company_id, models.Company.owner == current_user.id))
            company = company.scalar()
            if not company:
                raise ForbiddenToProceed
            actions = await session.execute(
                select(self.model).filter(self.model.company_id == company_id, self.model.action == 'invite'))
            actions = actions.scalars().all()
            if not actions:
                raise HTTPException(status_code=404, detail="No invitations")
            return {'Invitations': actions}

    async def company_response(self, company_id: int, user_id: int, current_user: User, answer: AnswerResponse):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(models.Company.id == company_id, models.Company.owner == current_user.id))
            company = company.scalar()
            if not company:
                raise ForbiddenToProceed
            request = await session.execute(
                select(self.model).filter(self.model.user_id == user_id, self.model.company_id == company_id,
                                          self.model.action == 'request'))
            request = request.scalar()
            if not request:
                raise RequestNotFound
            if answer.accept:
                await session.delete(request)
                company = await session.execute(select(models.Company).filter(models.Company.id == company_id))
                company = company.scalar()
                company.member_ids.append(user_id)
                await session.commit()
                return {'Invitation': 'Accepted'}
            else:
                await session.delete(request)
                await session.commit()
                return {'Request': 'Declined'}

    async def company_kick_user(self, company_id: int, user_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(models.Company.id == company_id, models.Company.owner == current_user.id))
            company = company.scalar()
            if not company:
                raise ForbiddenToProceed
            if user_id not in company.member_ids:
                raise NoSuchId
            company.member_ids.remove(user_id)
            await session.commit()
            return {'User': 'Deleted'}

    async def user_leave_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(text(f"ARRAY[{current_user.id}]::integer[] <@ companies.member_ids")))
            company = company.scalar()
            if not company:
                raise HTTPException(status_code=403, detail="You are not in this company")
            company.member_ids.remove(current_user.id)
            await session.commit()
            return {'Success': 'You left company'}

    async def get_all_members(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(select(models.Company).filter(models.Company.id == company_id).where(
                or_(models.Company.is_visible == True, models.Company.owner == current_user.id)))
            company = company.scalar()
            if not company:
                raise NoSuchId
            return company


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


class QuizzRepository(AbstractRepositoryQuizz):
    model = None

    async def check_owner_admin(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(models.Company.owner == current_user.id, models.Company.id == company_id))
            company = company.scalar()
            administrator = await session.execute(
                select(models.Administrator).filter(models.Administrator.company_id == company_id,
                                                    models.Administrator.user_id == current_user.id))
            administrator = administrator.scalar()
            if not company:
                if not administrator:
                    raise ForbiddenToProceed

    async def create_quizz(self, company_id: int, form: CreateQuizz, current_user: User):
        async with async_session() as session:
            await self.check_owner_admin(company_id, current_user)
            quizz = self.model(
                name=form.name,
                title=form.title,
                description=form.description,
                frequency=form.frequency,
                company_id=company_id,
                created_by=current_user.id
            )
            session.add(quizz)
            await session.commit()
            return quizz

    async def get_all_quizzes(self, company_id: int, current_user: User, params: Params = Depends()):
        async with async_session() as session:
            await self.check_owner_admin(company_id, current_user)
            quizzes = await session.execute(select(self.model).filter(self.model.company_id == company_id))
            quizzes = quizzes.scalars().all()

            return paginate(quizzes, params)

    async def update_quizz(self, company_id: int, quizz_id: int, form: UpdateQuizz, current_user: User):
        async with async_session() as session:
            quizz = await session.execute(select(self.model).filter(self.model.id == quizz_id))
            quizz = quizz.scalar()
            if not quizz:
                raise NoSuchId
            await self.check_owner_admin(company_id, current_user)
            for key, value in form.model_dump(exclude_unset=True).items():
                setattr(quizz, key, value)
                quizz.updated_by = current_user.id
                await session.commit()
            return quizz

    async def delete_quizz(self, company_id: int, quizz_id: int, current_user: User):
        async with async_session() as session:
            quizz = await session.execute(select(self.model).filter(self.model.id == quizz_id))
            quizz = quizz.scalar()
            if not quizz:
                raise NoSuchId
            await self.check_owner_admin(company_id, current_user)
            quizz_to_show = quizz
            await session.delete(quizz)
            await session.commit()
            return quizz_to_show
