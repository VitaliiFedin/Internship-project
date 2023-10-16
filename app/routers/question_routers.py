from typing import List

from fastapi_pagination import Params, Page

from app.core.dependencies import get_current_user_dependency
from fastapi import APIRouter, Depends
from app.schemas.question_schemas import CreateQuestion, GetQuestions
from app.repositories.quizzes import QuizzRepo
from app.schemas.user_schemas import User

question = APIRouter()


@question.post('/question')
async def create_question(company_id: int, quiz_id: int, form: CreateQuestion,
                          current_user: User = Depends(get_current_user_dependency)):
    return await QuizzRepo().create_questions(company_id, quiz_id, form, current_user)


@question.get('/question/{quiz_id}', response_model=List[GetQuestions])
async def get_questions(company_id: int, quiz_id: int, current_user: User = Depends(get_current_user_dependency)):
    return await QuizzRepo().get_questions(company_id, quiz_id, current_user)
