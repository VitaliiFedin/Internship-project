from typing import List, Optional
from pydantic import BaseModel


class Company(BaseModel):
    id: int
    name: str
    title: str
    description: str
    city: str
    phone: int
    links: Optional[List[str]]
    avatar: Optional[str]
    is_visible: bool
    owner: int
    member_ids: Optional[List[int]]


class CompanyCreate(BaseModel):
    name: str
    title: str
    description: str
    city: str
    phone: int
    is_visible: bool


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_visible: Optional[bool] = None


class CompanyReturn(BaseModel):
    company: Company
