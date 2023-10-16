from app.db.models import Quizz
from app.utils.repository import QuizzRepository


class QuizzRepo(QuizzRepository):
    model = Quizz
