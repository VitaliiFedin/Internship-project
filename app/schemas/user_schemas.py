from typing import List

from pydantic import BaseModel


class User(BaseModel):
    id: int
    email: str
    firstname: str
    lastname: str
    status: str
    city: str
    phone: int
    links: List[str]
    avatar: str
    hashed_password: str
    is_superuser: bool = False
    created_at: str
    updated_at: str


class UserSigninRequest(BaseModel):
    email: str
    hashed_password: str


class UserSignupRequest(BaseModel):
    email: str
    firstname: str
    lastname: str
    city: str
    hashed_password: str
    phone: int

    class Config:
        orm_mode = True


class UserUpdateRequest(BaseModel):
    firstname: str
    lastname: str
    city: str
    phone: str
    links: List[str]
    avatar: str


class UserListResponse(BaseModel):
    users: List[User]


class UserDetailResponse(BaseModel):
    user: User
