from fastapi import HTTPException
from sqlalchemy import select

from app.core.exception import NoSuchId
from app.db import models
from app.db.database import async_session
from app.repositories.companies import CompanyRepos
from app.schemas.user_schemas import User
from app.utils.repository import AbstractResult
from app.repositories.users import UsersRepository


class ResultRepository(AbstractResult):

    async def get_result(self, user_id: int):
        async with async_session() as session:
            results = await session.execute(select(models.Result).filter(models.Result.user_id == user_id))
            results = results.scalars().all()
            total_correct = 0
            total_questions = 0

            for result in results:
                total_correct += result.right_count
                total_questions += result.total_count

            if total_questions == 0:
                return 0

            rating = total_correct / total_questions
            return {"Rating": rating.__round__(2)}

    async def get_user_rating(self, user_id: int):
        async with async_session() as session:
            await UsersRepository().get_user_id(user_id)
            await self.get_result(user_id)

    async def get_user_rating_company(self, user_id: int, company_id: int, current_user: User):
        company = await CompanyRepos().get_company_by_id(company_id, current_user)
        if user_id not in company.member_ids:
            await CompanyRepos().check_owner_admin(company_id, current_user)
            raise HTTPException(status_code=403, detail="You are not in company")

        await self.get_result(user_id)
