from typing import List, Optional
from pydantic import BaseModel


class CreateQuestion(BaseModel):
    text: str
    answers: List[str]
    correct_answer: int


class GetQuestions(BaseModel):
    id: int
    text: str
    answers: List[str]


class UserAnswers(BaseModel):
    answers: List[int]
