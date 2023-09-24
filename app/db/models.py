from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Model = declarative_base()


class User(Model):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    firstname = Column(String)
    lastname = Column(String)
    status = Column(Boolean, default=True)
    city = Column(String)
    phone = Column(Integer, unique=True)
    links = Column(ARRAY(String))
    avatar = Column(String)
    hashed_password = Column(String)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
