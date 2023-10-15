import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import FastAPIConfig
from core.log_config import logging_config
from routers.health import router
from routers.user_routers import user
from app.routers.jwt_routers import jwt
from app.routers.auth0_routers import auth0
from app.routers.company_routers import company
from app.routers.action_routers import action
settings = FastAPIConfig()
app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=settings.allow_origins,
                   allow_credentials=settings.allow_credentials,
                   allow_methods=settings.allow_methods,
                   allow_headers=settings.allow_headers,
                   )
app.include_router(router)
app.include_router(user, tags=["User"])
app.include_router(jwt)
app.include_router(auth0)
app.include_router(company, tags=["Company"])
app.include_router(action, tags=["Actions"])

if __name__ == '__main__':
    uvicorn.run(settings.app_name, reload=settings.reload, host=settings.host, port=settings.port,
                log_config=logging_config)
