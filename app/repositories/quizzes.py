from fastapi import Depends
from fastapi_pagination import paginate, Params
from sqlalchemy import select

from app.core.exception import NoSuchId, ForbiddenToProceed
from app.db import models
from app.db.database import async_session
from app.db.models import Quizz
from app.schemas.quizz_schemas import CreateQuizz, UpdateQuizz
from app.schemas.user_schemas import User
from app.utils.repository import AbstractRepositoryQuizz


class QuizzRepository(AbstractRepositoryQuizz):
    model = None

    async def check_owner_admin(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(
                select(models.Company).filter(models.Company.owner == current_user.id, models.Company.id == company_id))
            company = company.scalar()
            """
            administrator = await session.execute(
                select(models.Administrator).filter(models.Administrator.company_id == company_id,
                                                    models.Administrator.user_id == current_user.id))
            administrator = administrator.scalar()
            if not company:
                if not administrator:
                    raise ForbiddenToProceed

    """
            if not company:
                if current_user.id not in company.admin_ids:
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


class QuizzRepo(QuizzRepository):
    model = Quizz
