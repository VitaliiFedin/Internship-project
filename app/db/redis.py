import sys

sys.path.append("..")
import asyncio
import redis.asyncio as redis
from app.config import RedisConfig

settings = RedisConfig()


async def redis_connection():
    connection = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    await connection.close()


def redis_init():
    asyncio.run(redis_connection())
    return {"Redis": 'Success'}
