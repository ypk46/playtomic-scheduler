# Native imports
from typing import Optional, Text

# 3rd party imports
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Setup dotenv file support
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # CLI configuration
    config_path: Optional[Text] = Field(default=None, alias="PLAYTOMIC_SCHEDULER_PATH")


settings = Settings()
