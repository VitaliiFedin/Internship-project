from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.database import get_session
from sqlalchemy.exc import IntegrityError

from app.services import service

router = APIRouter()


class CitySchema(BaseModel):
    name: str
    population: int


@router.get('/')
def health_check():
    return {'status_code': 200, 'detail': 'ok', 'result': 'working'}


@router.get('/lox')
async def health_check2():
    return {'status_code': 201, 'detail': 'ok', 'result': 'working'}


@router.get("/cities/biggest", response_model=list[CitySchema])
async def get_biggest_cities(session: AsyncSession = Depends(get_session)):
    cities = await service.get_biggest_cities(session)
    return [CitySchema(name=c.name, population=c.population) for c in cities]


@router.post("/cities/")
async def add_city(city: CitySchema, session: AsyncSession = Depends(get_session)):
    city = service.add_city(session, city.name, city.population)
    try:
        await session.commit()
        return city
    except IntegrityError as ex:
        await session.rollback()


