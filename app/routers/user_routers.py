from fastapi import APIRouter
from fastapi.params import Depends

from app.repositories.users import UsersRepository
from app.services.user_services import *
from fastapi_pagination import Page, Params, paginate

user = APIRouter()


@user.post('/users/add', response_model=UserSignupRequest)
async def post_user(user_in: UserSignupRequest):
    new_user = await UsersRepository().create_new_user(obj_in=user_in)
    return new_user


@user.delete('/users/{user_id}/delete')
async def delete_user(user_id: int):
    user = await UsersRepository().delete_user(user_id)
    return user


@user.get('/users', response_model=Page[User])
async def get_all_users(params: Params = Depends()):
    all_users = await UsersRepository().get_all_users()
    return paginate(all_users, params)


@user.get('/users/{user_id}/get', response_model=UserDetailResponse)
async def user_get(user_id: int):
    user = await UsersRepository().get_one_user(user_id)
    return {'user': user}


@user.patch('/users/{user_id}/update')
async def user_update(user_id: int, obj: UserUpdateRequest):
    user = await UsersRepository().update_user(user_id, obj)
    return user
