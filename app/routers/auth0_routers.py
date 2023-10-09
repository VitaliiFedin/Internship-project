from fastapi import APIRouter
from app.core.auth0 import get_token
auth0 = APIRouter()


@auth0.get("/decode-token/")
async def read_token(token: str):
    return await get_token(token)

