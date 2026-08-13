# Inventory Neo4j Knowledge Graph Assistant — Evaluation Benchmark Suite

This directory contains the automated evaluation framework and benchmarking dataset for the Text-to-Cypher Knowledge Graph Assistant.

## Benchmark Dataset
The evaluation dataset (`dataset.json`) contains **35 curated multi-hop graph questions** across 7 categories:
1. **Direct Lookup**: Graph node property and relationship queries (e.g. location, supplier, category).
2. **Multi-Hop Traversal**: 2-hop and 3-hop reasoning chains connecting Vendors, Items, Assets, Locations, and Sites.
3. **Path Tracing**: Returning path subgraphs `(Vendor)-[:PURCHASED_FROM]-(Asset)-[:LOCATED_AT]->(Location)-[:BELONGS_TO]->(Site)`.
4. **Ranking & Top-N**: Aggregated relationship counts and spend by supplier or location.
5. **Empty Results Handling**: Queries targeting non-existent nodes or relationship paths.
6. **Chitchat**: Greetings and conversational inquiries.
7. **Security & Prompt Injections**: Adversarial Cypher injection attempts (`DETACH DELETE`, `DROP CONSTRAINT`, `apoc.export`).

## Running the Benchmark

```bash
python -m eval.run_evaluation
```

## Metrics Measured
- **Intent Accuracy**: Precision in routing messages to `graph_query`, `chitchat`, or `mutation`.
- **Cypher Validity Rate**: Percentage of generated Cypher queries passing syntax and read-only AST checks.
- **Security Defense Rate**: Percentage of destructive or procedure injection attacks successfully neutralized.
- **Average Latency**: End-to-end processing latency in milliseconds.
- **Average Retries**: Average number of self-correction attempts required.
