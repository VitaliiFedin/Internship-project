from typing import List

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params
from app.schemas.action_schemas import InvitationRequest, AnswerResponse, CompanyMembers
from app.schemas.user_schemas import User
from app.core.dependencies import get_current_user_dependency
from app.repositories.actions import ActionRepos

action = APIRouter()


@action.post('/company/action/{company_id}/invite')
async def invite_user_to_company(company_id: int, user_id: int,
                                 curren_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().invite_user(company_id, user_id, curren_user)


@action.get('/user/all_invitations')
async def get_all_invitations(current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().all_invitations(current_user)


@action.get('/user/all_requests')
async def get_all_requests(current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().all_requests(current_user)


@action.delete('/company/invitation/{company_id}')
async def delete_invitation(company_id: int, user_id: int, current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().cancel_invitation(company_id, user_id, current_user)


@action.post('/user/invitation/answer')
async def user_accept_invitation(company_id: int, answer: AnswerResponse, user_id: int,
                                 current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().accept_invitation(company_id, user_id, current_user, answer)


@action.post('/user/request/send/{company_id}')
async def user_send_request(company_id: int, current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().request_to_join_company(company_id, current_user)


@action.delete('/user/request/{company_id}')
async def user_delete_request(company_id: int, current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().decline_request_to_join_company(company_id, current_user)


@action.get('/company/requests/{company_id}')
async def company_get_requests(company_id: int, current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().all_request_to_company(company_id, current_user)


@action.get('/company/invitations/{company_id}')
async def company_get_invitations(company_id: int, current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().company_all_invitations(company_id, current_user)


@action.post('/company/request/answer')
async def company_request_answer(company_id: int, user_id: int, answer: AnswerResponse,
                                 current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().company_response(company_id, user_id, current_user, answer)


@action.post('/company/members/kick')
async def company_members_kick(company_id: int, user_id: int,
                               current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().company_kick_user(company_id, user_id, current_user)


@action.post('/user/leave')
async def user_leave_company(company_id: int, current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().user_leave_company(company_id, current_user)


@action.get('/company/members/{company_id}', response_model=CompanyMembers)
async def company_get_members(company_id: int, current_user: User = Depends(get_current_user_dependency)):
    return await ActionRepos().get_all_members(company_id, current_user)
