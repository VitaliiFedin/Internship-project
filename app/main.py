import os
import asyncio
from app.db.database import init_models
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import aioredis

from app.routers.health import router

load_dotenv()

app = FastAPI()


async def main():
    redis = await aioredis.create_redis_pool('redis://localhost')
    await redis.set('my-key', 'value')
    value = await redis.get('my-key', encoding='utf-8')
    print(value)

    redis.close()
    await redis.wait_closed()




"""
app.add_middleware(CORSMiddleware,
                   allow_origins=os.getenv('ORIGINS'),
                   allow_credentials=os.getenv('ALLOW_CREDENTIALS'),
                   allow_methods=os.getenv('ALLOW_METHODS'),
                   allow_headers=os.getenv('ALLOW_HEADERS'),
                   )
                   """
app.include_router(router)


def db_init_models():
    asyncio.run(init_models())
    print("Done")


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, host='0.0.0.0', port=80)
    db_init_models()
    asyncio.run(main())