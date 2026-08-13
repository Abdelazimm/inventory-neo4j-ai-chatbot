import pytest
from app.agents.validator import validate_cypher_query


def test_valid_read_cypher_queries():
    valid = [
        "MATCH (a:Asset) RETURN a.asset_tag, a.name",
        "MATCH (v:Vendor)-[:SUPPLIES]->(i:Item) RETURN v.name AS Vendor, count(i) AS ItemCount",
        "MATCH (a:Asset)-[:LOCATED_AT]->(l:Location)-[:BELONGS_TO]->(s:Site) WHERE s.name = 'Headquarters' RETURN a.name, a.cost",
        "MATCH (v:Vendor)-[:PURCHASED_FROM]-(a:Asset) RETURN v.name, sum(a.cost) AS TotalSpend ORDER BY TotalSpend DESC LIMIT 5",
        "OPTIONAL MATCH (i:Item)-[:IN_CATEGORY]->(c:Category) RETURN i.name, c.name",
        "WITH 'TAG-1001' AS tag MATCH (a:Asset {asset_tag: tag}) RETURN a.name"
    ]
    for q in valid:
        is_valid, error = validate_cypher_query(q)
        assert is_valid is True, f"Expected query to be valid: {q}, error: {error}"
        assert error is None


def test_block_destructive_cypher():
    blocked = [
        "MATCH (n) DETACH DELETE n",
        "MATCH (a:Asset) DELETE a",
        "CREATE (a:Asset {name: 'Malicious'}) RETURN a",
        "MERGE (v:Vendor {name: 'Fake'}) RETURN v",
        "MATCH (a:Asset) SET a.cost = 0 RETURN a",
        "MATCH (a:Asset) REMOVE a.cost RETURN a",
        "DROP CONSTRAINT unique_asset_tag",
        "LOAD CSV WITH HEADERS FROM 'http://evil.com/data.csv' AS row RETURN row",
        "CALL dbms.security.listUsers() YIELD user RETURN user"
    ]
    for q in blocked:
        is_valid, error = validate_cypher_query(q)
        assert is_valid is False, f"Expected query to be blocked: {q}"
        assert error is not None
        assert "forbidden" in error.lower() or "read-only" in error.lower()


def test_block_stacked_cypher():
    stacked = [
        "MATCH (a:Asset) RETURN a; MATCH (n) DETACH DELETE n;",
        "MATCH (a:Asset) RETURN a; DROP CONSTRAINT unique_asset_tag;"
    ]
    for q in stacked:
        is_valid, error = validate_cypher_query(q)
        assert is_valid is False
        assert "multiple" in error.lower() or "forbidden" in error.lower()


def test_block_missing_return():
    invalid = [
        "MATCH (a:Asset)"
    ]
    for q in invalid:
        is_valid, error = validate_cypher_query(q)
        assert is_valid is False
        assert "return" in error.lower()
