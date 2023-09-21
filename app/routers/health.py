from fastapi import APIRouter

import sys

sys.path.append("..")
from app.db.redis import redis_init
from app.db.database import db_init_models

router = APIRouter()


@router.get('/')
def health_check():
    return {'status_code': 200, 'detail': 'ok', 'result': 'working'}


@router.get('/redis')
def redis_check():
    return redis_init()


@router.get('/db')
def db_check():
    return db_init_models()
