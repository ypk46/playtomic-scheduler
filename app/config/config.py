from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Setup dotenv file support
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Application configuration
    name: str = Field(default="flask-demo", alias="APP_NAME")
    version: str = Field(default="0.1.0", alias="APP_VERSION")
    env: str = Field(default="dev", alias="APP_ENV")
    port: int = Field(default=5000, alias="APP_PORT")
    threads: int = Field(default=2, alias="APP_THREADS")


settings = Settings()
