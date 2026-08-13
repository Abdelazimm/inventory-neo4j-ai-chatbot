import pytest
from app.agents.schema import get_dynamic_neo4j_schema


def test_schema_contains_inventory_entities():
    schema_str = get_dynamic_neo4j_schema()
    
    # Verify core inventory entities are present
    assert ":Asset" in schema_str
    assert ":Vendor" in schema_str
    assert ":Item" in schema_str
    assert ":Site" in schema_str
    assert ":Location" in schema_str
    
    # Verify core relationships are present
    assert "SUPPLIES" in schema_str
    assert "PURCHASED_FROM" in schema_str
    assert "LOCATED_AT" in schema_str
    assert "BELONGS_TO" in schema_str

    # Verify ABSOLUTELY ZERO football remnants exist!
    assert "football" not in schema_str.lower()
    assert "player" not in schema_str.lower()
    assert "stadium" not in schema_str.lower()
    assert "club" not in schema_str.lower()
    assert "plays_for" not in schema_str.lower()
