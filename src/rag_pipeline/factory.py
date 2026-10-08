from __future__ import annotations

from .settings import Settings
from .stores import FileKnowledgeStore


def create_store(settings: Settings):
    if settings.store_backend == "neo4j":
        from .stores.neo4j import Neo4jKnowledgeStore

        return Neo4jKnowledgeStore(
            uri=settings.neo4j_uri,
            username=settings.neo4j_username,
            password=settings.neo4j_password.get_secret_value(),
            database=settings.neo4j_database,
        )
    return FileKnowledgeStore(settings.rag_kb_path, settings.provenance_path)
