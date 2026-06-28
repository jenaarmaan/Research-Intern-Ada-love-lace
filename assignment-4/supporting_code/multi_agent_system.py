import os
import sys
import time
import subprocess
import tempfile
import re
from typing import List, Dict, Any, Tuple
from google import genai
from dotenv import load_dotenv

# Load Environment and Initialize API
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

class Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def get_system_prompt(self) -> str:
        return f"You are {self.name}, the {self.role} in a software development team. Collaborate professionally to deliver clean, working code."

class ProductManagerAgent(Agent):
    def __init__(self):
        super().__init__("Sarah", "Product Manager")

    def refine_spec(self, raw_spec: str, offline: bool = False) -> str:
        if gemini_available and not offline:
            try:
                prompt = (
                    f"Refine the following natural language coding specification into a structured markdown "
                    f"feature document with user stories, scope, and technical acceptance criteria:\n\n{raw_spec}"
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={"system_instruction": self.get_system_prompt()}
                )
                return response.text.strip()
            except Exception as e:
                pass

        # Offline Fallback / Simulator
        return (
            f"# Feature Specification: {raw_spec[:50]}...\n\n"
            f"## User Stories\n"
            f"*   **As a User**, I want to trigger this program with clean input parameters so I get accurate calculations.\n"
            f"*   **As a Developer**, I want clean modular functions so the code is easy to test.\n\n"
            f"## Scope & Acceptance Criteria\n"
            f"*   Must implement all core requirements outlined in: '{raw_spec}'\n"
            f"*   All functions must handle boundary values (e.g. negative inputs, empty datasets).\n"
            f"*   Must include a comprehensive test suite using Python's standard `unittest` framework."
        )

class ArchitectAgent(Agent):
    def __init__(self):
        super().__init__("David", "System Architect")

    def design_structure(self, spec: str, offline: bool = False) -> Tuple[str, List[Dict[str, str]]]:
        if gemini_available and not offline:
            try:
                prompt = (
                    f"Given this feature specification, design the files structure. Outline the file paths to create "
                    f"and write a brief technical design for each file (classes, methods, interfaces, dependencies). "
                    f"Return your design. Your output must clearly list target files to create.\n\n{spec}"
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={"system_instruction": self.get_system_prompt()}
                )
                design = response.text.strip()
                # Parse files to create
                files = []
                for line in design.splitlines():
                    if "file:" in line.lower() or "path:" in line.lower() or "creating:" in line.lower():
                        match = re.search(r'([\w\-]+\.py)', line)
                        if match:
                            fname = match.group(1)
                            if fname not in [f["path"] for f in files]:
                                files.append({"path": fname, "description": f"Design block for {fname}"})
                
                if not files:
                    # Default files if LLM output couldn't be parsed
                    files = [{"path": "core_lib.py", "description": "Core features"}, {"path": "test_core.py", "description": "Unit tests"}]
                return design, files
            except Exception:
                pass

        # Offline Fallback
        if "fibonacci" in spec.lower() or "prime" in spec.lower():
            files = [
                {"path": "math_lib.py", "description": "Contains fibonacci(n) and is_prime(n) functions."},
                {"path": "test_math.py", "description": "Unittests verifying the mathematical utilities."}
            ]
        elif "rpn" in spec.lower() or "polish" in spec.lower():
            files = [
                {"path": "rpn.py", "description": "Contains RPNCalculator class handling operations."},
                {"path": "test_rpn.py", "description": "Unittests checking stack operation and arithmetic validation."}
            ]
        elif "count" in spec.lower() or "analyzer" in spec.lower():
            files = [
                {"path": "text_analyzer.py", "description": "Word, sentence, and char frequency calculations."},
                {"path": "test_analyzer.py", "description": "Unittests asserting analytics metrics."}
            ]
        elif "json" in spec.lower() or "transaction" in spec.lower():
            files = [
                {"path": "json_db.py", "description": "Key-value store with commit and rollback transactions."},
                {"path": "test_db.py", "description": "Unittests checking transaction isolation."}
            ]
        else:
            files = [
                {"path": "temp_converter.py", "description": "Celsius/Fahrenheit/Kelvin logging utility."},
                {"path": "test_temp.py", "description": "Unittests verifying precision and CSV logging."}
            ]

        design_doc = (
            f"# Technical System Design\n\n"
            f"We partition the codebase into 2 core modules:\n"
            f"1.  **Core Implementation File**: `{files[0]['path']}` containing target classes and validation logic.\n"
            f"2.  **Test Suite File**: `{files[1]['path']}` executing testing assertions.\n\n"
            f"### API Contract Specifications\n"
            f"*   All functions must raise appropriate standard Python exceptions (`ValueError`, `IndexError`) on invalid inputs.\n"
            f"*   The test file will dynamically import the code and execute asserts under standard subprocess environments."
        )
        return design_doc, files

class DeveloperAgent(Agent):
    def __init__(self):
        super().__init__("Alex", "Software Developer")

    def write_code(self, filename: str, spec: str, design: str, feedback: str = "", offline: bool = False) -> str:
        if gemini_available and not offline:
            try:
                prompt = (
                    f"You are writing code for file: '{filename}'.\n"
                    f"Project Spec:\n{spec}\n\n"
                    f"System Design:\n{design}\n\n"
                )
                if feedback:
                    prompt += f"WARNING: Previous test run failed with following error trace:\n{feedback}\nPlease adjust the code contents to repair this bug."
                
                prompt += "\nOutput ONLY valid raw Python code inside your response. Do not surround with markdown backticks."
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={"system_instruction": self.get_system_prompt()}
                )
                # Strip backticks if LLM returns them anyway
                code = response.text.strip()
                if code.startswith("```"):
                    code = re.sub(r'^```python\n|^```\n?', '', code)
                    code = re.sub(r'\n?```$', '', code)
                return code
            except Exception:
                pass

        # Offline Fallback
        return self._simulate_code(filename, spec, feedback)

    def _simulate_code(self, filename: str, spec: str, feedback: str) -> str:
        is_test = filename.startswith("test_")
        
        # Scenario 1: Fibonacci & Prime
        if "fibonacci" in spec.lower() or "prime" in spec.lower():
            if is_test:
                return (
                    "import unittest\n"
                    "from math_lib import fibonacci, is_prime\n\n"
                    "class TestMathLib(unittest.TestCase):\n"
                    "    def test_fibonacci(self):\n"
                    "        self.assertEqual(fibonacci(5), [0, 1, 1, 2, 3])\n"
                    "        self.assertEqual(fibonacci(0), [])\n"
                    "        with self.assertRaises(ValueError):\n"
                    "            fibonacci(-1)\n\n"
                    "    def test_prime(self):\n"
                    "        self.assertTrue(is_prime(5))\n"
                    "        self.assertFalse(is_prime(4))\n"
                    "        self.assertFalse(is_prime(1))\n\n"
                    "if __name__ == '__main__':\n"
                    "    unittest.main()\n"
                )
            else:
                # If there's no feedback and we want to show a bug that gets corrected:
                if not feedback:
                    # Let's add a buggy code for prime (it returns True for 4 because loop doesn't check divisibility correctly)
                    return (
                        "def fibonacci(n):\n"
                        "    if n < 0: raise ValueError('N must be non-negative')\n"
                        "    if n == 0: return []\n"
                        "    if n == 1: return [0]\n"
                        "    seq = [0, 1]\n"
                        "    while len(seq) < n:\n"
                        "        seq.append(seq[-1] + seq[-2])\n"
                        "    return seq\n\n"
                        "def is_prime(n):\n"
                        "    if n <= 1: return False\n"
                        "    # BUG: Starts checking from 3, misses divisibility by 2 or doesn't check composite inputs properly\n"
                        "    for i in range(3, int(n**0.5) + 1):\n"
                        "        if n % i == 0: return False\n"
                        "    return True # Throws bug for 4\n"
                    )
                else:
                    # Repaired code
                    return (
                        "def fibonacci(n):\n"
                        "    if n < 0: raise ValueError('N must be non-negative')\n"
                        "    if n == 0: return []\n"
                        "    if n == 1: return [0]\n"
                        "    seq = [0, 1]\n"
                        "    while len(seq) < n:\n"
                        "        seq.append(seq[-1] + seq[-2])\n"
                        "    return seq\n\n"
                        "def is_prime(n):\n"
                        "    if n <= 1: return False\n"
                        "    for i in range(2, int(n**0.5) + 1):\n"
                        "        if n % i == 0: return False\n"
                        "    return True\n"
                    )

        # Scenario 2: RPN Calculator
        elif "rpn" in spec.lower() or "polish" in spec.lower():
            if is_test:
                return (
                    "import unittest\n"
                    "from rpn import RPNCalculator\n\n"
                    "class TestRPN(unittest.TestCase):\n"
                    "    def test_rpn(self):\n"
                    "        calc = RPNCalculator()\n"
                    "        calc.evaluate('3')\n"
                    "        calc.evaluate('4')\n"
                    "        calc.evaluate('+')\n"
                    "        self.assertEqual(calc.get_result(), 7.0)\n"
                    "        calc.evaluate('2')\n"
                    "        calc.evaluate('*')\n"
                    "        self.assertEqual(calc.get_result(), 14.0)\n\n"
                    "if __name__ == '__main__':\n"
                    "    unittest.main()\n"
                )
            else:
                if not feedback:
                    # Bug: division zero isn't handled or stack pop misses IndexError
                    return (
                        "class RPNCalculator:\n"
                        "    def __init__(self):\n"
                        "        self.stack = []\n"
                        "    def push(self, val):\n"
                        "        self.stack.append(float(val))\n"
                        "    def pop(self):\n"
                        "        return self.stack.pop() # BUG: Throws IndexError under empty stack without message\n"
                        "    def evaluate(self, token):\n"
                        "        if token in ('+', '-', '*', '/'):\n"
                        "            b = self.pop()\n"
                        "            a = self.pop()\n"
                        "            if token == '+': self.push(a + b)\n"
                        "            elif token == '-': self.push(a - b)\n"
                        "            elif token == '*': self.push(a * b)\n"
                        "            elif token == '/': self.push(a / b)\n"
                        "        else:\n"
                        "            self.push(token)\n"
                        "    def get_result(self):\n"
                        "        return self.stack[-1] if self.stack else 0.0\n"
                    )
                else:
                    return (
                        "class RPNCalculator:\n"
                        "    def __init__(self):\n"
                        "        self.stack = []\n"
                        "    def push(self, val):\n"
                        "        self.stack.append(float(val))\n"
                        "    def pop(self):\n"
                        "        if not self.stack: raise IndexError('Pop from empty stack')\n"
                        "        return self.stack.pop()\n"
                        "    def evaluate(self, token):\n"
                        "        if token in ('+', '-', '*', '/'):\n"
                        "            if len(self.stack) < 2: raise IndexError('Insufficient operands')\n"
                        "            b = self.pop()\n"
                        "            a = self.pop()\n"
                        "            if token == '+': self.push(a + b)\n"
                        "            elif token == '-': self.push(a - b)\n"
                        "            elif token == '*': self.push(a * b)\n"
                        "            elif token == '/':\n"
                        "                if b == 0: raise ZeroDivisionError('Division by zero')\n"
                        "                self.push(a / b)\n"
                        "        else:\n"
                        "            self.push(float(token))\n"
                        "    def get_result(self):\n"
                        "        return self.stack[-1] if self.stack else 0.0\n"
                    )

        # Scenario 3: Text Analyzer
        elif "count" in spec.lower() or "analyzer" in spec.lower():
            if is_test:
                return (
                    "import unittest\n"
                    "import os\n"
                    "from text_analyzer import analyze_text_file\n\n"
                    "class TestAnalyzer(unittest.TestCase):\n"
                    "    def test_analyzer(self):\n"
                    "        with open('temp.txt', 'w') as f:\n"
                    "            f.write('Hello world. Hello python.')\n"
                    "        res = analyze_text_file('temp.txt')\n"
                    "        self.assertEqual(res['word_count'], 4)\n"
                    "        self.assertEqual(res['sentence_count'], 2)\n"
                    "        os.remove('temp.txt')\n\n"
                    "if __name__ == '__main__':\n"
                    "    unittest.main()\n"
                )
            else:
                if not feedback:
                    return (
                        "import os_typo # BUG: Typo in standard module\n\n"
                        "def analyze_text_file(filepath):\n"
                        "    with open(filepath, 'r') as f:\n"
                        "        content = f.read()\n"
                        "    words = content.split()\n"
                        "    return {'word_count': len(words), 'sentence_count': 0}\n"
                    )
                else:
                    return (
                        "import os\n\n"
                        "def analyze_text_file(filepath):\n"
                        "    if not os.path.exists(filepath):\n"
                        "        raise FileNotFoundError('Target text file not found')\n"
                        "    with open(filepath, 'r', encoding='utf-8') as f:\n"
                        "        content = f.read()\n"
                        "    words = content.split()\n"
                        "    sentences = [s for s in content.split('.') if s.strip()]\n"
                        "    chars = {}\n"
                        "    for c in content:\n"
                        "        if c.isalnum():\n"
                        "            chars[c] = chars.get(c, 0) + 1\n"
                        "    return {\n"
                        "        'word_count': len(words),\n"
                        "        'sentence_count': len(sentences),\n"
                        "        'char_frequencies': chars\n"
                        "    }\n"
                    )

        # Scenario 4: JSON DB
        elif "json" in spec.lower() or "transaction" in spec.lower():
            if is_test:
                return (
                    "import unittest\n"
                    "import os\n"
                    "from json_db import JSONDB\n\n"
                    "class TestJSONDB(unittest.TestCase):\n"
                    "    def test_kv(self):\n"
                    "        db = JSONDB('test_db.json')\n"
                    "        db.set('name', 'Armaan')\n"
                    "        self.assertEqual(db.get('name'), 'Armaan')\n"
                    "        db.begin()\n"
                    "        db.set('name', 'Arjun')\n"
                    "        self.assertEqual(db.get('name'), 'Arjun')\n"
                    "        db.rollback()\n"
                    "        self.assertEqual(db.get('name'), 'Armaan')\n"
                    "        if os.path.exists('test_db.json'): os.remove('test_db.json')\n\n"
                    "if __name__ == '__main__':\n"
                    "    unittest.main()\n"
                )
            else:
                if not feedback:
                    return (
                        "import json\n"
                        "class JSONDB:\n"
                        "    def __init__(self, filepath):\n"
                        "        self.filepath = filepath\n"
                        "        self.data = {}\n"
                        "    def set(self, key, val):\n"
                        "        self.data[key] = val\n"
                        "    def get(self, key):\n"
                        "        return None # BUG: always returns None\n"
                    )
                else:
                    return (
                        "import json\n"
                        "import os\n"
                        "class JSONDB:\n"
                        "    def __init__(self, filepath):\n"
                        "        self.filepath = filepath\n"
                        "        self.data = {}\n"
                        "        self.load()\n"
                        "        self.transaction = None\n"
                        "    def load(self):\n"
                        "        if os.path.exists(self.filepath):\n"
                        "            with open(self.filepath, 'r') as f:\n"
                        "                self.data = json.load(f)\n"
                        "    def save(self):\n"
                        "        with open(self.filepath, 'w') as f:\n"
                        "            json.dump(self.data, f)\n"
                        "    def set(self, key, val):\n"
                        "        if self.transaction is not None:\n"
                        "            self.transaction[key] = val\n"
                        "        else:\n"
                        "            self.data[key] = val\n"
                        "            self.save()\n"
                        "    def get(self, key):\n"
                        "        if self.transaction is not None and key in self.transaction:\n"
                        "            return self.transaction[key]\n"
                        "        return self.data.get(key)\n"
                        "    def begin(self):\n"
                        "        self.transaction = dict(self.data)\n"
                        "    def commit(self):\n"
                        "        if self.transaction is None: raise RuntimeError('No active transaction')\n"
                        "        self.data = self.transaction\n"
                        "        self.transaction = None\n"
                        "        self.save()\n"
                        "    def rollback(self):\n"
                        "        if self.transaction is None: raise RuntimeError('No active transaction')\n"
                        "        self.transaction = None\n"
                    )

        # Scenario 5: Temp Converter
        else:
            if is_test:
                return (
                    "import unittest\n"
                    "from temp_converter import convert_temp\n\n"
                    "class TestTemp(unittest.TestCase):\n"
                    "    def test_convert(self):\n"
                    "        self.assertAlmostEqual(convert_temp(32, 'F', 'C'), 0.0)\n"
                    "        self.assertAlmostEqual(convert_temp(100, 'C', 'F'), 212.0)\n\n"
                    "if __name__ == '__main__':\n"
                    "    unittest.main()\n"
                )
            else:
                if not feedback:
                    return (
                        "def convert_temp(val, from_unit, to_unit):\n"
                        "    # BUG: always divides by zero for Kelvin\n"
                        "    if from_unit == 'K': return val / 0\n"
                        "    return val\n"
                    )
                else:
                    return (
                        "import csv\n"
                        "import os\n"
                        "def convert_temp(val, from_unit, to_unit):\n"
                        "    from_unit = from_unit.upper()\n"
                        "    to_unit = to_unit.upper()\n"
                        "    if from_unit == to_unit: return val\n"
                        "    if from_unit == 'C': c = val\n"
                        "    elif from_unit == 'F': c = (val - 32) * 5/9\n"
                        "    elif from_unit == 'K': c = val - 273.15\n"
                        "    else: raise ValueError('Invalid unit')\n"
                        "    if to_unit == 'C': return c\n"
                        "    elif to_unit == 'F': return c * 9/5 + 32\n"
                        "    elif to_unit == 'K': return c + 273.15\n"
                        "    else: raise ValueError('Invalid unit')\n"
                    )

class QAEngineerAgent(Agent):
    def __init__(self):
        super().__init__("Rachel", "QA Engineer")

    def run_tests(self, file_map: Dict[str, str], work_dir: str) -> Dict[str, Any]:
        # Save files to workspace directory
        test_file = ""
        for name, content in file_map.items():
            path = os.path.join(work_dir, name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            if name.startswith("test_"):
                test_file = name

        if not test_file:
            return {"success": False, "output": "No test file found to execute.", "errors": ["No test file"]}

        # Run tests in subprocess
        try:
            res = subprocess.run(
                [sys.executable, test_file],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            success = (res.returncode == 0)
            output = res.stdout + "\n" + res.stderr
            errors = []
            if not success:
                errors = [line for line in output.splitlines() if "Error" in line or "FAIL:" in line or "Traceback" in line]
            return {
                "success": success,
                "output": output,
                "errors": errors
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "Test execution timed out.", "errors": ["TimeoutExpired"]}
        except Exception as e:
            return {"success": False, "output": f"Test runner crash: {e}", "errors": [str(e)]}

class SoftwareCompanyPipeline:
    def __init__(self):
        self.pm = ProductManagerAgent()
        self.architect = ArchitectAgent()
        self.developer = DeveloperAgent()
        self.qa = QAEngineerAgent()
        self.logs = []

    def log(self, step: str, agent_name: str, message: str, detail: Any = None):
        self.logs.append({
            "step": step,
            "agent": agent_name,
            "message": message,
            "detail": detail or {}
        })

    def run(self, raw_spec: str, correction_enabled: bool = True, offline: bool = False) -> Dict[str, Any]:
        self.logs = []
        self.log("INGEST_SPEC", "System", f"Received task specification: '{raw_spec}'")
        
        # 1. Product Manager Turn
        self.log("PM_START", self.pm.name, "Product Manager refining the feature specs...")
        refined_spec = self.pm.refine_spec(raw_spec, offline)
        self.log("PM_COMPLETE", self.pm.name, "Refined specifications document completed.", {"spec": refined_spec})
        
        # 2. Architect Turn
        self.log("ARCH_START", self.architect.name, "Architect designing code modules and API structure...")
        design_doc, files = self.architect.design_structure(refined_spec, offline)
        self.log("ARCH_COMPLETE", self.architect.name, f"Architect completed system design. Target files defined: {[f['path'] for f in files]}", {"design": design_doc, "files": files})
        
        # 3. Developer Initial Generation
        file_contents = {}
        for f in files:
            fname = f["path"]
            self.log("DEV_START", self.developer.name, f"Developer coding file '{fname}'...")
            code = self.developer.write_code(fname, refined_spec, design_doc, feedback="", offline=offline)
            file_contents[fname] = code
            self.log("DEV_COMPLETE", self.developer.name, f"Completed implementation of '{fname}'.", {"code": code})

        # 4. QA & Correction Loop
        with tempfile.TemporaryDirectory() as temp_dir:
            self.log("QA_START", self.qa.name, "QA Engineer running sandbox testing suite...")
            qa_res = self.qa.run_tests(file_contents, temp_dir)
            
            iterations = 0
            max_iterations = 3 if correction_enabled else 0
            
            while not qa_res["success"] and iterations < max_iterations:
                iterations += 1
                error_trace = qa_res["output"]
                self.log("RE-PLANNING", "System", f"Test Failure detected! Routing error trace back to Developer (Iteration {iterations}/{max_iterations}).", {"errors": qa_res["errors"]})
                
                # Developer attempts to fix files (typically core files, not tests)
                for f in files:
                    fname = f["path"]
                    if not fname.startswith("test_"):
                        self.log("DEV_START", self.developer.name, f"Developer reviewing traceback and adjusting '{fname}'...")
                        repaired_code = self.developer.write_code(fname, refined_spec, design_doc, feedback=error_trace, offline=offline)
                        file_contents[fname] = repaired_code
                        self.log("DEV_COMPLETE", self.developer.name, f"Rewrote adjusted implementation of '{fname}'.", {"code": repaired_code})
                
                # Re-run QA
                self.log("QA_START", self.qa.name, "QA Engineer executing sandboxed testing suite on repaired codebase...")
                qa_res = self.qa.run_tests(file_contents, temp_dir)
            
            success = qa_res["success"]
            self.log("FINISH", "System", "Orchestration process completed.", {
                "success": success,
                "iterations": iterations,
                "output": qa_res["output"]
            })
            
            return {
                "success": success,
                "iterations": iterations,
                "files": file_contents,
                "test_output": qa_res["output"],
                "logs": self.logs
            }

if __name__ == "__main__":
    # Local CLI Verification
    company = SoftwareCompanyPipeline()
    print("Executing offline verification loop...")
    res = company.run("Fibonacci prime checker", correction_enabled=True, offline=True)
    print("Success status:", res["success"])
    print("Correction Iterations:", res["iterations"])
    print("Generated files:", list(res["files"].keys()))
