import sys
import time
from agent import ReActAgent

def run_5_tests():
    # Instantiate the agent
    agent = ReActAgent()

    # Define 5 diverse test prompts matching the agent's capabilities
    test_cases = [
        {
            "num": 1,
            "name": "Multi-Hop Financial Query",
            "prompt": "Find Apple's 2024 annual revenue and Microsoft's 2024 annual revenue, and calculate the absolute difference between them."
        },
        {
            "num": 2,
            "name": "Flaky Scraper Recovery (Dynamic Re-planning)",
            "prompt": "Scrape financial statistics from the URL 'https://flaky-database.api/data' and recover using backup mirror endpoints if a failure occurs."
        },
        {
            "num": 3,
            "name": "Buggy Code Runtime Correction",
            "prompt": "Calculate the result of dividing 100 by the divisor variable (initially 0). Catch standard runtime exceptions (ZeroDivisionError) and correct it to divisor=5."
        },
        {
            "num": 4,
            "name": "Recursive Demographic Analysis",
            "prompt": "Search for the individual populations of Paris, Tokyo, and New York City, and calculate their mathematical average population using python."
        },
        {
            "num": 5,
            "name": "Missing Tool Input Query Refinement",
            "prompt": "Search for Google's 2024 annual revenue, handling an empty search string error initially, and recover using refined keywords."
        }
    ]

    print("=" * 80)
    print("      RUNNING LOCAL EVALUATION SUITE FOR 5 DIVERSE TEST INPUTS      ")
    print("=" * 80)

    for tc in test_cases:
        print(f"\n[TEST CASE {tc['num']}/5] {tc['name']}")
        print(f"Prompt: \"{tc['prompt']}\"")
        print("-" * 80)
        
        start_time = time.time()
        outcome = agent.run(tc["prompt"])
        duration = time.time() - start_time
        
        # Display the step-by-step trace logs beautifully
        print("AGENT TRACE LOGS:")
        for log in outcome["trace_logs"]:
            log_type = log["type"]
            msg = log["message"]
            detail = log.get("detail")
            
            # Stylize different log types
            if log_type == "RECEIVE_TASK":
                print(f"  --> [Task Received] {msg}")
            elif log_type == "INITIAL_PLAN":
                print(f"  --> [Plan] {msg} -> {detail.get('plan') if detail else ''}")
            elif log_type == "THOUGHT":
                print(f"  --> [Thought] {msg}")
            elif log_type == "ACTION":
                print(f"  --> [Action] {msg}")
                if detail:
                    print(f"      Tool: {detail.get('tool')}")
                    print(f"      Input: \"{detail.get('input')}\"")
            elif log_type == "OBSERVATION":
                print(f"  --> [Observation] {msg}")
                if detail:
                    output_snippet = str(detail.get('output'))
                    if len(output_snippet) > 120:
                        output_snippet = output_snippet[:120] + "..."
                    print(f"      Output: {output_snippet}")
            elif log_type == "FAILURE_TRACE":
                print(f"  [!] [Failure Detected] {msg}")
            elif log_type == "RE-PLANNING":
                print(f"  --> [Re-planning] Deciding fallback strategy...")
                if detail:
                    print(f"      Rationale: {detail.get('thought')}")
            elif log_type == "PLAN_UPDATED":
                print(f"  --> [Plan Updated] Remaining steps redirected -> {detail.get('remaining_plan') if detail else ''}")
            elif log_type == "FINISH":
                print(f"  --> [Finished] {msg}")
        
        print("-" * 80)
        print(f"SUCCESS: {outcome['success']}")
        print(f"STEPS TAKEN: {outcome['steps_taken']}")
        print(f"FAILURES ENCOUNTERED & RESOLVED: {outcome['failures_resolved']}")
        print(f"FINAL COMPILED ANSWER: {outcome['final_answer']}")
        print(f"LATENCY: {duration:.4f}s")
        print("=" * 80)

if __name__ == "__main__":
    run_5_tests()
