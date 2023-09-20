import asyncio
import os

import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()


async def redis_connection():
    connection = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'))
    print(f"Redis Ping successful: {await connection.ping()}")
    await connection.close()


def redis_init():
    asyncio.run(redis_connection())
    print("PostgreSQL Done ")
