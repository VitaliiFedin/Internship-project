from app.db.models import Company
from app.utils.repository import CompanyRepository


class CompanyRepos(CompanyRepository):
    model = Company
