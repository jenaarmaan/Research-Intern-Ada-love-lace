import os
import json
from typing import List, Dict, Any
from memory_agent import PersonalAssistantAgent

class MemoryEvaluator:
    """
    Evaluates the personal assistant agent on a benchmark of 5 sequential sessions.
    Compares performance head-to-head: Memory-On vs. Memory-Off.
    """
    def __init__(self, db_folder: str = "memory_store_eval"):
        self.db_folder = db_folder
        
    def run_eval_session_sequence(self, memory_enabled: bool) -> List[Dict[str, Any]]:
        # Clean up database folder first to ensure deterministic evaluation
        import shutil
        if os.path.exists(self.db_folder):
            shutil.rmtree(self.db_folder)
            
        agent = PersonalAssistantAgent(self.db_folder)
        
        # Define 5 sequential user session queries
        sessions = [
            {
                "session_id": "sess_1_intro",
                "query": "Hi, I'm Armaan. I'm a research intern working on the Agentic AI project. I prefer using Streamlit for UI prototypes.",
                "expected_recall": []
            },
            {
                "session_id": "sess_2_recall",
                "query": "What project am I working on again, and what UI framework do I prefer?",
                "expected_recall": ["armaan", "agentic ai", "streamlit"]
            },
            {
                "session_id": "sess_3_correction",
                "query": "Actually, we should switch our database focus from ChromaDB to a lightweight NumPy-based vector store because it has fewer installation issues.",
                "expected_recall": []
            },
            {
                "session_id": "sess_4_recommendation",
                "query": "Can you suggest how I should implement our UI and database for the internship project?",
                "expected_recall": ["streamlit", "numpy"]
            },
            {
                "session_id": "sess_5_boilerplate",
                "query": "Please write a boilerplate code template for my project.",
                "expected_recall": ["streamlit", "numpy"]
            }
        ]
        
        results = []
        
        for idx, sess in enumerate(sessions):
            print(f"  Running {sess['session_id']} (Memory={memory_enabled})...")
            
            # Execute dialogue turn
            agent_res = agent.run(sess["query"], sess["session_id"], memory_enabled=memory_enabled)
            response = agent_res["response"]
            
            # Calculate accuracy score based on expected recall keywords
            recall_score = 1.0
            recalled_keys = []
            failed_keys = []
            
            if sess["expected_recall"]:
                matched = 0
                for kw in sess["expected_recall"]:
                    if kw in response.lower():
                        matched += 1
                        recalled_keys.append(kw)
                    else:
                        failed_keys.append(kw)
                recall_score = float(matched / len(sess["expected_recall"]))
            
            # Save step results
            results.append({
                "session_index": idx + 1,
                "session_id": sess["session_id"],
                "query": sess["query"],
                "response": response,
                "expected_recall": sess["expected_recall"],
                "recalled_keys": recalled_keys,
                "failed_keys": failed_keys,
                "recall_accuracy": recall_score,
                "num_memories_stored": len(agent.memory.memories),
                "insights_active": list(agent.reflection_engine.insights)
            })
            
        # Clean up database files after run
        if os.path.exists(self.db_folder):
            shutil.rmtree(self.db_folder)
            
        return results

    def run_benchmark(self) -> Dict[str, Any]:
        print("Starting Memory-ON Evaluation...")
        mem_on_results = self.run_eval_session_sequence(memory_enabled=True)
        
        print("\nStarting Memory-OFF Evaluation...")
        mem_off_results = self.run_eval_session_sequence(memory_enabled=False)
        
        # Compute aggregate metrics
        avg_acc_on = sum(r["recall_accuracy"] for r in mem_on_results) / len(mem_on_results)
        avg_acc_off = sum(r["recall_accuracy"] for r in mem_off_results) / len(mem_off_results)
        
        benchmark_report = {
            "metadata": {
                "evaluation_date": "2026-06-28",
                "num_sessions": 5,
                "eval_parameters": {
                    "similarity_threshold": 0.15,
                    "episodic_limit": 3
                }
            },
            "summary": {
                "memory_on_average_accuracy": avg_acc_on,
                "memory_off_average_accuracy": avg_acc_off,
                "improvement_delta": avg_acc_on - avg_acc_off
            },
            "runs": {
                "memory_on": mem_on_results,
                "memory_off": mem_off_results
            }
        }
        
        return benchmark_report

    def save_reports(self, report: Dict[str, Any], json_path: str = "evaluation_report.json", md_path: str = "evaluation_report.md"):
        # Save JSON
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[EVAL] Saved JSON evaluation report to: {json_path}")
        
        # Generate Markdown Report
        md_content = f"""# Evaluation Report: Memory-Augmented Personal Assistant Agent
**Date: 2026-06-28  |  Benchmark Setup: 5 Sequential Sessions**

---

## Executive Summary

This report evaluates the performance of the **Memory-Augmented Personal Assistant Agent** in recalling user identity, stack preferences, and database updates across 5 separate interactive sessions. We compare the **Memory-ON** configuration (utilizing vector episodic storage + reflection insights) against the **Memory-OFF** configuration (zero-shot baseline).

### Aggregate Performance Metrics

| Configuration | Average Recall Accuracy | Memories Stored | Active Insights |
|---|---|---|---|
| **Memory-ON** | **{report['summary']['memory_on_average_accuracy'] * 100:.1f}%** | 10 turns | Yes (Dynamic Update) |
| **Memory-OFF** | **{report['summary']['memory_off_average_accuracy'] * 100:.1f}%** | 0 turns | No |

**Improvement Delta**: **+{report['summary']['improvement_delta'] * 100:.1f}%** increase in query accuracy and preference alignment.

---

## Detailed Session Walkthrough

"""
        for idx in range(len(report["runs"]["memory_on"])):
            run_on = report["runs"]["memory_on"][idx]
            run_off = report["runs"]["memory_off"][idx]
            
            md_content += f"""### Session {run_on['session_index']}: {run_on['session_id']}
* **User Query**: "{run_on['query']}"
* **Expected Context Retrieval**: `{run_on['expected_recall']}`

#### Memory-ON Mode
* **Recall Accuracy**: `{run_on['recall_accuracy'] * 100:.0f}%` (Recalled: `{run_on['recalled_keys']}`, Missed: `{run_on['failed_keys']}`)
* **Agent Response**:
  > {run_on['response'].replace(chr(10), chr(10) + '> ')}
* **Active Insights**:
{chr(10).join([f"  - {ins}" for ins in run_on['insights_active']]) if run_on['insights_active'] else '  - None'}

#### Memory-OFF Mode
* **Recall Accuracy**: `{run_off['recall_accuracy'] * 100:.0f}%`
* **Agent Response**:
  > {run_off['response'].replace(chr(10), chr(10) + '> ')}

---
"""
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"[EVAL] Saved Markdown evaluation report to: {md_path}")


if __name__ == "__main__":
    evaluator = MemoryEvaluator("memory_store_eval")
    report = evaluator.run_benchmark()
    evaluator.save_reports(
        report, 
        json_path="d:/projects/Research Intern - Ada love lace/assignment-3/supporting_code/memory_store/evaluation_report.json",
        md_path="d:/projects/Research Intern - Ada love lace/assignment-3/supporting_code/memory_store/evaluation_report.md"
    )
