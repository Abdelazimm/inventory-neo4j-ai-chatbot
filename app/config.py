import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    # LLM Settings
    OPENAI_API_KEY: str = Field(default="sk-mock-key-for-local-testing")
    MODEL_NAME: str = Field(default="gpt-4o-mini")
    TEMPERATURE: float = Field(default=0.0)

    # Neo4j Settings (Compatible with Neo4j Aura and Local Neo4j)
    NEO4J_URI: str = Field(default="bolt://localhost:7687")
    NEO4J_USERNAME: str = Field(default="neo4j")
    NEO4J_PASSWORD: str = Field(default="password")
    NEO4J_DATABASE: str = Field(default="neo4j")
    MAX_CYPHER_RECORDS: int = Field(default=100)
    CYPHER_TIMEOUT_SECONDS: int = Field(default=10)

    # State & Checkpoints
    CHECKPOINTS_DB_PATH: str = Field(default="/tmp/neo4j_checkpoints.sqlite" if os.environ.get("VERCEL") else "./neo4j_checkpoints.sqlite")

    # Security & JWT
    JWT_SECRET: str = Field(default="inventory_neo4j_ai_jwt_secret_key_change_in_production_987654321")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=480)

    # Observability
    LANGSMITH_API_KEY: str = Field(default="")
    LANGCHAIN_TRACING_V2: str = Field(default="false")
    LANGCHAIN_PROJECT: str = Field(default="inventory-neo4j-ai-chatbot")

    # App Settings
    APP_ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    CORS_ORIGINS: Union[List[str], str] = Field(default=["http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:3001"])

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
