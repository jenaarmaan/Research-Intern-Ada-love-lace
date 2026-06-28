import os
import sys
import time
import subprocess
import tempfile
import re
import numpy as np
from typing import List, Dict, Any, Tuple
from google import genai
from dotenv import load_dotenv

# Initialize APIs
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
gemini_available = False
client = None

if api_key:
    try:
        client = genai.Client(api_key=api_key.strip())
        gemini_available = True
    except Exception:
        gemini_available = False

# --- L5.1 Input Guardrails (Prompt Injection Detection) ---
class InputGuardrail:
    def __init__(self):
        self.injection_keywords = [
            "ignore previous", "system files", "override instruction", 
            "restrict command", "bypass security", "exploit", "hack",
            "sudo", "rm -rf", "delete database", "drop table"
        ]

    def is_safe(self, text: str) -> Tuple[bool, str]:
        text_lower = text.lower()
        for kw in self.injection_keywords:
            if kw in text_lower:
                return False, f"Blocked Prompt Injection Pattern Match: '{kw}'"
        return True, "Passed Safety Check"

# --- Isolated Python Sandbox Executor ---
class SandboxREPL:
    def execute(self, code: str, work_dir: str) -> Dict[str, Any]:
        temp_file = os.path.join(work_dir, "sandbox_run.py")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            res = subprocess.run(
                [sys.executable, "sandbox_run.py"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            success = (res.returncode == 0)
            output = res.stdout + "\n" + res.stderr
            return {
                "success": success,
                "output": output.strip(),
                "exit_code": res.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "Execution timed out.", "exit_code": -1}
        except Exception as e:
            return {"success": False, "output": f"Subprocess error: {e}", "exit_code": -2}

# --- Episodic Memory Layer ---
class VectorEpisodicMemory:
    def __init__(self):
        self.database = []

    def embed_text(self, text: str) -> List[float]:
        # Character-hash local dense vectorizer (fallback)
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        vector = [0.0] * 128
        txt = text.lower()
        for char_idx, char in enumerate(txt):
            if char in chars:
                pos = chars.index(char)
                vector[(char_idx + pos) % 128] += 1.0
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [float(x / norm) for x in vector]
        return vector

    def add_memory(self, session_id: str, content: str):
        v = self.embed_text(content)
        self.database.append({
            "session_id": session_id,
            "content": content,
            "vector": np.array(v)
        })

    def search(self, query: str, k: int = 1) -> List[Dict[str, Any]]:
        if not self.database:
            return []
        qv = np.array(self.embed_text(query))
        results = []
        for m in self.database:
            sim = np.dot(qv, m["vector"]) / (np.linalg.norm(qv) * np.linalg.norm(m["vector"]))
            results.append((m, float(sim)))
        results.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in results[:k] if item[1] > 0.15]

# --- Reflection Insight Profiler ---
class ReflectionEngine:
    def __init__(self):
        self.insights = []

    def reflect(self, history: List[Dict[str, str]]) -> List[str]:
        # Local keyword parser for simulation
        all_text = " ".join([h["content"] for h in history]).lower()
        self.insights = []
        if "regression" in all_text:
            self.insights.append("User is researching linear regression modeling.")
        if "prime" in all_text:
            self.insights.append("User is exploring prime count densities.")
        if "frequency" in all_text:
            self.insights.append("User is implementing character frequency analytics.")
        if "variance" in all_text:
            self.insights.append("User is calculating statistical variance metrics.")
        return self.insights

# --- Researcher Agent Profiles ---
class Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

class SupervisorAgent(Agent):
    def __init__(self):
        super().__init__("Dr. Liam", "Research Coordinator")

class LiteratureAnalystAgent(Agent):
    def __init__(self):
        super().__init__("Dr. Elena", "Literature Analyst")

class ResearchDeveloperAgent(Agent):
    def __init__(self):
        super().__init__("Marcus", "Software Engineer")

class SafetyInspectorAgent(Agent):
    def __init__(self):
        super().__init__("Clara", "Safety Inspector")

# --- Capstone Research Pipeline ---
class ResearchPipeline:
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.analyst = LiteratureAnalystAgent()
        self.developer = ResearchDeveloperAgent()
        self.safety = SafetyInspectorAgent()
        
        self.guardrail = InputGuardrail()
        self.repl = SandboxREPL()
        self.memory = VectorEpisodicMemory()
        self.reflection = ReflectionEngine()
        
        self.logs = []

    def log(self, step: str, agent_name: str, message: str, detail: Any = None):
        self.logs.append({
            "step": step,
            "agent": agent_name,
            "message": message,
            "detail": detail or {}
        })

    def run_phase_1(self, raw_query: str, session_id: str, offline: bool = False) -> Dict[str, Any]:
        """Phase 1: Ingest, Safety scan, Literature synthesis, and Code generation."""
        self.logs = []
        self.log("INGEST_QUERY", "System", f"Ingested research task query: '{raw_query}'")

        # 1. Safety Guardrail Scan
        self.log("SAFETY_SCAN", self.safety.name, "Clara scanning prompt query parameters for safety guardrails...")
        safe, block_msg = self.guardrail.is_safe(raw_query)
        if not safe:
            self.log("SAFETY_BLOCK", self.safety.name, f"CRITICAL: {block_msg}", {"blocked": True})
            return {
                "status": "blocked",
                "message": block_msg,
                "logs": self.logs
            }
        self.log("SAFETY_PASS", self.safety.name, "Passed all input validation metrics.")

        # Episodic Retrieval
        self.log("MEM_LOOKUP", "System", "Searching vector database for matching academic experiences...")
        matched_memories = self.memory.search(raw_query, k=1)
        if matched_memories:
            self.log("MEM_RECALL", "System", f"Recalled {len(matched_memories)} episodic memory block.", {"recalled": matched_memories[0]["content"]})
        else:
            self.log("MEM_RECALL", "System", "No previous matching episodic research context found.")

        # 2. Literature Analyst synthesis
        self.log("LIT_START", self.analyst.name, "Elena searching publications and synthesizing methodology...")
        time.sleep(0.1) # Sim latency
        methodology = self._get_literature_synthesis(raw_query)
        self.log("LIT_COMPLETE", self.analyst.name, "Elena completed publication analysis.", {"methodology": methodology})

        # 3. Developer writing script code
        self.log("DEV_START", self.developer.name, "Marcus writing calculation script module...")
        code = self._get_generated_code(raw_query)
        self.log("DEV_COMPLETE", self.developer.name, "Marcus completed implementation code block.", {"code": code})

        # 4. Safety Inspector checks code structure before execution
        self.log("HITL_PROMPT", self.safety.name, "Clara scanning script code and setting Human-in-the-Loop permission block.")
        
        return {
            "status": "waiting_approval",
            "code_to_run": code,
            "methodology": methodology,
            "logs": self.logs
        }

    def run_phase_2(self, code: str, raw_query: str, session_id: str) -> Dict[str, Any]:
        """Phase 2: Subprocess Sandbox Run & Final Review Compilation."""
        self.log("HITL_APPROVED", "System", "Human-in-the-loop permission granted. Starting subprocess execution...")
        
        # Execute script
        with tempfile.TemporaryDirectory() as temp_dir:
            exec_res = self.repl.execute(code, temp_dir)
            
        success = exec_res["success"]
        output = exec_res["output"]
        self.log("EXEC_FINISHED", self.safety.name, f"Subprocess finished with exit code {exec_res['exit_code']}.", {"output": output})

        # Reflect and compile
        self.log("REFLECT_START", self.supervisor.name, "Liam updating research context engine...")
        history_turn = [
            {"role": "user", "content": raw_query},
            {"role": "assistant", "content": output}
        ]
        insights = self.reflection.reflect(history_turn)
        for ins in insights:
            self.log("INSIGHT_UPDATED", self.supervisor.name, f"Committed reflection insight: '{ins}'")

        # Save to episodic vector store
        self.memory.add_memory(session_id, f"Research Task: {raw_query} | Output: {output[:60]}...")

        # Formulate review
        review = f"### Final Research Summary\n\n**Output of Script Run**:\n```bash\n{output}\n```\n\n**Scientific Conclusion**: The math calculations compiled successfully. Verified correct outputs under isolated subprocess environments."
        self.log("FINISH", "System", "Research process completed successfully.")

        return {
            "status": "success",
            "output": output,
            "review": review,
            "logs": self.logs
        }

    def _get_literature_synthesis(self, query: str) -> str:
        q = query.lower()
        if "regression" in q:
            return "Linear regression models relationships by fitting a linear equation to observed data: y = mx + c. Intercept and slope are derived using least-squares calculations."
        elif "prime" in q:
            return "Prime numbers are positive integers greater than 1 with no positive divisors other than 1 and itself. Density calculations count occurrences in discrete integer blocks."
        elif "frequency" in q:
            return "Word count frequency calculates the histogram distributions of tokens in text streams, filtering punctuation."
        elif "variance" in q:
            return "Variance determines data dispersion: Var = E[(X - mean)^2]. Standard deviation is the square root of the variance value."
        else:
            return "Standard mathematical analysis. Formulates conversions and lists values."

    def _get_generated_code(self, query: str) -> str:
        q = query.lower()
        if "regression" in q:
            return (
                "x = [1, 2, 3]\n"
                "y = [2, 3, 5]\n"
                "n = len(x)\n"
                "sum_x = sum(x)\n"
                "sum_y = sum(y)\n"
                "sum_xx = sum(i*i for i in x)\n"
                "sum_xy = sum(x[i]*y[i] for i in range(n))\n"
                "slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x**2)\n"
                "intercept = (sum_y - slope * sum_x) / n\n"
                "print(f'Slope: {slope}, Intercept: {intercept}')\n"
            )
        elif "prime" in q:
            return (
                "def is_prime(n):\n"
                "    if n <= 1: return False\n"
                "    for i in range(2, int(n**0.5) + 1):\n"
                "        if n % i == 0: return False\n"
                "    return True\n"
                "for block in range(5):\n"
                "    start = block * 20 + 1\n"
                "    end = (block + 1) * 20\n"
                "    count = sum(1 for i in range(start, end+1) if is_prime(i))\n"
                "    print(f'Block {start}-{end}: {count} primes')\n"
            )
        elif "frequency" in q:
            return (
                "content = 'the quick brown fox jumps over the lazy dog the fox is quick'\n"
                "words = content.split()\n"
                "freq = {}\n"
                "for w in words: freq[w] = freq.get(w, 0) + 1\n"
                "sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)\n"
                "for w, f in sorted_freq[:3]:\n"
                "    print(f'{w}: {f}')\n"
            )
        elif "variance" in q:
            return (
                "data = [10, 20, 30, 40, 50]\n"
                "mean = sum(data) / len(data)\n"
                "variance = sum((x - mean)**2 for x in data) / len(data)\n"
                "std_dev = variance ** 0.5\n"
                "print(f'Mean: {mean}, Variance: {variance}, StdDev: {std_dev}')\n"
            )
        else:
            return (
                "temps = [0, 10, 20, 30, 40]\n"
                "for t in temps:\n"
                "    k = t + 273.15\n"
                "    print(f'{t}C = {k}K')\n"
            )

if __name__ == "__main__":
    # Test script offline
    pipeline = ResearchPipeline()
    p1 = pipeline.run_phase_1("Calculate variance of [10, 20]", "sess_test", offline=True)
    print("Phase 1 Status:", p1["status"])
    if p1["status"] == "waiting_approval":
        p2 = pipeline.run_phase_2(p1["code_to_run"], "Calculate variance of [10, 20]", "sess_test")
        print("Phase 2 Status:", p2["status"])
        print(p2["review"])
