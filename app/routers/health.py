import sys

sys.path.append('..')
import os
from fastapi import APIRouter
from app.config import RedisConfig
import redis.asyncio as redis
import asyncpg

settings = RedisConfig()
router = APIRouter()


@router.get('/')
def health_check():
    return {'status_code': 200, 'detail': 'ok', 'result': 'working'}


@router.get('/redis')
async def redis_check():
    connection = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    result = await connection.ping()
    await connection.close()
    return {'Redis': result}


@router.get('/db')
async def db_check():
    connection = await asyncpg.connect(os.getenv('DATABASE_URL'))
    result = await connection.fetchval("SELECT 1")
    return {'Postgresql': result}
