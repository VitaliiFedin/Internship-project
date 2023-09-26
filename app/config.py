from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class FastAPIConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow', frozen=False)
    app_name: str
    reload: bool
    host: str
    port: int
    allow_origins: List[str]
    allow_credentials: bool = True
    allow_methods: List[str] = ['*']
    allow_headers: List[str]
    database_url_for_test: str
    database_url: str


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow', frozen=False)
    redis_host: str
    redis_port: int
