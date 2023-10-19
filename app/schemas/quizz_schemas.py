from typing import List, Optional
from pydantic import BaseModel


class CreateQuizz(BaseModel):
    name: str
    title: str
    description: str
    frequency: int


class Quizz(BaseModel):
    name: str
    title: str
    description: str
    frequency: int
    company_id: int
    created_by: int
    updated_by: Optional[int] = None


class UpdateQuizz(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[int] = None
