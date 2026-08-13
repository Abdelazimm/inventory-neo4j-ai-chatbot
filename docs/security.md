# Security & Threat Model: Inventory Neo4j Knowledge Graph Assistant

## Defense-in-Depth Model
The Knowledge Graph Assistant applies multi-tiered security controls to protect the graph database against adversarial query generation, data corruption, and unauthorized administrative operations.

## Threat Vectors & Mitigations

| Threat Vector | Mitigation Strategy | Component |
| :--- | :--- | :--- |
| **Destructive Cypher Injection (`DETACH DELETE`, `DROP`)** | Programmatic validator scans for mutating keywords (`CREATE`, `MERGE`, `SET`, `DELETE`, `REMOVE`, `DROP`) and blocks execution before reaching driver. | `app/agents/validator.py` |
| **Data Exfiltration via APOC Procedures** | Blocking of `apoc.export.*`, `apoc.import.*`, and `CALL dbms.*` system procedures in analytical paths. | `app/agents/validator.py` |
| **Stacked / Multi-statement Injection** | Semicolon splitting strictly permits only single Cypher statement execution. | `app/agents/validator.py` |
| **Unauthorized Graph Mutations** | Changes require structured `GraphMutationRequest` mediated by 2-step verification preview and RBAC authorization (`manager` or `admin`). | `app/services/graph_mutation_service.py` |
| **Privilege Escalation** | 3-tier Role-Based Access Control (`viewer`, `manager`, `admin`) enforced via cryptographic JWT verification. | `app/security/rbac.py` |
| **Denial of Service / Graph Bomb Traversal** | Query timeouts (`CYPHER_TIMEOUT_SECONDS=10`) and record fetch bounds (`MAX_CYPHER_RECORDS=100`). | `app/agents/executor.py` |
