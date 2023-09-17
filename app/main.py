import uvicorn
from fastapi import FastAPI

from app.config import FastAPIConfig
from app.routers.health import router

settings = FastAPIConfig()
app = FastAPI()

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(settings.app_name, reload=settings.reload)
