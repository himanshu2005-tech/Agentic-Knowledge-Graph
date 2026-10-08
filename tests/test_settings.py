from src.rag_pipeline.settings import Settings


def test_settings_support_file_and_neo4j_backends():
    assert Settings(RAG_STORE_BACKEND="file").store_backend == "file"
    assert Settings(RAG_STORE_BACKEND="neo4j", NEO4J_PASSWORD="secret").store_backend == "neo4j"
