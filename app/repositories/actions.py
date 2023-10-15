from app.db.models import UsersCompaniesActions
from app.utils.repository import ActionRepository

class ActionRepos(ActionRepository):
    model = UsersCompaniesActions
