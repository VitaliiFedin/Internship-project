import asyncio
from pydantic_settings import BaseSettings, SettingsConfigDict

import redis.asyncio as redis


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow', frozen=False)
    redis_host: str
    redis_port: int


settings = RedisConfig()


async def redis_connection():
    connection = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    await connection.close()


def redis_init():
    asyncio.run(redis_connection())
    print("Redis Done")
