from fastapi import Depends, HTTPException
from fastapi_pagination import Params, paginate
from sqlalchemy import select

from app.core.exception import NoSuchId, ForbiddenToProceed
from app.db import models
from app.db.database import async_session
from app.db.models import Quizz
from app.schemas.question_schemas import CreateQuestion, UserAnswers
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

    async def create_questions(self, company_id: int, quiz_id: int, form: CreateQuestion, current_user: User):
        async with async_session() as session:
            quiz = await session.execute(select(self.model).filter(self.model.id == quiz_id))
            quizz = quiz.scalar()
            if not quizz:
                raise NoSuchId
            await self.check_owner_admin(company_id, current_user)
            question = models.Question(
                text=form.text,
                answers=form.answers,
                correct_answer=form.correct_answer,
                quiz_id=quiz_id,
                company_id=company_id,
                created_by=current_user.id
            )
            session.add(question)
            await session.commit()
            return question

    async def get_questions(self, company_id: int, quiz_id: int, current_user: User):
        async with async_session() as session:
            quiz = await session.execute(select(self.model).filter(self.model.id == quiz_id))
            quizz = quiz.scalar()
            if not quizz:
                raise NoSuchId
            company = await session.execute(select(models.Company).filter(models.Company.id == company_id))
            company = company.scalar()
            if not company:
                raise NoSuchId
            if current_user.id not in company.member_ids or company.owner != current_user.id:
                raise HTTPException(status_code=403, detail="You are not in this company")
            question = await session.execute(select(models.Question).filter(models.Question.quiz_id == quiz_id))
            question = question.scalars().all()
            return question

    async def attempt_questions(self, quiz_id: int, company_id: int, user_answer: UserAnswers, current_user: User):
        async with async_session() as session:
            quiz = await session.execute(select(models.Quizz).filter(models.Quizz.id == quiz_id))
            quiz = quiz.scalar()
            if not quiz:
                raise NoSuchId
            company = await session.execute(select(models.Company).filter(models.Company.id == company_id))
            company = company.scalar()
            if not company:
                raise NoSuchId
            if current_user.id not in company.member_ids:
                raise HTTPException(status_code=403, detail="You are not in company")
            questions = await session.execute(select(models.Question).filter(models.Question.quiz_id == quiz_id))
            questions = questions.scalars().all()
            if not questions:
                raise HTTPException(status_code=403, detail="No questions")
            if len(user_answer.answers) != len(questions):
                raise HTTPException(status_code=400, detail="User must provide answers for all questions")
            correct_answers = 0
            for i, question in enumerate(questions):
                if user_answer.answers[i] == question.correct_answer:
                    correct_answers += 1

            result = models.Result(
                user_id=current_user.id,
                company_id=company_id,
                quiz_id=quiz_id,
                right_count=correct_answers,
                total_count=len(questions)
            )
            session.add(result)
            await session.commit()
            return result

    async def get_user_rating(self, user_id: int):
        async with async_session() as session:
            user = await session.execute(select(models.User).filter(models.User.id == user_id))
            user = user.scalar()
            if not user:
                raise NoSuchId
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

    async def get_user_rating_company(self, user_id: int, company_id: int, current_user: User):
        async with async_session() as session:
            company = await session.execute(select(models.Company).filter(models.Company.id == company_id))
            company = company.scalar()
            if not company:
                raise HTTPException(status_code=403, detail="You are not in company")
            if user_id not in company.member_ids:
                await self.check_owner_admin(company_id, current_user)
                raise HTTPException(status_code=403, detail="You are not in company")

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


class QuizzRepo(QuizzRepository):
    model = Quizz
