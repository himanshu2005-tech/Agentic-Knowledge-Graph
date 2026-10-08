from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field("development", alias="RAG_ENV")
    log_level: str = Field("INFO", alias="RAG_LOG_LEVEL")
    store_backend: Literal["file", "neo4j"] = Field("file", alias="RAG_STORE_BACKEND")

    rag_kb_path: Path = PROJECT_ROOT / "data" / "rag" / "rag_knowledge.txt"
    provenance_path: Path = PROJECT_ROOT / "data" / "rag" / "fact_provenance.jsonl"
    feedback_path: Path = PROJECT_ROOT / "data" / "rag" / "answer_feedback.jsonl"
    local_model_path: Path = Field(PROJECT_ROOT / "local_qwen_3b", alias="LOCAL_MODEL_PATH")

    kg_model: str = Field("openai/gpt-oss-120b", alias="KG_MODEL")
    groq_api_key: SecretStr | None = Field(None, alias="GROQ_API_KEY")
    tavily_api_key: SecretStr | None = Field(None, alias="TAVILY_API_KEY")

    retrieval_top_k: int = Field(12, alias="RAG_RETRIEVAL_TOP_K", ge=1, le=100)
    confidence_threshold: float = Field(0.60, alias="RAG_CONFIDENCE_THRESHOLD", ge=0, le=1)
    embedding_model: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2", alias="RAG_EMBEDDING_MODEL"
    )
    enable_embeddings: bool = Field(True, alias="RAG_ENABLE_EMBEDDINGS")
    cors_origins: str = Field(
        "http://127.0.0.1:5173,http://localhost:5173",
        alias="RAG_CORS_ORIGINS",
    )

    neo4j_uri: str = Field("bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_username: str = Field("neo4j", alias="NEO4J_USERNAME")
    neo4j_password: SecretStr = Field(SecretStr("change-me"), alias="NEO4J_PASSWORD")
    neo4j_database: str = Field("neo4j", alias="NEO4J_DATABASE")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
