import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver
from app.config import settings

logger = logging.getLogger(__name__)

_driver: Optional[Driver] = None


def get_neo4j_driver() -> Driver:
    """Returns a singleton Neo4j driver instance."""
    global _driver
    if _driver is None:
        try:
            _driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
                max_connection_lifetime=3600,
                max_connection_pool_size=50
            )
            logger.info(f"Connected to Neo4j at {settings.NEO4J_URI}")
        except Exception as e:
            logger.error(f"Failed to create Neo4j driver: {e}")
            raise
    return _driver


def check_neo4j_connection() -> bool:
    """Verifies Neo4j database connectivity."""
    try:
        driver = get_neo4j_driver()
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            result = session.run("RETURN 1 AS connected")
            record = result.single()
            return record is not None and record["connected"] == 1
    except Exception as e:
        logger.warning(f"Neo4j connection check failed: {e}")
        return False


def close_neo4j_driver():
    """Closes the active Neo4j driver connection pool."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
        logger.info("Neo4j driver closed.")
