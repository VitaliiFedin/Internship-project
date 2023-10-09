from fastapi import Depends

from app.db.models import User
from app.utils.repository import JWTRepository


class JWTRepos(JWTRepository):
    model = User






