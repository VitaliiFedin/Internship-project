from sqlalchemy import Column, Integer, String, Boolean, ARRAY, TIMESTAMP,text, BigInteger
from sqlalchemy.ext.declarative import declarative_base


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
