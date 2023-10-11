from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params

from app.core.dependencies import get_current_user_dependency
from app.repositories.companies import CompanyRepos
from app.schemas.company_schemas import Company, CompanyCreate, CompanyUpdate
from app.schemas.user_schemas import User

company = APIRouter()


@company.get('/companies', response_model=Page[Company])
async def get_all_companies(params: Params = Depends()):
    return await CompanyRepos().get_all_companies(params)


@company.get('/company/{company_id}', response_model=Company)
async def get_company(company_id: int):
    return await CompanyRepos().get_one_company(company_id)


@company.delete('/company/delete/{company_id}', response_model=Company)
async def delete_company(company_id: int, current_user: User = Depends(get_current_user_dependency)):
    return await CompanyRepos().delete_company(company_id, current_user)


@company.post('/company/add', response_model=CompanyCreate)
async def post_company(company: CompanyCreate, current_user: User = Depends(get_current_user_dependency)):
    return await CompanyRepos().create_new_company(company, current_user)


@company.patch('/company/update/{company_id}', response_model=Company)
async def update_company(company_id: int, model_to_update: CompanyUpdate,
                         current_user: User = Depends(get_current_user_dependency)):
    return await CompanyRepos().update_company(company_id,model_to_update, current_user)
