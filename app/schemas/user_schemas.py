from typing import List, Optional

from pydantic import BaseModel


class User(BaseModel):
    id: int
    email: str
    firstname: Optional[str]
    lastname: Optional[str]
    status: Optional[str]
    city: Optional[str]
    phone: Optional[int]
    links: List[str]
    avatar: Optional[str]
    hashed_password: str
    is_superuser: bool = False
    created_at: str
    updated_at: str


class UserSigninRequest(BaseModel):
    email: str
    hashed_password: str


class UserSignupRequest(BaseModel):
    email: str
    firstname: Optional[str]
    lastname: Optional[str]
    city: Optional[str]
    hashed_password: str
    phone: Optional[int]


class UserUpdateRequest(BaseModel):
    firstname: Optional[str]
    lastname: Optional[str]
    city: Optional[str]
    phone: Optional[str]
    links: Optional[List[str]]
    avatar: Optional[str]


class UserListResponse(BaseModel):
    users: List[User]


class UserDetailResponse(BaseModel):
    user: User
