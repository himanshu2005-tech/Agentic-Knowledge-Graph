from __future__ import annotations

import argparse

from .settings import get_settings
from .stores import FileKnowledgeStore
from .stores.neo4j import Neo4jKnowledgeStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate the legacy file KG into Neo4j")
    parser.add_argument("--batch-size", type=int, default=500)
    args = parser.parse_args()
    settings = get_settings()
    source = FileKnowledgeStore(settings.rag_kb_path, settings.provenance_path)
    target = Neo4jKnowledgeStore(
        settings.neo4j_uri, settings.neo4j_username,
        settings.neo4j_password.get_secret_value(), settings.neo4j_database,
    )
    facts = source.all_facts()
    total = 0
    try:
        for offset in range(0, len(facts), args.batch_size):
            total += target.upsert_facts(facts[offset:offset + args.batch_size])
            print(f"Migrated {min(offset + args.batch_size, len(facts))}/{len(facts)} facts")
    finally:
        target.close()
    print(f"Neo4j migration complete: {total} facts touched")


if __name__ == "__main__":
    main()
