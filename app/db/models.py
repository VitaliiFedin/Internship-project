from sqlalchemy import Column, String, Integer
from .database import Model


class User(Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    price = Column(Integer)
