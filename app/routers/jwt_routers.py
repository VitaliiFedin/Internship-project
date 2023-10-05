from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.repositories.jwt import JWTRepos
from app.schemas.token_schemas import TokenSchema, UserAuth, UserOut, SystemUser

jwt = APIRouter()


@jwt.post('/signup', response_model=UserOut)
async def create_user(data: UserAuth):
    return await JWTRepos().create_user(data)


@jwt.post('/login', response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await JWTRepos().login(form_data)


@jwt.get('/me', summary='Get details of currently logged in user', response_model=UserOut)
async def get_me(user: SystemUser = Depends(JWTRepos().get_current_user)):
    return user
