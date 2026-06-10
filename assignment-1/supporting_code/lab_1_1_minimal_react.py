import re
import time
import sys

# Colors for terminal styling
class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Helper parsers for dynamic query analysis
def extract_math_expr(query_str: str) -> str:
    pattern = r"[\d\s\+\-\*\/\(\)\.]+"
    matches = re.findall(pattern, query_str)
    valid_matches = []
    for m in matches:
        m_strip = m.strip()
        if len(m_strip) >= 3 and any(char in m_strip for char in "+-*/") and any(char.isdigit() for char in m_strip):
            valid_matches.append(m_strip)
    if valid_matches:
        return max(valid_matches, key=len)
    return ""

def extract_search_query(query_str: str) -> str:
    math_expr = extract_math_expr(query_str)
    clean_query = query_str
    if math_expr:
        clean_query = clean_query.replace(math_expr, "")
    match = re.search(r"(?:verify|find|search for|what is|capital of|population of)\s+([^.]+)", clean_query, re.IGNORECASE)
    if match:
        extracted = match.group(1).strip()
        extracted = re.sub(r"^(?:the capital of|the population of|the|capital of|population of)\s+", "", extracted, flags=re.IGNORECASE)
        if "capital of" in query_str.lower():
            return f"capital of {extracted}"
        elif "population of" in query_str.lower():
            return f"population of {extracted}"
        return extracted
    return ""

# 1. Define Tools
def search_tool(query: str) -> str:
    """Mock search tool containing simple facts."""
    db = {
        "capital of france": "Paris is the capital of France.",
        "capital of germany": "Berlin is the capital of Germany.",
        "capital of italy": "Rome is the capital of Italy.",
        "capital of spain": "Madrid is the capital of Spain.",
        "capital of united kingdom": "London is the capital of the United Kingdom.",
        "capital of usa": "Washington, D.C. is the capital of the United States.",
        "capital of united states": "Washington, D.C. is the capital of the United States.",
        "capital of japan": "Tokyo is the capital of Japan.",
        "capital of india": "New Delhi is the capital of India.",
        "population of france": "The population of France is approximately 68 million.",
        "population of germany": "The population of Germany is approximately 84 million.",
        "population of paris": "The population of Paris is approximately 2.1 million.",
        "population of tokyo": "The population of Tokyo is approximately 37.4 million.",
        "population of london": "The population of London is approximately 8.9 million.",
        "population of new york": "The population of New York is approximately 8.3 million."
    }
    q = query.lower().strip()
    for key in db:
        if key in q or q in key:
            return db[key]
    return f"{query.capitalize()} info retrieved (mock database result)."

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

# 2. Dynamic Mock LLM Brain
class MockLLMBrain:
    """Simulates LLM response containing Thought, Action, and Final Answer matching ReAct syntax."""
    def __init__(self):
        self.step = 0

    def generate(self, prompt: str) -> str:
        self.step += 1
        
        # Extract original query from the prompt context
        query_match = re.search(r"User Query:\s*(.*)", prompt)
        query = query_match.group(1).strip() if query_match else ""
        
        math_expr = extract_math_expr(query)
        search_q = extract_search_query(query)
        
        if self.step == 1:
            if math_expr:
                return f"Thought: I need to perform two steps to resolve this prompt. First, I must calculate the mathematical equation: {math_expr}. I should use the Math tool for this task.\nAction: Math[{math_expr}]"
            elif search_q:
                return f"Thought: I need to verify the information for '{search_q}'. I should use the Search tool.\nAction: Search[{search_q}]"
            else:
                return "Thought: I don't see any specific sub-problems. I will synthesize the final answer.\nFinal Answer: Task completed successfully."
                
        elif self.step == 2:
            # Extract previous math observation if any
            math_obs = "N/A"
            obs_matches = re.findall(r"Observation:\s*(.*)", prompt)
            if obs_matches:
                math_obs = obs_matches[-1].strip()
                
            if math_expr and search_q:
                return f"Thought: The calculation output is {math_obs}. Now, I need to verify the info for '{search_q}'. I should use the Search tool to query this fact.\nAction: Search[{search_q}]"
            else:
                return f"Thought: I have obtained the results. I will now compile the final response.\nFinal Answer: The result is {math_obs}."
                
        elif self.step == 3:
            # Extract observations from history
            obs_matches = re.findall(r"Observation:\s*(.*)", prompt)
            math_obs = obs_matches[0].strip() if len(obs_matches) > 0 else "N/A"
            search_obs = obs_matches[1].strip() if len(obs_matches) > 1 else "N/A"
            
            final_ans = ""
            if math_expr:
                final_ans += f"The calculation yields {math_obs}. "
            if search_q:
                final_ans += f"{search_obs}"
            if not final_ans:
                final_ans = "Task resolved successfully."
                
            return f"Thought: I have obtained all pieces of information. I am ready to formulate the final answer.\nFinal Answer: {final_ans}"
            
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
            
            time.sleep(0.5)

if __name__ == "__main__":
    # If a command line argument is provided, use it; otherwise ask the user or run default
    if len(sys.argv) > 1:
        query_input = " ".join(sys.argv[1:])
    else:
        query_input = "Calculate (45 * 23) + 12 and verify the capital of France."
        
    agent = ReActAgent()
    agent.run(query_input)
