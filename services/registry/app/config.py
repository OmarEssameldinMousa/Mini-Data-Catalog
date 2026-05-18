from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):

    registry_service_name: str 
    
    registry_service_version: str 

    registry_db_url: str

    debug: bool = False

    model_config = SettingsConfigDict(
        extra="ignore"
    )
@lru_cache
def get_settings():
    return Settings()