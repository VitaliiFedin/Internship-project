from pydantic import Field
from pydantic import BaseModel


class UserAuth(BaseModel):
    email: str = Field(..., description="user email")
    hashed_password: str = Field(..., min_length=5, max_length=24, description="user password")


class UserOut(BaseModel):
    id: int
    hashed_password: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class SystemUser(UserOut):
    hashed_password: str
