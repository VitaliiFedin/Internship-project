from typing import Optional, List

from pydantic import BaseModel


class InvitationRequest(BaseModel):
    user_id: int


class RequestToJoinCompany(BaseModel):
    company_id: int


class UserInCompanyResponse(BaseModel):
    user_id: int
    company_id: int


class AnswerResponse(BaseModel):
    accept: bool


class CompanyMembers(BaseModel):
    member_ids: Optional[list] = None
