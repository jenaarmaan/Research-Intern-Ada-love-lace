import json
import os
import time
from typing import List, Dict, Any
from agent import ReActAgent

def run_evaluation_suite():
    """
    Executes the 10 benchmark tasks to evaluate the autonomous task-solving agent.
    Collects performance, step count, latency, and re-planning counts, saving reports.
    """
    # 1. Instantiate the Agent
    agent = ReActAgent()
    
    # 2. Define the 10 Diverse Benchmark Tasks
    benchmark_tasks = [
        {
            "id": "task_1",
            "name": "Multi-Hop Financial Query",
            "task": "Find Apple's 2024 annual revenue and Microsoft's 2024 annual revenue, and calculate the absolute difference between them."
        },
        {
            "id": "task_2",
            "name": "Flaky Scraper Recovery",
            "task": "Scrape financial statistics from the URL 'https://flaky-database.api/data' and recover using backup mirror endpoints if a failure occurs."
        },
        {
            "id": "task_3",
            "name": "Buggy Code Execution Correction",
            "task": "Calculate the result of dividing 100 by the divisor variable (initially 0). Catch standard runtime exceptions (ZeroDivisionError) and correct it to divisor=5."
        },
        {
            "id": "task_4",
            "name": "Recursive Demographic Analysis",
            "task": "Search for the individual populations of Paris, Tokyo, and New York City, and calculate their mathematical average population using python."
        },
        {
            "id": "task_5",
            "name": "Sandbox Fibonacci Computation",
            "task": "Construct a Python sequence solver inside the sandboxed environment to calculate the 15th Fibonacci number."
        },
        {
            "id": "task_6",
            "name": "Calculated Future Compound Interest",
            "task": "Search for interest details and calculate future compound value of a $10,000 principal at a 5% interest rate over 5 years."
        },
        {
            "id": "task_7",
            "name": "Multi-Step Historic Geographic Query",
            "task": "Locate Alan Turing's birth year, and verify the capital city of the country where his birth city is located."
        },
        {
            "id": "task_8",
            "name": "Scraped Document Keyword Analysis",
            "task": "Fetch the Alan Turing fact sheet URL 'https://science-history.org/turing' and write a Python block to count how many times the word 'Turing' occurs."
        },
        {
            "id": "task_9",
            "name": "Missing Tool Input and Query Refinement",
            "task": "Search for Google's 2024 annual revenue, handling an empty search string error initially, and recover using refined keywords."
        },
        {
            "id": "task_10",
            "name": "Complex Corporate Balance Metric",
            "task": "Retrieve Apple's total assets, liabilities, and shareholder equity for 2024, and calculate its Debt-to-Equity Ratio."
        }
    ]

    print("==========================================================")
    print("      RUNNING AUTONOMOUS AGENT EVALUATION BENCHMARK       ")
    print("==========================================================")
    
    results = []
    total_latency = 0.0
    total_steps = 0
    total_failures_resolved = 0
    success_count = 0
    
    # Create supporting directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    for idx, t in enumerate(benchmark_tasks, 1):
        print(f"\n[TASK {idx}/10] Running: {t['name']}")
        print(f"Prompt: {t['task']}")
        
        # Run agent
        outcome = agent.run(t["task"])
        
        # Aggregate metrics
        success = outcome["success"]
        latency = outcome["execution_time_seconds"]
        steps = outcome["steps_taken"]
        failures_resolved = outcome["failures_resolved"]
        
        total_latency += latency
        total_steps += steps
        total_failures_resolved += failures_resolved
        if success:
            success_count += 1
            
        task_result = {
            "task_id": t["id"],
            "name": t["name"],
            "prompt": t["task"],
            "success": success,
            "steps_taken": steps,
            "failures_resolved": failures_resolved,
            "latency_seconds": latency,
            "final_answer": outcome["final_answer"],
            "trace_length": len(outcome["trace_logs"])
        }
        results.append(task_result)
        
        status_str = "[SUCCESS]" if success else "[FAILED]"
        print(f"Outcome: {status_str} in {latency:.3f}s | Steps: {steps} | Failures Resolved: {failures_resolved}")
        print(f"Answer: {outcome['final_answer']}")

    # 3. Compute Summary Aggregates
    success_rate = (success_count / len(benchmark_tasks)) * 100
    avg_steps = total_steps / len(benchmark_tasks)
    avg_latency = total_latency / len(benchmark_tasks)
    
    evaluation_report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system": "ReAct Agent v1.0",
            "environment": "Windows Py3 Sandbox"
        },
        "summary": {
            "total_tasks": len(benchmark_tasks),
            "successful_tasks": success_count,
            "success_rate_percent": success_rate,
            "total_steps": total_steps,
            "average_steps_per_task": avg_steps,
            "total_failures_resolved": total_failures_resolved,
            "total_execution_time_seconds": round(total_latency, 3),
            "average_latency_seconds": round(avg_latency, 3)
        },
        "tasks": results
    }

    # 4. Save JSON Report
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, indent=4)
        
    # 5. Save Markdown Report
    md_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Evaluation Benchmark Report\n\n")
        f.write(f"*Generated on: {evaluation_report['metadata']['timestamp']}*\n")
        f.write(f"*System: {evaluation_report['metadata']['system']}*\n\n")
        
        f.write("## Performance Summary Matrix\n\n")
        f.write("| Metric | Value |\n")
        f.write("| :--- | :--- |\n")
        f.write(f"| **Total Tasks Evaluated** | {evaluation_report['summary']['total_tasks']} |\n")
        f.write(f"| **Successful Executions** | {evaluation_report['summary']['successful_tasks']} |\n")
        f.write(f"| **Overall Success Rate** | **{evaluation_report['summary']['success_rate_percent']:.1f}%** |\n")
        f.write(f"| **Total Steps Taken** | {evaluation_report['summary']['total_steps']} |\n")
        f.write(f"| **Average Steps per Task** | {evaluation_report['summary']['average_steps_per_task']:.1f} |\n")
        f.write(f"| **Transient Failures Resolved** | {evaluation_report['summary']['total_failures_resolved']} |\n")
        f.write(f"| **Total Latency (seconds)** | {evaluation_report['summary']['total_execution_time_seconds']:.3f}s |\n")
        f.write(f"| **Average Latency per Task** | {evaluation_report['summary']['average_latency_seconds']:.3f}s |\n\n")
        
        f.write("## Detailed Task Evaluations\n\n")
        f.write("| Task ID | Name | Success | Steps | Failures Resolved | Latency | Final Answer |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :--- |\n")
        
        for r in results:
            status_symbol = "PASSED" if r["success"] else "FAILED"
            f.write(f"| `{r['task_id']}` | **{r['name']}** | {status_symbol} | {r['steps_taken']} | {r['failures_resolved']} | {r['latency_seconds']:.3f}s | {r['final_answer']} |\n")
            
        f.write("\n## Dynamic Re-planning Case Analysis\n\n")
        f.write("### 1. Transient HTTP 500 Network Scrape Recovery (`task_2`)\n")
        f.write("- **Scenario**: The agent is tasked to retrieve economic data from `https://flaky-database.api/data`. The primary server yields a 500 server timeout.\n")
        f.write("- **Recovery**: The agent catches the error, updates its plan, searches the index for backup registries, and fetches the data successfully from the secondary mirror `https://backup-database.api/data`.\n\n")
        
        f.write("### 2. Code Runtime Error Correction (`task_3`)\n")
        f.write("- **Scenario**: The agent must run a Python arithmetic calculation where the divisor variable is set to 0. It generates a `ZeroDivisionError` exception.\n")
        f.write("- **Recovery**: The agent intercepts the division by zero exception traceback, logs the failure, updates its internal division parameters to a correct divisor (5), and executes it again to output the correct result.\n\n")
        
        f.write("### 3. Missing Tool Query Parameter Refinement (`task_9`)\n")
        f.write("- **Scenario**: The search index requires query keywords to be at least 3 characters long. The initial request provides a blank query, causing a search error.\n")
        f.write("- **Recovery**: The agent captures the search error, reasons that the query parameters were empty, alters its task to construct refined keywords ('Google revenue 2024'), and completes the search.\n")
        
    print("\n==========================================================")
    print("   BENCHMARK RUN COMPLETE. REPORTS GENERATED SUCCESSFULLY. ")
    print("==========================================================")
    print(f"JSON Report: {json_path}")
    print(f"Markdown Report: {md_path}")
    print("==========================================================")

if __name__ == "__main__":
    run_evaluation_suite()
