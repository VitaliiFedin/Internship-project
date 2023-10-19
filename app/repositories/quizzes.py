from fastapi import Depends
from fastapi_pagination import paginate, Params
from sqlalchemy import select

from app.core.exception import NoSuchId
from app.db.database import async_session
from app.db.models import Quizz
from app.repositories.companies import CompanyRepos
from app.schemas.quizz_schemas import CreateQuizz, UpdateQuizz
from app.schemas.user_schemas import User
from app.utils.repository import AbstractRepositoryQuizz


class QuizzRepository(AbstractRepositoryQuizz):
    model = None

    async def create_quizz(self, company_id: int, form: CreateQuizz, current_user: User):
        async with async_session() as session:
            await CompanyRepos().check_owner_admin(company_id, current_user)
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
            await CompanyRepos().check_owner_admin(company_id, current_user)
            quizzes = await session.execute(select(self.model).filter(self.model.company_id == company_id))
            quizzes = quizzes.scalars().all()

            return paginate(quizzes, params)

    async def update_quizz(self, company_id: int, quizz_id: int, form: UpdateQuizz, current_user: User):
        async with async_session() as session:
            quizz = await self.get_quiz(quizz_id)
            await CompanyRepos().check_owner_admin(company_id, current_user)
            for key, value in form.model_dump(exclude_unset=True).items():
                setattr(quizz, key, value)
            quizz.updated_by = current_user.id
            await session.commit()
            return quizz

    async def get_quiz(self, quizz_id: int):
        async with async_session() as session:
            quizz = await session.execute(select(self.model).filter(self.model.id == quizz_id))
            quizz = quizz.scalar()
            if not quizz:
                raise NoSuchId
            return quizz

    async def delete_quizz(self, company_id: int, quizz_id: int, current_user: User):
        async with async_session() as session:
            quizz = await self.get_quiz(quizz_id)
            await CompanyRepos().check_owner_admin(company_id, current_user)
            await session.delete(quizz)
            await session.commit()
            return f"Quiz {quizz_id} was deleted"


class QuizzRepo(QuizzRepository):
    model = Quizz
