"""Single place where environment variables become typed settings.

Every other module imports `get_settings()`; nothing else reads os.environ.
Secrets have no defaults, so a missing one fails at startup, not at 2am.
"""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "local"
    log_level: str = "INFO"

    s3_endpoint: str = "http://localhost:8333"
    s3_access_key: SecretStr
    s3_secret_key: SecretStr
    s3_bucket_raw: str = "wa-raw"
    s3_bucket_mart: str = "wa-mart"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
