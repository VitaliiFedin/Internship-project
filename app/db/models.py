from sqlalchemy import Column, Integer, String, Boolean, ARRAY, TIMESTAMP, text, BigInteger, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList

Model = declarative_base()


class User(Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    firstname = Column(String)
    lastname = Column(String)
    status = Column(Boolean, server_default=text('TRUE'))
    city = Column(String)
    phone = Column(BigInteger, unique=True)
    links = Column(ARRAY(String), server_default=text("'{mylink}'"))
    avatar = Column(String, server_default=text("'myavatar'"))
    hashed_password = Column(String, nullable=False)
    is_superuser = Column(Boolean, server_default=text('FALSE'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    user_company = relationship('Company', back_populates='owner_relationship', cascade='all, delete-orphan')


class Company(Model):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(40))
    title = Column(String)
    description = Column(Text)
    city = Column(String)
    phone = Column(BigInteger, unique=True)
    links = Column(ARRAY(String), server_default=text("'{mylink}'"))
    avatar = Column(String, server_default=text("'myavatar'"))
    is_visible = Column(Boolean, server_default=text('TRUE'))
    owner = Column(Integer, ForeignKey('users.id'))
    member_ids = Column(MutableList.as_mutable(ARRAY(Integer)), server_default="{}")
    admin_ids = Column(MutableList.as_mutable(ARRAY(Integer)), server_default="{}")
    owner_relationship = relationship('User', back_populates='user_company', foreign_keys=[owner])


class UsersCompaniesActions(Model):
    __tablename__ = 'actions'
    action_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    action = Column(String)


class Quizz(Model):
    __tablename__ = 'quizzes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    title = Column(String)
    description = Column(String)
    frequency = Column(Integer)
    company_id = Column(Integer, ForeignKey('companies.id'))
    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'))


class Question(Model):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    answers = Column(MutableList.as_mutable(ARRAY(String)), server_default="{}")
    correct_answer = Column(String)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'))


class Result(Model):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    quiz_id = Column(Integer, ForeignKey('quizzes.id'))
    right_count = Column(Integer)
    total_count = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
