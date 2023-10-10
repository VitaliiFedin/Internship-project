from fastapi import APIRouter
from app.repositories.companies import CompanyRepos
from fastapi_pagination import Page, Params


company = APIRouter()

