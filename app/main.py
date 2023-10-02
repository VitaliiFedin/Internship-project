import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import FastAPIConfig
from core.log_config import logging_config
from routers.health import router
from routers.user_routers import user
from app.routers.jwt_routers import jwt
settings = FastAPIConfig()
app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=settings.allow_origins,
                   allow_credentials=settings.allow_credentials,
                   allow_methods=settings.allow_methods,
                   allow_headers=settings.allow_headers,
                   )
app.include_router(router)
app.include_router(user)
app.include_router(jwt)

if __name__ == '__main__':
    uvicorn.run(settings.app_name, reload=settings.reload, host=settings.host, port=settings.port,
                log_config=logging_config)
