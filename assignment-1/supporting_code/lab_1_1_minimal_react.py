import re
import time

# Colors for terminal styling
class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

# 1. Define Tools
def search_tool(query: str) -> str:
    """Mock search tool containing simple facts."""
    db = {
        "capital of france": "Paris is the capital of France.",
        "capital of germany": "Berlin is the capital of Germany.",
        "population of paris": "The population of Paris is approximately 2.1 million."
    }
    q = query.lower().strip()
    for key in db:
        if key in q or q in key:
            return db[key]
    return f"No search results found for: '{query}'"

def math_tool(expression: str) -> str:
    """Math tool to execute safe mathematical calculations."""
    # Strip dangerous characters to ensure safety
    cleaned_expr = re.sub(r'[^0-9\+\-\*\/\(\)\. ]', '', expression)
    try:
        # Safe evaluation of basic math
        result = eval(cleaned_expr, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating math expression '{expression}': {e}"

# Tool mapper
TOOLS = {
    "Search": search_tool,
    "Math": math_tool
}

# 2. Mock LLM Brain
class MockLLMBrain:
    """Simulates LLM response containing Thought, Action, and Final Answer matching ReAct syntax."""
    def __init__(self):
        self.step = 0

    def generate(self, prompt: str) -> str:
        self.step += 1
        
        # Scenario: "Calculate (45 * 23) + 12 and verify the capital of France."
        if "calculate" in prompt.lower() and "france" in prompt.lower():
            if self.step == 1:
                return """Thought: I need to perform two steps to resolve this prompt. First, I must calculate the mathematical equation: (45 * 23) + 12. I should use the Math tool for this task.
Action: Math[(45 * 23) + 12]"""
            elif self.step == 2:
                return """Thought: The calculation output is 1047. Now, I need to verify the capital of France. I should use the Search tool to query this fact.
Action: Search[capital of France]"""
            elif self.step == 3:
                return """Thought: I have obtained both pieces of information: the calculation result is 1047, and the capital of France is Paris. I am ready to formulate the final answer.
Final Answer: The calculation of (45 * 23) + 12 yields 1047, and the capital of France is confirmed as Paris."""
        
        return "Final Answer: Task completed successfully."

# 3. ReAct Agent Loop
class ReActAgent:
    def __init__(self):
        self.brain = MockLLMBrain()
        self.max_loops = 5

    def run(self, query: str):
        print(f"{Color.CYAN}{Color.BOLD}[ReAct Agent Initialized]{Color.END} Query: '{query}'")
        
        current_prompt = f"User Query: {query}\nSolve the query using ReAct loop. You have access to: Math[expr], Search[query].\n"
        
        for i in range(1, self.max_loops + 1):
            print(f"\n{Color.BOLD}--- CYCLE {i} ---{Color.END}")
            
            # Generate LLM thought/action
            llm_output = self.brain.generate(current_prompt)
            print(f"{Color.YELLOW}[LLM OUTPUT]{Color.END}\n{llm_output}")
            
            # Parse output
            if "Final Answer:" in llm_output:
                final_ans = llm_output.split("Final Answer:", 1)[1].strip()
                print(f"\n{Color.GREEN}{Color.BOLD}[GOAL ACHIEVED] Final Answer:{Color.END} {final_ans}")
                break
                
            # Parse action call (format: Action: ToolName[arg])
            action_match = re.search(r"Action:\s*(\w+)\[(.*?)\]", llm_output)
            if action_match:
                tool_name, tool_arg = action_match.groups()
                print(f"\n[EXECUTION] Calling Tool: {Color.BOLD}{tool_name}{Color.END} with argument: '{tool_arg}'")
                
                # Execute tool
                if tool_name in TOOLS:
                    observation = TOOLS[tool_name](tool_arg)
                else:
                    observation = f"Error: Tool '{tool_name}' is not recognized."
                    
                print(f"[OBSERVATION] {Color.CYAN}Observation: {observation}{Color.END}")
                
                # Feed observation back into context
                current_prompt += f"\n{llm_output}\nObservation: {observation}\n"
            else:
                print(f"{Color.RED}[ERROR] Agent generated output without valid action or final answer.{Color.END}")
                break
            
            time.sleep(1.0)

if __name__ == "__main__":
    agent = ReActAgent()
    agent.run("Calculate (45 * 23) + 12 and verify the capital of France.")
