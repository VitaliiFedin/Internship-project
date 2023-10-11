from fastapi import Depends

from app.repositories.jwt import JWTRepos


async def get_current_user_dependency(token: str = Depends(JWTRepos().get_current_user)):
    return token
