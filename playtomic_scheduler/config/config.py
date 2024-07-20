# Native imports
from typing import Optional, Text, List, Dict

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

    # Constants
    tenants: List[Dict] = [
        {
            "id": "6b2efacb-a5b4-43cc-bca3-abca920c7a22",
            "name": "PADEL REPUBLIC",
        },
        {
            "id": "245b2d22-73f6-44be-ab5b-2e466ed83b99",
            "name": "PADEL OASIS",
        },
    ]


settings = Settings()
