from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    email: str
    firstname: Optional[str]
    lastname: Optional[str]
    status: Optional[bool]
    city: Optional[str]
    phone: Optional[int]
    links: List[str]
    avatar: Optional[str]
    hashed_password: str
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime


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
    firstname: Optional[str] = None
    hashed_password: Optional[str] = None


class UserListResponse(BaseModel):
    users: List[User]


class UserDetailResponse(BaseModel):
    user: User
