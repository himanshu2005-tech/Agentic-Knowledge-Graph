from __future__ import annotations

import re
from collections.abc import Sequence

from neo4j import GraphDatabase

from ..domain import Fact, RetrievalHit, Source


class Neo4jKnowledgeStore:
    """Neo4j-backed fact, entity, and source repository with indexed retrieval."""

    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        self.database = database
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.driver.verify_connectivity()
        self.ensure_schema()

    def ensure_schema(self) -> None:
        statements = [
            "CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.key IS UNIQUE",
            "CREATE CONSTRAINT fact_id IF NOT EXISTS FOR (f:Fact) REQUIRE f.id IS UNIQUE",
            "CREATE CONSTRAINT source_url IF NOT EXISTS FOR (s:Source) REQUIRE s.url IS UNIQUE",
            "CREATE FULLTEXT INDEX fact_text IF NOT EXISTS FOR (f:Fact) ON EACH [f.text, f.subject, f.object, f.domain]",
            "CREATE INDEX fact_domain IF NOT EXISTS FOR (f:Fact) ON (f.domain)",
            "CREATE INDEX fact_status IF NOT EXISTS FOR (f:Fact) ON (f.verificationStatus)",
        ]
        with self.driver.session(database=self.database) as session:
            for statement in statements:
                session.run(statement).consume()

    @staticmethod
    def _fact_from_record(record) -> Fact:
        sources = tuple(
            Source(
                url=item["url"], title=item.get("title", ""), excerpt=item.get("excerpt", ""),
                provider=item.get("provider", ""), score=item.get("score"),
            )
            for item in record.get("sources", [])
        )
        return Fact(
            domain=record["domain"], subject=record["subject"], relation=record["relation"],
            object=record["object"], confidence=record.get("confidence", 0.5),
            verification_status=record.get("verificationStatus", "unverified"), sources=sources,
        )

    def health(self) -> dict:
        self.driver.verify_connectivity()
        return {"backend": "neo4j", "status": "healthy", "facts": self.count()}

    def count(self) -> int:
        records, _, _ = self.driver.execute_query(
            "MATCH (f:Fact) RETURN count(f) AS count", database_=self.database
        )
        return int(records[0]["count"])

    def upsert_facts(self, facts: Sequence[Fact]) -> int:
        if not facts:
            return 0
        rows = [fact.to_dict() for fact in facts]
        query = """
        UNWIND $rows AS row
        MERGE (f:Fact {id: row.id})
        ON CREATE SET f.createdAt = row.created_at
        SET f.domain = row.domain, f.subject = row.subject, f.relation = row.relation,
            f.object = row.object, f.text = row.subject + ' ' + row.relation + ' ' + row.object,
            f.confidence = row.confidence, f.verificationStatus = row.verification_status,
            f.updatedAt = datetime()
        MERGE (subject:Entity {key: toLower(row.subject)}) SET subject.name = row.subject
        MERGE (object:Entity {key: toLower(row.object)}) SET object.name = row.object
        MERGE (subject)-[:SUBJECT_OF]->(f)
        MERGE (f)-[:OBJECT_OF]->(object)
        FOREACH (source IN row.sources |
          MERGE (s:Source {url: source.url})
          SET s.title = source.title, s.excerpt = source.excerpt, s.provider = source.provider,
              s.retrievedAt = source.retrieved_at, s.score = source.score
          MERGE (s)-[:SUPPORTS]->(f)
        )
        RETURN count(f) AS touched
        """
        records, _, _ = self.driver.execute_query(query, rows=rows, database_=self.database)
        return int(records[0]["touched"])

    def _search_records(self, query: str, parameters: dict) -> list[RetrievalHit]:
        records, _, _ = self.driver.execute_query(query, parameters_=parameters, database_=self.database)
        hits = []
        for row in records:
            payload = dict(row["fact"])
            payload["sources"] = [dict(source) for source in row.get("sources", []) if source]
            score = float(row.get("score", 0.0))
            hits.append(RetrievalHit(
                fact=self._fact_from_record(payload), score=min(score, 1.0),
                lexical_score=min(score, 1.0), reasons=("neo4j-index",),
            ))
        return hits

    def lexical_search(self, query: str, limit: int = 20) -> list[RetrievalHit]:
        cypher = """
        CALL db.index.fulltext.queryNodes('fact_text', $query, {limit: $limit})
        YIELD node, score
        OPTIONAL MATCH (s:Source)-[:SUPPORTS]->(node)
        RETURN node AS fact, score / (score + 1.0) AS score, collect(s) AS sources
        ORDER BY score DESC LIMIT $limit
        """
        escaped = " ".join(f"{token}~" for token in re.findall(r"[A-Za-z0-9]+", query) if len(token) > 2)
        return self._search_records(cypher, {"query": escaped or query, "limit": limit})

    def graph_expand(self, entity_names: Sequence[str], limit: int = 20) -> list[RetrievalHit]:
        cypher = """
        UNWIND $entities AS entity
        MATCH (e:Entity) WHERE e.key CONTAINS toLower(entity)
        MATCH (e)-[:SUBJECT_OF|OBJECT_OF]-(f:Fact)
        OPTIONAL MATCH (s:Source)-[:SUPPORTS]->(f)
        RETURN DISTINCT f AS fact, 0.45 AS score, collect(s) AS sources
        LIMIT $limit
        """
        hits = self._search_records(cypher, {"entities": list(entity_names), "limit": limit})
        return [
            RetrievalHit(fact=hit.fact, score=hit.score, graph_score=hit.score, reasons=("graph-neighbor",))
            for hit in hits
        ]

    def graph_page(
        self, *, query: str = "", domain: str = "", offset: int = 0, limit: int = 200
    ) -> tuple[list[Fact], int, list[dict]]:
        where = """
        WHERE ($domain = '' OR toLower(f.domain) = toLower($domain))
          AND ($query = '' OR toLower(f.text) CONTAINS toLower($query)
               OR toLower(f.subject) CONTAINS toLower($query)
               OR toLower(f.object) CONTAINS toLower($query)
               OR toLower(f.relation) CONTAINS toLower($query))
        """
        parameters = {"query": query, "domain": domain, "offset": offset, "limit": limit}
        count_records, _, _ = self.driver.execute_query(
            f"MATCH (f:Fact) {where} RETURN count(f) AS total",
            parameters_=parameters, database_=self.database,
        )
        records, _, _ = self.driver.execute_query(
            f"""
            MATCH (f:Fact) {where}
            OPTIONAL MATCH (s:Source)-[:SUPPORTS]->(f)
            RETURN f AS fact, collect(s) AS sources
            ORDER BY f.domain, f.subject, f.relation, f.object
            SKIP $offset LIMIT $limit
            """,
            parameters_=parameters, database_=self.database,
        )
        facts = []
        for row in records:
            payload = dict(row["fact"])
            payload["sources"] = [dict(source) for source in row["sources"] if source]
            facts.append(self._fact_from_record(payload))
        domain_records, _, _ = self.driver.execute_query(
            "MATCH (f:Fact) RETURN f.domain AS name, count(f) AS facts ORDER BY facts DESC, name",
            database_=self.database,
        )
        domains = [{"name": row["name"], "facts": int(row["facts"])} for row in domain_records]
        return facts, int(count_records[0]["total"]), domains

    def all_facts(self) -> list[Fact]:
        cypher = """
        MATCH (f:Fact) OPTIONAL MATCH (s:Source)-[:SUPPORTS]->(f)
        RETURN f AS fact, 1.0 AS score, collect(s) AS sources ORDER BY f.id
        """
        return [hit.fact for hit in self._search_records(cypher, {})]

    def close(self) -> None:
        self.driver.close()
