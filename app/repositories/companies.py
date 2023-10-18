from fastapi import HTTPException, Depends
from fastapi_pagination import paginate, Params
from sqlalchemy import select, or_

from app.core.exception import PhoneExist, NoSuchId, ForbiddenToDeleteCompany, ForbiddenToUpdateCompany, \
    ForbiddenToProceed
from app.db import models
from app.db.database import async_session
from app.db.models import Company
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
                company.admin_ids.append(user_id)
                await session.commit()
                return {"message": "Administrator appointed"}
            else:
                raise HTTPException(status_code=400, detail="User is not a member of the company")

    async def get_all_admins(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(self.model.id == company_id, self.model.owner == current_user.id))
            company = company.scalar()
            if not company:
                raise ForbiddenToProceed
            admins = company.admin_ids
            return {'Admins': admins}

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
            if user.id in company.admin_ids:
                company.admin_ids.remove(user.id)
                await session.commit()
                return {"message": "Administrator removed"}
            raise HTTPException(status_code=404, detail="Administrator not found")


class CompanyRepos(CompanyRepository):
    model = Company
