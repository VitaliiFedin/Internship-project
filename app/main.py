import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import FastAPIConfig
from core.log_config import logging_config
from routers.health import router

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
    uvicorn.run(settings.app_name, reload=settings.reload, host=settings.host, port=settings.port,
                log_config=logging_config)
