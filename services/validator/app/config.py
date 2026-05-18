from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):

    validator_service_name: str 

    validator_service_version: str 
    validator_db_url: str

    debug: bool = False

    model_config = SettingsConfigDict(
        extra="ignore"
    )

@lru_cache
def get_settings():
    return Settings()