import re
from typing import Tuple, Optional

FORBIDDEN_CYPHER_KEYWORDS = [
    r"\bCREATE\b",
    r"\bMERGE\b",
    r"\bSET\b",
    r"\bDELETE\b",
    r"\bDETACH\s+DELETE\b",
    r"\bREMOVE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bLOAD\s+CSV\b",
    r"\bFOREACH\b",
    r"\bCALL\s+dbms\b",
    r"\bCALL\s+db\.create\b",
    r"\bCALL\s+apoc\.export\b",
    r"\bCALL\s+apoc\.import\b",
    r"\bCALL\s+apoc\.system\b",
]

ALLOWED_READ_ROOTS = ["MATCH", "OPTIONAL MATCH", "WITH", "UNWIND", "CALL db.labels", "CALL db.relationshipTypes"]


def validate_cypher_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validates a generated Cypher query for safety:
    1. Checks for empty input.
    2. Strips markdown delimiters.
    3. Blocks multiple stacked statements (semicolons).
    4. Checks for forbidden mutating keywords & administrative procedure calls.
    5. Ensures query begins with an allowed read clause (MATCH, WITH, UNWIND, OPTIONAL MATCH).
    """
    if not query or not query.strip():
        return False, "Cypher query is empty."
        
    clean_query = query.strip()
    
    # Strip markdown if present
    if clean_query.startswith("```cypher"):
        clean_query = clean_query[9:]
    elif clean_query.startswith("```"):
        clean_query = clean_query[3:]
    if clean_query.endswith("```"):
        clean_query = clean_query[:-3]
    clean_query = clean_query.strip()
    
    # Check for multiple statements
    statements = [s.strip() for s in clean_query.split(";") if s.strip()]
    if len(statements) > 1:
        return False, f"Multiple Cypher statements detected ({len(statements)}). Only single read queries are permitted."

    single_stmt = statements[0]
    
    # Check forbidden mutating keywords
    for pattern in FORBIDDEN_CYPHER_KEYWORDS:
        if re.search(pattern, single_stmt, re.IGNORECASE):
            match_word = re.findall(pattern, single_stmt, re.IGNORECASE)[0]
            return False, f"Forbidden Cypher operation detected: '{match_word}'. Only read-only queries are permitted."

    # Check query starts with an allowed read clause
    upper_stmt = single_stmt.upper().strip()
    starts_with_allowed = any(upper_stmt.startswith(allowed) for allowed in ALLOWED_READ_ROOTS)
    if not starts_with_allowed:
        return False, "Cypher query must begin with a read clause (e.g. MATCH, OPTIONAL MATCH, WITH)."

    # Ensure query contains a RETURN clause
    if not re.search(r"\bRETURN\b", upper_stmt):
        return False, "Cypher analytical query must contain a RETURN clause to project data."

    return True, None
