from fastapi import HTTPException, Depends
from fastapi_pagination import paginate, Params
from sqlalchemy import select, or_

from app.core.exception import PhoneExist, NoSuchId, ForbiddenToDeleteCompany, ForbiddenToUpdateCompany, \
    ForbiddenToProceed
from app.db.database import async_session
from app.db.models import Company
from app.repositories.users import UsersRepository
from app.schemas.company_schemas import CompanyCreate, CompanyUpdate
from app.schemas.user_schemas import User
from app.utils.repository import AbstractRepositoryCompany


class CompanyRepository(AbstractRepositoryCompany):
    model = None

    async def check_phone(self, model_to_use: Company):
        async with async_session() as session:
            phone_check = await session.execute(select(self.model).where(self.model.phone == model_to_use.phone))
            phone_check = phone_check.scalar()
            if phone_check:
                raise PhoneExist

    async def get_company_by_id(self, session, company_id: int, current_user: User):
        result = await session.execute(select(self.model).filter(self.model.id == company_id).where(
            or_(self.model.is_visible, self.model.owner == current_user.id)))
        if not result:
            raise NoSuchId
        return result.scalar()

    async def get_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            result = await self.get_company_by_id(session, company_id, current_user)
            return result

    async def get_all_companies(self, current_user: User, params: Params = Depends()):
        async with async_session() as session:
            result = await session.execute(
                select(self.model).where(or_(self.model.is_visible, self.model.owner == current_user.id)))
            result = result.scalars().all()
            return paginate(result, params)

    async def delete_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            company_to_delete = await self.get_company_by_id(session, company_id, current_user)
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
            company = await self.get_company_by_id(session, company_id, current_user)
            if company.owner != current_user.id:
                raise ForbiddenToUpdateCompany
            for key, value in model.model_dump(exclude_unset=True).items():
                setattr(company, key, value)
                await session.commit()
            return company

    async def make_admin(self, company_id: int, user_id: int, current_user: User):
        async with async_session() as session:
            company = await self.get_company_by_id(session, company_id, current_user)
            user = await UsersRepository().get_user_id(user_id)
            if user.id in company.member_ids:
                company.admin_ids.append(user)
                await session.commit()
                return {"message": "Administrator appointed"}
            else:
                raise HTTPException(status_code=400, detail="User is not a member of the company")

    async def get_all_admins(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await self.get_company_by_id(session, company_id, current_user)
            admins = company.admin_ids
            return {'Admins': admins}

    async def remove_admin(self, company_id: int, user_id: int, current_user: User):
        async with async_session() as session:
            company = await self.get_company_by_id(session, company_id, current_user)
            user = await UsersRepository().get_user_id(user_id)
            if user.id in company.admin_ids:
                company.admin_ids.remove(user.id)
                await session.commit()
                return {"message": "Administrator removed"}
            raise HTTPException(status_code=404, detail="Administrator not found")

    async def check_owner_admin(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await self.get_company_by_id(session, company_id, current_user)
            if not company:
                if current_user.id not in company.admin_ids:
                    raise ForbiddenToProceed


class CompanyRepos(CompanyRepository):
    model = Company
