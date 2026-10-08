from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvData(BaseSettings):
    DB_URL_ASYNC: str
    DB_URL_SYNC: str
    

class Config(BaseModel):
    env_data:EnvData = EnvData()

config = Config()