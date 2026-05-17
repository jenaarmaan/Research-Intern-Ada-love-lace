import time
import sys
import re

# ANSI Color Codes for Premium Console Styling
class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

class MockDockerSandbox:
    """Simulates an isolated Docker container with a file system and bash terminal."""
    def __init__(self):
        self.files = {}
        self.installed_packages = set(["pip", "python"])
        self.command_history = []

    def execute_bash(self, command: str) -> tuple[str, int]:
        """Executes a simulated bash command and returns (stdout/stderr, exit_code)."""
        self.command_history.append(command)
        command = command.strip()
        
        # Simulating file writes via editor or echoing
        if command.startswith("echo") and ">" in command:
            # Simple echo parser: echo 'content' > filename
            match = re.search(r"echo\s+['\"](.*?)['\"]\s*>\s*([a-zA-Z0-9_\-\.]+)", command, re.DOTALL)
            if match:
                content, filename = match.groups()
                self.files[filename] = content
                return f"Successfully wrote to {filename}", 0
            return "Syntax error in echo redirect simulation", 1

        # Simulating file reading
        elif command.startswith("cat "):
            filename = command.split(" ", 1)[1].strip()
            if filename in self.files:
                return self.files[filename], 0
            else:
                return f"cat: {filename}: No such file or directory", 1

        # Simulating package installations
        elif command.startswith("pip install "):
            package = command.split("pip install ", 1)[1].strip()
            self.installed_packages.add(package)
            return f"Collecting {package}\n  Downloading {package}-py3-none-any.whl\nInstalling collected packages: {package}\nSuccessfully installed {package}", 0

        # Simulating Python executions
        elif command.startswith("python "):
            filename = command.split("python ", 1)[1].strip()
            if filename not in self.files:
                return f"python: can't open file '{filename}': [Errno 2] No such file or directory", 2
            
            content = self.files[filename]

            # Scenario 1: Check for missing dependencies
            if "import flask" in content and "flask" not in self.installed_packages:
                return "Traceback (most recent call last):\n  File \"app.py\", line 1, in <module>\n    import flask\nModuleNotFoundError: No module named 'flask'", 1
            
            # Scenario 2: Check for syntax errors
            if "def index()" in content and "def index():" not in content:
                return "  File \"app.py\", line 4\n    def index()\n               ^\nSyntaxError: expected ':'", 1
            
            # Scenario 3: Successful run
            if "import flask" in content and "def index():" in content:
                return "Flask App running on http://127.0.0.1:5000/ (Press CTRL+C to quit)\n[INFO] Route '/' accessed successfully - status 200", 0

            return "Python executed successfully with empty output.", 0

        elif command == "ls" or command == "dir":
            if not self.files:
                return "", 0
            return "\n".join(self.files.keys()), 0

        else:
            return f"bash: {command}: command not found", 127

class DevinAgent:
    """Simulates Devin's cognitive loop (Reason, Plan, Act, Observe)."""
    def __init__(self, sandbox: MockDockerSandbox):
        self.sandbox = sandbox
        self.plan = [
            {"id": 1, "task": "Create app.py and write basic Flask server code", "status": "pending"},
            {"id": 2, "task": "Verify code by running the Flask server", "status": "pending"},
            {"id": 3, "task": "Verify route / returns success code", "status": "pending"}
        ]
        self.memory_insights = []

    def print_plan(self):
        print(f"\n{Color.BOLD}--- CURRENT DEVIN HIERARCHICAL PLAN ---{Color.END}")
        for item in self.plan:
            status_color = Color.GREEN if item["status"] == "completed" else (Color.YELLOW if item["status"] == "pending" else Color.RED)
            print(f" [{status_color}{item['status'].upper()}{Color.END}] {item['id']}. {item['task']}")
        print(f"{Color.BOLD}---------------------------------------{Color.END}\n")

    def run(self, goal: str):
        print(f"{Color.CYAN}{Color.BOLD}[Devin Initialized]{Color.END} Goal: {goal}")
        self.print_plan()
        
        step = 0
        max_steps = 10
        
        while step < max_steps:
            step += 1
            print(f"\n{Color.MAGENTA}=== AGENT LOOP CYCLE {step} ==={Color.END}")
            
            # 1. PERCEIVE / REASON
            next_task = next((t for t in self.plan if t["status"] == "pending"), None)
            if not next_task:
                print(f"\n{Color.GREEN}{Color.BOLD}[SUCCESS] TASK COMPLETED!{Color.END} All items on Devin's checklist are successful.")
                break

            print(f"{Color.BOLD}[Reasoning]{Color.END} Current focal task is Task {next_task['id']}: \"{next_task['task']}\".")
            
            # 2. DECIDE / PLAN / ACT
            if next_task["id"] == 1:
                # Intentionally writing code with a missing dependency and a syntax error to show Devin's self-healing loop!
                print(f"{Color.BOLD}[Action]{Color.END} Generating Flask web application code with an intentional syntax bug...")
                code = "import flask\\napp = flask.Flask(__name__)\\n\\n@app.route('/')\\ndef index()\\n    return 'Hello from Devin Sandbox!'\\n\\nif __name__ == '__main__':\\n    app.run()"
                cmd = f"echo '{code}' > app.py"
                
                print(f"  Executing Command: {Color.CYAN}{cmd}{Color.END}")
                stdout, code_exit = self.sandbox.execute_bash(cmd)
                
                # 3. OBSERVE
                print(f"  {Color.BOLD}[Observation]{Color.END} Bash Exit Code: {code_exit}")
                print(f"  Output:\n{stdout}")
                next_task["status"] = "completed"
                self.print_plan()

            elif next_task["id"] == 2:
                print(f"{Color.BOLD}[Action]{Color.END} Verifying code in sandbox by starting Python execution.")
                cmd = "python app.py"
                print(f"  Executing Command: {Color.CYAN}{cmd}{Color.END}")
                stdout, code_exit = self.sandbox.execute_bash(cmd)
                
                # Observe failure
                print(f"  {Color.BOLD}[Observation]{Color.END} Bash Exit Code: {code_exit}")
                print(f"  Output:\n{Color.RED}{stdout}{Color.END}")
                
                if code_exit != 0:
                    print(f"\n{Color.RED}{Color.BOLD}[Self-Correction Triggered]{Color.END} Compilation failed! Analyzing logs...")
                    
                    if "ModuleNotFoundError" in stdout:
                        # Re-plan! Inject package install task before task 2
                        print(f"{Color.YELLOW}[Planning Re-routing]{Color.END} Missing dependency detected. Dynamic plan restructuring: inserting pip installation.")
                        # Reset current task to pending
                        next_task["status"] = "pending"
                        # Insert a new task before task 2
                        self.plan.insert(1, {"id": 1.5, "task": "Install missing package 'flask' via pip", "status": "pending"})
                        self.memory_insights.append("Insight: Flask library was missing in core sandbox. Inserted installation sequence.")
                    
                    elif "SyntaxError" in stdout:
                        print(f"{Color.YELLOW}[Planning Re-routing]{Color.END} Python syntax error discovered in app.py. Dynamically inserting patch fix.")
                        next_task["status"] = "pending"
                        self.plan.insert(1, {"id": 1.8, "task": "Fix syntax error in app.py (add missing colon after function declaration)", "status": "pending"})
                        self.memory_insights.append("Insight: Found syntax bug (missing colon after def index). Writing correction edit.")
                else:
                    print(f"  {Color.GREEN}[SUCCESS] Code verified successfully (Exit Code 0). Marking task as completed.{Color.END}")
                    next_task["status"] = "completed"
                        
                self.print_plan()

            # Execution of dynamic sub-task: pip installation
            elif next_task["id"] == 1.5:
                print(f"{Color.BOLD}[Action]{Color.END} Installing required packages inside Sandbox...")
                cmd = "pip install flask"
                print(f"  Executing Command: {Color.CYAN}{cmd}{Color.END}")
                stdout, code_exit = self.sandbox.execute_bash(cmd)
                print(f"  {Color.BOLD}[Observation]{Color.END} Bash Exit Code: {code_exit}")
                print(f"  Output:\n{Color.GREEN}{stdout}{Color.END}")
                next_task["status"] = "completed"
                self.print_plan()

            # Execution of dynamic sub-task: fixing syntax error
            elif next_task["id"] == 1.8:
                print(f"{Color.BOLD}[Action]{Color.END} Fixing the syntax error (adding colon to index function definition)...")
                # Correct code
                code = "import flask\\napp = flask.Flask(__name__)\\n\\n@app.route('/')\\ndef index():\\n    return 'Hello from Devin Sandbox!'\\n\\nif __name__ == '__main__':\\n    app.run()"
                cmd = f"echo '{code}' > app.py"
                print(f"  Executing Command: {Color.CYAN}{cmd}{Color.END}")
                stdout, code_exit = self.sandbox.execute_bash(cmd)
                print(f"  {Color.BOLD}[Observation]{Color.END} Bash Exit Code: {code_exit}")
                next_task["status"] = "completed"
                self.print_plan()

            elif next_task["id"] == 3:
                print(f"{Color.BOLD}[Action]{Color.END} Running the final server code to verify successful route mapping.")
                cmd = "python app.py"
                print(f"  Executing Command: {Color.CYAN}{cmd}{Color.END}")
                stdout, code_exit = self.sandbox.execute_bash(cmd)
                print(f"  {Color.BOLD}[Observation]{Color.END} Bash Exit Code: {code_exit}")
                
                if code_exit == 0:
                    print(f"  Output:\n{Color.GREEN}{stdout}{Color.END}")
                    next_task["status"] = "completed"
                else:
                    print(f"  Output:\n{Color.RED}{stdout}{Color.END}")
                    next_task["status"] = "failed"
                self.print_plan()

            time.sleep(1.0) # Simulating processing delay

        print(f"\n{Color.CYAN}--- DEVIN INTERN SUMMARY ---{Color.END}")
        print(f"Sandbox Command History: {self.sandbox.command_history}")
        print(f"Cognitive Insights Retained: {self.memory_insights}")

if __name__ == "__main__":
    sandbox = MockDockerSandbox()
    agent = DevinAgent(sandbox)
    agent.run("Deploy a simple Flask web application in a Linux Docker environment.")
