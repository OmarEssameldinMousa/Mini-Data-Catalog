from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    
    service_name: str 

    service_version: str

    database_url: str

    validator_url: str = "http://validator:8000"

    registry_url: str = "http://registry:8000"

    debug: bool = False

    model_config = SettingsConfigDict(
        env_prefix="INGESTION_",
        extra="ignore"
    )

@lru_cache
def get_settings():
    return Settings()