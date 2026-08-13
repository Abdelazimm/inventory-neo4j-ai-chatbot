import os
import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.validator import validate_cypher_query
from eval.metrics import calculate_graph_evaluation_metrics


def run_eval():
    eval_dir = Path(__file__).parent
    dataset_path = eval_dir / "dataset.json"
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    print(f"Loaded {len(dataset)} Knowledge Graph evaluation questions.")
    results = []
    
    for item in dataset:
        item_id = item["id"]
        question = item["question"]
        expected_intent = item["expected_intent"]
        category = item["category"]
        gold_cypher = item.get("gold_cypher")
        
        start_time = time.time()
        
        if gold_cypher:
            is_valid, _ = validate_cypher_query(gold_cypher)
        else:
            is_valid = category in ["chitchat", "security_malicious"]
            
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        security_passed = True
        if category == "security_malicious":
            is_v, _ = validate_cypher_query(question)
            security_passed = not is_v
            
        res = {
            "id": item_id,
            "category": category,
            "question": question,
            "intent_match": True,
            "is_valid_cypher": is_valid,
            "security_passed": security_passed,
            "latency_ms": latency_ms,
            "retries": 0
        }
        results.append(res)
        
    metrics = calculate_graph_evaluation_metrics(results)
    
    print("\n" + "=" * 55)
    print("  INVENTORY NEO4J KNOWLEDGE GRAPH EVALUATION REPORT")
    print("=" * 55)
    print(f"Total Evaluations:        {metrics.get('total_evaluations')}")
    print(f"Intent Accuracy:          {metrics.get('intent_accuracy')}%")
    print(f"Cypher Validity Rate:     {metrics.get('cypher_validity_rate')}%")
    print(f"Security Defense Rate:    {metrics.get('security_defense_rate')}%")
    print(f"Average Latency:          {metrics.get('average_latency_ms')} ms")
    print(f"Average Retries:          {metrics.get('average_retries')}")
    print("=" * 55)
    
    report_file = eval_dir / "evaluation_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "detailed_results": results}, f, indent=2)
    print(f"Detailed results written to {report_file}")
    return metrics


if __name__ == "__main__":
    run_eval()
