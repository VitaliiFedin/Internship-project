from fastapi_pagination import Params, Page

from app.core.dependencies import get_current_user_dependency
from fastapi import APIRouter, Depends
from app.schemas.quizz_schemas import Quizz, CreateQuizz, UpdateQuizz
from app.repositories.quizzes import QuizzRepo
from app.schemas.user_schemas import User

quizz = APIRouter()


@quizz.post('/quizz', response_model=Quizz)
async def create_quizz(company_id: int, form: CreateQuizz, current_user: User = Depends(get_current_user_dependency)):
    return await QuizzRepo().create_quizz(company_id, form, current_user)


@quizz.get('/quizzes/{company_id}', response_model=Page[Quizz])
async def get_all_quizzes(company_id: int, current_user: User = Depends(get_current_user_dependency),
                          params: Params = Depends()):
    return await QuizzRepo().get_all_quizzes(company_id, current_user, params)


@quizz.patch('/quizz/{quizz_id}', response_model=Quizz)
async def update_quizz(company_id: int, quizz_id: int, form: UpdateQuizz,
                       current_user: User = Depends(get_current_user_dependency)):
    return await QuizzRepo().update_quizz(company_id, quizz_id, form, current_user=current_user)


@quizz.delete('/quizz/{quizz_id}')
async def delete_quizz(company_id: int, quizz_id: int, current_user: User = Depends(get_current_user_dependency)):
    return await QuizzRepo().delete_quizz(company_id, quizz_id, current_user)
