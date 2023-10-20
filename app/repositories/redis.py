import csv
import json
import os

from fastapi import HTTPException
from sqlalchemy import select
from app.db.redis import redis_connection
from app.utils.repository import AbstractRepositoryRedis
from app.db import models
from app.db.database import async_session


class RedisRepository(AbstractRepositoryRedis):

    async def save_to_redis(self, company_id: int, quiz_id: int, user_id: int):
        async with async_session() as session:
            results = await session.execute(select(models.Result).filter
                                            (models.Result.quiz_id == quiz_id, models.Result.company_id == company_id),
                                            models.Result.user_id == user_id)
            results = results.scalars().all()
            for result in results:
                questions = await session.execute(select(models.Question).filter(
                    (models.Question.quiz_id == quiz_id) & (models.Question.company_id == company_id)))
                questions = questions.scalars().all()
            questions_data = []
            for question in questions:
                question_data = {
                    'text': question.text,
                    'answers': question.answers,
                    'correct_answer': question.correct_answer,
                    'quiz_id': quiz_id,
                    'company_id': question.company_id,
                    'created_by': question.created_by
                }
                questions_data.append(question_data)

            result_data = {
                'user_id': user_id,
                'company_id': company_id,
                'quiz_id': quiz_id,
                'right_count': result.right_count,
                'total_count': result.total_count,
                'question_data': questions_data
            }

            result_json = json.dumps(result_data)

            redis_key = f'result:{user_id}:{company_id}:{quiz_id}'
            await redis_connection().setex(redis_key, 48 * 60 * 60, result_json)
        return result_data

    async def read_from_redis(self, company_id: int, user_id: int, quiz_id: int):
        redis_key = f'result:{user_id}:{company_id}:{quiz_id}'
        connection = await redis_connection()
        result_json = await connection.get(redis_key)
        if result_json:
            result_data = json.loads(result_json.decode())
            return result_data
        else:
            raise HTTPException(status_code=404, detail="Result not found")

    async def save_to_json(self, company_id: int, user_id: int, quiz_id: int):
        result_data = await self.read_from_redis(company_id, user_id, quiz_id)
        json_file_path = 'exported_files/data.json'
        if not os.path.exists('exported_files'):
            os.makedirs('exported_files')
        if not result_data:
            return {"Error": "no data"}
            # Export to JSON
        with open(json_file_path, 'w') as json_file:
            json.dump(result_data, json_file)
            return json_file

    async def save_to_csv(self, company_id: int, user_id: int, quiz_id: int):
        result_data = await self.read_from_redis(company_id, user_id, quiz_id)
        csv_file_path = 'exported_files/data.csv'
        questions_data = result_data.get('question_data', [])
        if not questions_data:
            return {"Redis": "Error"}
        with open(csv_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=questions_data[0].keys())
            csv_writer.writeheader()
            for data in questions_data:
                csv_writer.writerow(data)
        return {"Redis": "Success"}


class RedisRepo(RedisRepository):
    pass
