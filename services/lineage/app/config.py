from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    
    lineage_service_name: str 
    
    lineage_service_version: str

    lineage_db_url: str

    debug: bool = False

    model_config = SettingsConfigDict(
        extra="ignore"
    )

@lru_cache
def get_settings():
    return Settings()