from fastapi import HTTPException
from sqlalchemy import select

from app.db import models
from app.db.database import async_session
from app.repositories.companies import CompanyRepos
from app.repositories.quizzes import QuizzRepo
from app.schemas.question_schemas import CreateQuestion, UserAnswers
from app.schemas.user_schemas import User
from app.utils.repository import AbstractQuestion


class QuestionRepository(AbstractQuestion):
    async def create_questions(self, company_id: int, quiz_id: int, form: CreateQuestion, current_user: User):
        async with async_session() as session:
            await QuizzRepo().get_quiz(quiz_id)
            await CompanyRepos().check_owner_admin(company_id, current_user)
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

    async def get_questions_by_quiz_id(self,quiz_id):
        async with async_session() as session:
            questions = await session.execute(select(models.Question).filter(models.Question.quiz_id == quiz_id))
            questions = questions.scalars().all()
            if not questions:
                raise HTTPException(status_code=403, detail="No questions")
            return questions

    async def get_questions(self, company_id: int, quiz_id: int, current_user: User):
        async with async_session() as session:
            await QuizzRepo().get_quiz(quiz_id)
            company = await CompanyRepos().get_company_by_id(company_id, current_user)
            if not company:
                if current_user.id not in company.member_ids or company.owner != current_user.id:
                    raise HTTPException(status_code=403, detail="You are not in this company")
            question = await self.get_questions_by_quiz_id(quiz_id)
            return question

    async def attempt_questions(self, quiz_id: int, company_id: int, user_answer: UserAnswers, current_user: User):
        async with async_session() as session:
            await QuizzRepo().get_quiz(quiz_id)
            company = await CompanyRepos().get_company_by_id(company_id, current_user)
            if current_user.id not in company.member_ids:
                raise HTTPException(status_code=403, detail="You are not in company")
            questions = await self.get_questions_by_quiz_id(quiz_id)
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


class QuestionRepo(QuestionRepository):
    pass
