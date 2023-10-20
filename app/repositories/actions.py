from fastapi import HTTPException
from sqlalchemy import select

from app.core.exception import NoSuchId, InvitationNotFound, RequestNotFound
from app.db.database import async_session
from app.db.models import UsersCompaniesActions
from app.repositories.companies import CompanyRepos
from app.repositories.users import UsersRepository
from app.schemas.action_schemas import AnswerResponse
from app.schemas.user_schemas import User
from app.utils.repository import AbstractRepositoryAction


class ActionRepository(AbstractRepositoryAction):
    model = None

    async def invite_user(self, company_id: int, user_id: int, current_user: User):
        async with async_session() as session:
            await CompanyRepos().get_company_by_id(session, company_id, current_user)
            user = await UsersRepository().get_user_id(user_id)
            action = self.model(
                user_id=user_id,
                company_id=company_id,
                action="invite")
            session.add(action)
            await session.commit()
            return {"message": "Invitation sent successfully"}

    async def get_actions(self, current_user: User, method: str):
        async with async_session() as session:
            actions = await session.execute(
                select(self.model).filter(self.model.user_id == current_user.id, self.model.action == f'{method}'))
            actions = actions.scalars().all()
            return actions

    async def all_invitations(self, current_user: User):
        method = 'invite'
        actions = await self.get_actions(current_user, method)
        return {'Invitations': actions}

    async def all_requests(self, current_user: User):
        method = 'request'
        actions = await self.get_actions(current_user, method)
        return {'Requests': actions}

    async def get_invitations(self, user_id: int, company_id: int):
        async with async_session() as session:
            invitation = await session.execute(
                select(self.model).filter(self.model.user_id == user_id, self.model.company_id == company_id,
                                          self.model.action == 'invite'))
            invitation = invitation.scalar()
            if not invitation:
                raise InvitationNotFound
            return invitation


    async def cancel_invitation(self, company_id: int, user_id: int, current_user: User):
        async with async_session() as session:
            await CompanyRepos().get_company_by_id(session, company_id, current_user)
            invitation = await self.get_invitations(user_id, company_id)
            await session.delete(invitation)
            await session.commit()
            return {"message": "Invitation canceled"}

    async def accept_invitation(self, company_id: int, user_id: int, current_user: User, answer: AnswerResponse):
        async with async_session() as session:
            invitation = await self.get_invitations(user_id, company_id)
            if current_user.id != user_id:
                raise Exception
            if not answer.accept:
                await session.delete(invitation)
                await session.commit()
                return {'Invitation': 'Declined'}
            await session.delete(invitation)
            company = await CompanyRepos().get_company_by_id(session, company_id, current_user)
            company.member_ids.append(current_user.id)
            await session.commit()
            return {'Invitation': 'Accepted'}

    async def request_to_join_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await CompanyRepos().get_company_by_id(session, company_id, current_user)
            if company.owner == current_user.id or current_user.id in company.member_ids:
                raise HTTPException(status_code=400, detail="You are already a member or owner of this company")
            request = await self.get_actions(current_user, method='request')
            invite = await self.get_actions(current_user, method='invite')
            if not request and not invite:
                request = self.model(
                    user_id=current_user.id,
                    company_id=company_id,
                    action='request'
                )
                session.add(request)
                await session.commit()
                return {'message': 'Request to join sent'}

    async def request_handle(self, session, company_id: int, current_user=None, user_id=None):
        if current_user is None:
            request = await session.execute(
                select(self.model).filter(self.model.company_id == company_id, self.model.action == 'request'))
            return request.scalars().all()
        if user_id is not None:
            request = await session.execute(
                select(self.model).filter(self.model.user_id == user_id, self.model.company_id == company_id,
                                          self.model.action == 'request'))
            return request.scalar()

        request = await session.execute(
            select(self.model).filter(self.model.company_id == company_id, self.model.action == 'request'))
        return request.scalar()

    async def decline_request_to_join_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            request = await self.request_handle(session, company_id, current_user)
            await session.delete(request)
            await session.commit()
            return {'Request': 'deleted'}

    async def all_request_to_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            await CompanyRepos().get_company_by_id(session, company_id, current_user)
            request = await self.request_handle(session, company_id)
            if not request:
                raise RequestNotFound
            return {'Requests': request}

    async def company_all_invitations(self, company_id: int, current_user: User):
        async with async_session() as session:
            await CompanyRepos().get_company_by_id(session, company_id, current_user)
            actions = await session.execute(
                select(self.model).filter(self.model.company_id == company_id, self.model.action == 'invite'))
            actions = actions.scalars().all()
            if not actions:
                raise HTTPException(status_code=404, detail="No invitations")
            return {'Invitations': actions}

    async def company_response(self, company_id: int, user_id: int, current_user: User, answer: AnswerResponse):
        async with async_session() as session:
            await CompanyRepos().get_company_by_id(session, company_id, current_user)
            request = await self.request_handle(session, company_id, user_id)
            if not request:
                raise RequestNotFound
            if not answer.accept:
                await session.delete(request)
                await session.commit()
                return {'Request': 'Declined'}
            await session.delete(request)
            company = await CompanyRepos().get_company_by_id(session, company_id, current_user)
            company.member_ids.append(user_id)
            await session.commit()
            return {'Invitation': 'Accepted'}

    async def company_kick_user(self, company_id: int, user_id: int, current_user: User):
        async with async_session() as session:
            company = await CompanyRepos().get_company_by_id(session, company_id, current_user)
            if user_id not in company.member_ids:
                raise NoSuchId
            company.member_ids.remove(user_id)
            await session.commit()
            return company.member_ids

    async def user_leave_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await CompanyRepos().get_company_by_id(session, company_id, current_user)
            if current_user in company.member_ids:
                company.member_ids.remove(current_user.id)
            await session.commit()
            return company.member_ids

    async def get_all_members(self, company_id: int, current_user: User):
        async with async_session() as session:
            members = await CompanyRepos().get_company_by_id(session, company_id, current_user)
            return members


class ActionRepos(ActionRepository):
    model = UsersCompaniesActions
