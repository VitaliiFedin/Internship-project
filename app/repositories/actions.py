from fastapi import HTTPException
from sqlalchemy import select, text

from app.core.exception import NoSuchId, InvitationNotFound, RequestNotFound
from app.db import models
from app.db.database import async_session
from app.db.models import UsersCompaniesActions
from app.repositories.companies import CompanyRepos
from app.schemas.action_schemas import InvitationRequest, AnswerResponse
from app.schemas.user_schemas import User
from app.utils.repository import AbstractRepositoryAction


class ActionRepository(AbstractRepositoryAction):
    model = None

    async def invite_user(self, company_id: int, invitation: InvitationRequest, current_user: User):
        async with async_session() as session:
            await CompanyRepos().get_company_by_id(company_id, current_user)
            invited_user = await session.execute(select(models.User).filter(models.User.id == invitation.user_id))
            invited_user = invited_user.scalar()
            if not invited_user:
                raise NoSuchId
            action = self.model(
                user_id=invited_user.id,
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
            if not actions:
                raise HTTPException(status_code=404, detail="No data")

    async def all_invitations(self, current_user: User, method: str):
        async with async_session() as session:
            method = 'invite'
            actions = await self.get_actions(current_user, method)
            return {'Invitations': actions}

    async def all_requests(self, current_user: User, method: str):
        async with async_session() as session:
            method = 'request'
            actions = await self.all_invitations(current_user, method)
            return {'Requests': actions}

    async def get_invitations(self, user_id: int, company_id: int):
        async with async_session() as session:
            invitation = await session.execute(
                select(self.model).filter(self.model.user_id == user_id, self.model.company_id == company_id,
                                          self.model.action == 'invite'))
            invitation = invitation.scalar()
            if not invitation:
                raise InvitationNotFound

    async def cancel_invitation(self, company_id: int, user_id: int, current_user: User):
        async with async_session() as session:
            await CompanyRepos().get_company_by_id(company_id, current_user)
            invitation = await self.get_invitations(user_id, company_id)
            await session.delete(invitation)
            await session.commit()
            return {"message": "Invitation canceled"}

    async def accept_invitation(self, company_id: int, user_id: int, current_user: User, answer: AnswerResponse):
        async with async_session() as session:
            invitation = await self.get_invitations(user_id,company_id)
            if current_user.id != user_id:
                raise Exception
            if answer.accept:
                await session.delete(invitation)
                company = await CompanyRepos().get_company_by_id(company_id, current_user)
                if company.member_ids is None:
                    company.member_ids = []
                company.member_ids.append(current_user.id)
                await session.commit()
                return {'Invitation': 'Accepted'}

            await session.delete(invitation)
            await session.commit()
            return {'Invitation': 'Declined'}

    async def request_to_join_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            company = await CompanyRepos().get_company_by_id(company_id, current_user)
            if company.owner == current_user.id or current_user.id in company.member_ids:
                raise HTTPException(status_code=400, detail="You are already a member or owner of this company")
            await self.get_actions(current_user, method='request')
            await self.get_actions(current_user, method='invite')
            request = self.model(
                user_id=current_user.id,
                company_id=company_id,
                action='request'
            )
            session.add(request)
            await session.commit()
            return {'message': 'Request to join sent'}

    async def decline_request_to_join_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            request = await session.execute(
                select(self.model).filter(self.model.company_id == company_id, self.model.user_id == current_user.id,
                                          self.model.action == 'request'))
            request = request.scalar()
            if not request:
                raise RequestNotFound
            await session.delete(request)
            await session.commit()
            return {'Request': 'deleted'}

    async def all_request_to_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            await CompanyRepos().get_company_by_id(company_id, current_user)
            request = await session.execute(
                select(self.model).filter(self.model.company_id == company_id, self.model.action == 'request'))
            request = request.scalars().all()
            if not request:
                raise RequestNotFound
            return {'Requests': request}

    async def company_all_invitations(self, company_id: int, current_user: User):
        async with async_session() as session:
            await CompanyRepos().get_company_by_id(company_id, current_user)
            actions = await session.execute(
                select(self.model).filter(self.model.company_id == company_id, self.model.action == 'invite'))
            actions = actions.scalars().all()
            if not actions:
                raise HTTPException(status_code=404, detail="No invitations")
            return {'Invitations': actions}

    async def company_response(self, company_id: int, user_id: int, current_user: User, answer: AnswerResponse):
        async with async_session() as session:
            await CompanyRepos().get_company_by_id(company_id, current_user)
            request = await session.execute(
                select(self.model).filter(self.model.user_id == user_id, self.model.company_id == company_id,
                                          self.model.action == 'request'))
            request = request.scalar()
            if not request:
                raise RequestNotFound
            if answer.accept:
                await session.delete(request)
                company = await session.execute(select(models.Company).filter(models.Company.id == company_id))
                company = company.scalar()
                company.member_ids.append(user_id)
                await session.commit()
                return {'Invitation': 'Accepted'}
            else:
                await session.delete(request)
                await session.commit()
                return {'Request': 'Declined'}

    async def company_kick_user(self, company_id: int, user_id: int, current_user: User):
        async with async_session() as session:
            company = await CompanyRepos().get_company_by_id(company_id, current_user)
            if user_id not in company.member_ids:
                raise NoSuchId
            company.member_ids.remove(user_id)
            await session.commit()
            return {'User': 'Deleted'}

    async def user_leave_company(self, company_id: int, current_user: User):
        async with async_session() as session:
            """
            company = await session.execute(
                select(models.Company).filter(text(f"ARRAY[{current_user.id}]::integer[] <@ companies.member_ids")))
            company = company.scalar()
            if not company:
                raise HTTPException(status_code=403, detail="You are not in this company")
            """
            company = await CompanyRepos().get_company_by_id(company_id,current_user)
            if current_user in company.member_ids:
                company.member_ids.remove(current_user.id)
            await session.commit()
            return {'Success': 'You left company'}

    async def get_all_members(self, company_id: int, current_user: User):
        async with async_session() as session:
            await CompanyRepos().get_company_by_id(company_id, current_user)


class ActionRepos(ActionRepository):
    model = UsersCompaniesActions
