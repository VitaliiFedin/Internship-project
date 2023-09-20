import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FastAPIConfig
from app.db.database import db_init_models as postgres_dependency
from app.db.redis import redis_init as redis_dependency
from app.routers.health import router

load_dotenv()

settings = FastAPIConfig()
app = FastAPI()


app.add_middleware(CORSMiddleware,
                   allow_origins=os.getenv('ORIGINS'),
                   allow_credentials=os.getenv('ALLOW_CREDENTIALS'),
                   allow_methods=os.getenv('ALLOW_METHODS'),
                   allow_headers=os.getenv('ALLOW_HEADERS'),
                   )
app.include_router(router)


if __name__ == '__main__':
    postgres_dependency()
    redis_dependency()
    uvicorn.run(settings.app_name, reload=settings.reload, host=settings.host, port=settings.port)

