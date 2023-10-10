from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


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


class CompanyCreate(BaseModel):
    name: str
    title: str
    description: str
    city: str
    phone: int
    links: Optional[List[str]]
    avatar: Optional[str]
    is_visible: bool


class CompanyUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
