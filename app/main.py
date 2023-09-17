import uvicorn
from fastapi import FastAPI
from pydantic_settings import BaseSettings

from app.routers.health import router


class FastAPIConfig(BaseSettings):
    app_name: str = 'main:app'
    reload: bool = True


settings = FastAPIConfig()
app = FastAPI()

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(settings.app_name, reload=settings.reload)
