from pydantic_settings import BaseSettings, SettingsConfigDict


class FastAPIConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8', extra='allow', frozen=False )
    app_name: str
    reload: bool

