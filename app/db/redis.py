import sys

sys.path.append("..")
import redis.asyncio as redis
from app.config import RedisConfig

settings = RedisConfig()


def redis_connection():
    connection = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    return connection
