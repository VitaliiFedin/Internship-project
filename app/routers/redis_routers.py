from fastapi import APIRouter
from app.repositories.redis import RedisRepo

redis = APIRouter()


@redis.post('/redis/save')
async def save_to_redis(company_id: int, quiz_id: int, user_id: int):
    return await RedisRepo().save_to_redis(company_id, quiz_id, user_id)


@redis.get('/redis/{quiz_id:int}')
async def show_from_redis(company_id: int, user_id: int, quiz_id: int):
    return await RedisRepo().read_from_redis(company_id, user_id, quiz_id)


@redis.get('/redis/{quiz_id:int}/json')
async def save_to_file_json(company_id: int, user_id: int, quiz_id: int):
    return await RedisRepo().save_to_json(company_id, user_id, quiz_id)


@redis.get('/redis/{quiz_id:int}/csv')
async def save_to_file_csv(company_id: int, user_id: int, quiz_id: int):
    return await RedisRepo().save_to_csv(company_id, user_id, quiz_id)
