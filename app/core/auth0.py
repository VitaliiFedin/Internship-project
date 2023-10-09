import random
import string

from jose import jwt
from sqlalchemy import select

from app.config import Auth0Cofnig
from app.core.security import get_password_hash
from app.db.database import async_session
from app.db.models import User
from app.schemas.auth0_schemas import TokenPayload

settings = Auth0Cofnig()


def decode_token(token: str):
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.auth0_algorithm],
                         issuer=settings.issuer,
                         audience=settings.audience)
    return payload


async def read_token(token: str):
    async with async_session() as session:
        payload = decode_token(token)
        token_data = TokenPayload(**payload)
        db = await session.execute(select(User).filter(User.email == token_data.email))
        db = db.scalar()
        if db:
            return {"email": token_data.email}
        else:
            letters = string.ascii_lowercase
            password = ''.join(random.choice(letters) for i in range(random.randint(6, 15)))
            print(password)
            user = User(
                email=token_data.email,
                hashed_password=get_password_hash(password),
            )
            session.add(user)
            await session.commit()
            return {'User': user}


async def get_token(token: str):
    token_data = await read_token(token)
    return token_data
