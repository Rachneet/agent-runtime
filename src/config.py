from typing import Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings using pydantic v2 + pydantic-settings.

    Loads environment variables and (for local dev) a `.env` file. Secrets are
    represented with `SecretStr` and a small helper `public_dict` is provided to
    produce a redacted view for logging.
    """

    # Allow extra keys in the .env file (do not fail on unknown env vars)
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # core
    MODEL_ID: str = Field("Qwen/Qwen3-Next-80B-A3B-Instruct", description="HuggingFace model id")
    HUGGINGFACE_API_KEY: Optional[SecretStr] = Field(None, description="HuggingFace API token")
    ENV: str = Field("development", description="one of: development, staging, production")

    # runtime / model
    MODEL_TIMEOUT_SECONDS: int = Field(30, description="LLM call timeout")
    MODEL_MAX_RETRIES: int = Field(3, description="Retries for LLM calls")
    MODEL_BATCH_SIZE: int = Field(1, description="Batch size for requests if supported")

    # logging & observability
    LOG_LEVEL: str = Field("INFO")
    LOG_FILE: str = Field("agent.log")

    # feature toggles
    ENABLE_STRICT_SCHEMA: bool = Field(True, description="Enforce schema validation on LLM output")

    @field_validator("ENV")
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"ENV must be one of {allowed}")
        return v

    def public_dict(self) -> dict:
        """Return a redacted settings dict safe for logging (secrets redacted)."""
        data = self.model_dump()
        if data.get("HUGGINGFACE_API_KEY"):
            data["HUGGINGFACE_API_KEY"] = "***REDACTED***"
        return data


# singleton to import across the app
settings = Settings()       