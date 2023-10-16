from typing import List, Optional
from pydantic import BaseModel


class CreateQuestion(BaseModel):
    text: str
    answers: List[str]
    correct_answer: str


class GetQuestions(BaseModel):
    id:int
    text: str
    answers: List[str]
