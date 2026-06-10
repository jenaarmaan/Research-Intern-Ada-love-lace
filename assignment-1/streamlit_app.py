import streamlit as st
import streamlit.components.v1 as components
import time
import re

def render_mermaid(code: str, height: int = 400):
    html_code = f"""
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #0d1117;
            overflow: hidden;
        }}
        .container {{
            background-color: #0d1117; 
            padding: 15px; 
            border-radius: 8px; 
            border: 1px solid #30363d; 
            height: {height}px;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: auto;
            box-sizing: border-box;
        }}
        .mermaid {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 100%;
        }}
        .mermaid svg {{
            max-width: 95% !important;
            max-height: {height - 40}px !important;
            height: auto !important;
            width: auto !important;
        }}
    </style>
    <div class="container">
        <div class="mermaid">
            {code}
        </div>
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ 
            startOnLoad: true, 
            theme: 'dark',
            flowchart: {{
                useMaxWidth: false,
                htmlLabels: true
            }}
        }});
    </script>
    """
    components.html(html_code, height=height, scrolling=False)


# Set page configuration for a premium, wide dashboard look
st.set_page_config(
    page_title="AgenticAI Lab: Interactive Architecture Lab",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Premium custom CSS for glassmorphism, dark themes, and custom styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Global Styling */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Sleek Title Gradient */
    .title-gradient {
        background: linear-gradient(135deg, #FF4B4B 0%, #7E22CE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle-text {
        font-size: 1.2rem;
        color: #A0AEC0;
        margin-bottom: 2rem;
    }
    
    /* Styled Glassmorphic Cards */
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }
    
    /* Styled CRT Terminal */
    .terminal-console {
        background-color: #0c0f12 !important;
        border: 2px solid #1a202c !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: #00FF66 !important;
        padding: 1rem;
        height: 280px;
        overflow-y: auto;
        white-space: pre-wrap;
        box-shadow: inset 0 0 10px #000000;
    }
    
    /* Mock Editor Frame */
    .editor-frame {
        background-color: #1e1e1e;
        border-radius: 8px;
        border: 1px solid #333;
        font-family: 'JetBrains Mono', monospace;
        color: #d4d4d4;
        padding: 1rem;
        height: 280px;
        overflow-y: auto;
    }
    
    /* Mermaid Container Style */
    .mermaid-box {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        font-weight: 800;
        font-size: 1.4rem;
        background: linear-gradient(135deg, #00FF66 0%, #00F0FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE CONFIG -----------------

# Devin State Defaults
if 'devin_step' not in st.session_state:
    st.session_state.devin_step = 0
if 'devin_logs' not in st.session_state:
    st.session_state.devin_logs = ["System initialized. Awaiting task initiation..."]
if 'devin_code' not in st.session_state:
    st.session_state.devin_code = ""
if 'devin_insights' not in st.session_state:
    st.session_state.devin_insights = []
if 'devin_plan' not in st.session_state:
    st.session_state.devin_plan = [
        {"id": 1, "task": "Create app.py and write basic Flask server code", "status": "pending"},
        {"id": 2, "task": "Verify code by running the Flask server", "status": "pending"},
        {"id": 3, "task": "Verify route / returns success code", "status": "pending"}
    ]
if 'devin_sandbox_installed' not in st.session_state:
    st.session_state.devin_sandbox_installed = set(["pip", "python"])

# Perplexity State Defaults
if 'perp_step' not in st.session_state:
    st.session_state.perp_step = 0
if 'perp_logs' not in st.session_state:
    st.session_state.perp_logs = ["System initialized. Awaiting search query initiation..."]
if 'perp_episodic_memory' not in st.session_state:
    st.session_state.perp_episodic_memory = {}
if 'perp_citations' not in st.session_state:
    st.session_state.perp_citations = []
if 'perp_gap_detected' not in st.session_state:
    st.session_state.perp_gap_detected = False
if 'perp_answer' not in st.session_state:
    st.session_state.perp_answer = ""
if 'perp_query' not in st.session_state:
    st.session_state.perp_query = ""
if 'last_perp_query' not in st.session_state:
    st.session_state.last_perp_query = ""

# ----------------- SIMULATED DATABASES -----------------

WEB_INDEX = {
    "2026 Oscar winners": [
        {
            "url": "https://variety.com/2026/oscars/winners",
            "title": "98th Academy Awards: The Complete Winners List",
            "content": "At the 98th Academy Awards (Oscars 2026), 'Dune: Part Three' dominated the night, taking home 6 Oscars including Best Director for Denis Villeneuve and Best Cinematography. The film won the most awards of any movie that evening."
        },
        {
            "url": "https://hollywoodreporter.com/awards/2026-oscars-sweep",
            "title": "Dune: Part Three Sweeps 2026 Oscars",
            "content": "Warner Bros' sci-fi epic 'Dune: Part Three' swept the technical categories and earned 6 statuettes at the 2026 Academy Awards. It stands out as the biggest Oscar victor of the year, leaving competitors trailing behind."
        }
    ],
    "Dune: Part Three movie budget": [
        {
            "url": "https://boxofficemojo.com/dune-part-three-financials",
            "title": "Dune: Part Three Budget and Box Office Analysis",
            "content": "Dune: Part Three carried a hefty production budget of $190 million, co-financed by Legendary Pictures and Warner Bros. It has grossed over $720 million worldwide, representing a massive financial success."
        },
        {
            "url": "https://wikipedia.org/wiki/Dune_Part_Three",
            "title": "Wikipedia: Dune: Part Three (2026 Film)",
            "content": "Dune: Part Three is a 2026 epic science fiction film. Principal photography took place on a budget of approximately $190 million USD, with filming in Jordan, Italy, and Budapest."
        }
    ],
    "piracy solutions": [
        {
            "url": "https://techcrunch.com/2026/security/anti-piracy-standards",
            "title": "Modern Technical Anti-Piracy Standards in 2026",
            "content": "Modern anti-piracy relies heavily on hardware-rooted trust, multi-factor authentication, and secure decryption enclaves. Dynamic DRM systems like Widevine L1 represent the best defensive solutions."
        },
        {
            "url": "https://wired.com/tech/piracy-prevention-widevine",
            "title": "Google Widevine L1 Prevents Media Piracy",
            "content": "Google's Widevine L1 DRM protocol enforces that video decryption keys are only handled within isolated hardware enclaves, preventing OS-level debuggers or screen recorders from sniffing high-quality streams."
        }
    ],
    "technical importance of secure enclaves": [
        {
            "url": "https://wikipedia.org/wiki/Hardware-backed_security",
            "title": "Wikipedia: Hardware-backed security enclaves",
            "content": "Hardware-rooted trust enclaves are critical because they execute decryption instructions in isolated registers, separating cryptographic operations from the main OS to prevent memory dump exploits."
        },
        {
            "url": "https://ieee.org/publications/hardware-enclave-security",
            "title": "IEEE: Security Importance of Hardware-Rooted Enclaves",
            "content": "Secure enclaves are technically important because they protect assets even if the host operating system is fully compromised. The decryption keys never leave the hardware boundary."
        }
    ]
}

# ----------------- APP LAYOUT & SIDEBAR -----------------

with st.sidebar:
    st.markdown('<div class="sidebar-header">🤖 AgenticAI Workspace</div>', unsafe_allow_html=True)
    st.caption("Module 1 Research Lab  •  Assignment 1")
    
    # Navigation Selector
    st.markdown("### Choose Lab Dashboard:")
    nav_selection = st.radio(
        label="Navigation Menu",
        options=["📊 Architecture Comparison", "💻 Devin Task Agent", "🔍 Perplexity Search Agent", "🧪 Lab Sessions (L1.1 & L1.2)", "📖 Workspace Documentation"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.markdown("### Student Intern State")
    st.info("💡 **Active Branch**: `assignment-1`\n\n🎯 **Coursework Status**: Fully Completed\n\n📈 **Weightage**: 15%")

# ----------------- PAGE 1: COMPARATIVE ARCHITECTURE -----------------

if nav_selection == "📊 Architecture Comparison":
    st.markdown('<div class="title-gradient">Agent Architecture Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">A rigorous comparative analysis of Devin (Action-Oriented Task Solver) and Perplexity Pro Search (Information Synthesizer)</div>', unsafe_allow_html=True)
    
    with st.expander("📖 User Guide: How to Interpret the Architectures", expanded=False):
        st.markdown("""
        ### 💡 Key Concepts
        * **Devin (Stateful Coder)**: Executes scripts, tracks compiler errors, and writes local files inside a container environment.
        * **Perplexity (Search Synthesizer)**: Searches queries in parallel, detects missing information gaps, and compiles cited markdown answers.
        ### 🛠️ Interactive Exploration
        * Review the side-by-side **System Integration Schematics** mapping sensor-actuator loops.
        * Compare architectural details in the **PEAS Dimension Comparison** table at the bottom of the page.
        """)
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💡 Devin Architecture")
        st.markdown("""
        **Devin** operates as a closed-loop system inside an isolated container:
        - **Core Focus**: Manipulating local operating system state (writing, installing, compiling, debugging).
        - **Environment**: Highly stateful, dynamic, write-access Docker environment.
        - **Planning Engine**: Hierarchical Directed Acyclic Graphs (DAG) combined with tree search.
        """)
        
        # Devin Mermaid Render
        st.markdown("**System Integration Schematic (Mermaid)**")
        render_mermaid("""
graph TB
    User[User Prompt] <--> Chat[Chat API]
    LLM[LLM Brain] <--> Plan[Plan DAG Manager]
    LLM <--> Eval[LLM-as-a-Judge]
    LLM <--> Memory[Episodic Memory Logs]
    LLM --> Terminal[Bash Terminal Sandbox]
    LLM --> Editor[File Editor/Patcher]
    LLM --> Browser[Chromium Web Browser]
    Terminal -->|stdout/stderr| LLM
    Editor -->|Content/Diffs| LLM
    Compiler[Compiler exit code] --> LLM
    Eval -->|Success/Correction| Plan
        """, height=420)

    with col2:
        st.subheader("🔍 Perplexity Pro Search")
        st.markdown("""
        **Perplexity** operates as an open-world, real-time research engine:
        - **Core Focus**: Distilling global information under strict latency requirements.
        - **Environment**: Stateful read-only open web indices, crawlers, and scrapers.
        - **Planning Engine**: Parallel multi-hop query routing and dynamic gap checks.
        """)
        
        # Perplexity Mermaid Render
        st.markdown("**System Integration Schematic (Mermaid)**")
        render_mermaid("""
graph TB
    User[User Query] --> Parser[Semantic Router]
    Parser --> Router[Search Query Router]
    Router --> Plan[Multi-Hop Planner]
    Plan --> SearchAPI[Google/Bing Search Index]
    SearchAPI --> Scraper[Web Scrapers]
    Scraper --> Memory[Episodic Fact Cache]
    Memory --> LLM[LLM Synthesis Judge]
    LLM --> Gap[Gap Detector / Re-planner]
    Gap -->|No Gaps| Answer[Cited Markdown Answer]
    Gap -->|Gaps Found| Router
        """, height=420)

    st.divider()
    
    st.subheader("📊 PEAS Framework Comparison")
    
    # Custom HTML Table for PEAS comparison to meet Premium Styling guidelines
    st.markdown("""
    <table style="width:100%; border-collapse: collapse; margin: 1rem 0; border: 1px solid rgba(255,255,255,0.1);">
      <tr style="background-color: rgba(255,255,255,0.05); text-align: left;">
        <th style="padding: 12px; border: 1px solid rgba(255,255,255,0.1); color: #FF4B4B;">PEAS Dimension</th>
        <th style="padding: 12px; border: 1px solid rgba(255,255,255,0.1); color: #FF4B4B;">Devin (Software Engineering)</th>
        <th style="padding: 12px; border: 1px solid rgba(255,255,255,0.1); color: #FF4B4B;">Perplexity Pro Search (Information)</th>
      </tr>
      <tr>
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1); font-weight: 600;">Performance Measure (P)</td>
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1);">SWE-bench score, compile success, code correctness, step efficiency.</td>
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1);">Factuality, minimized hallucinations, citation depth, user-latency.</td>
      </tr>
      <tr style="background-color: rgba(255,255,255,0.02);">
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1); font-weight: 600;">Environment (E)</td>
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1);">Isolated Linux OS container, dependency workspace, local git records.</td>
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1);">Public Web Index, active crawl domains, user current session history.</td>
      </tr>
      <tr>
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1); font-weight: 600;">Actuators (A)</td>
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1);">Bash CLI inputs, file system editor patches, browser automation actions.</td>
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1);">Multi-hop routing queries, html scraper scrapers, citation assembler.</td>
      </tr>
      <tr style="background-color: rgba(255,255,255,0.02);">
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1); font-weight: 600;">Sensors (S)</td>
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1);">Bash console outputs (stdout/stderr), compiler exit codes, DOM/screenshots.</td>
        <td style="padding: 12px; border: 1px solid rgba(255,255,255,0.1);">Search API search lists, web response packets, user feedback selections.</td>
      </tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.caption("Detailed architectural specifications can be accessed in [assignment_1_report.md](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/assignment_1_report.md).")

# ----------------- PAGE 2: DEVIN TASK AGENT SIMULATION -----------------

elif nav_selection == "💻 Devin Task Agent":
    st.markdown('<div class="title-gradient">Devin Task Sandbox</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Interactive Simulation of Devin\'s ReAct Loop & Autonomous Error Self-Correction</div>', unsafe_allow_html=True)
    
    with st.expander("📖 User Guide: Sandbox Simulator Controls", expanded=False):
        st.markdown("""
        ### 💡 Key Concepts
        * **ReAct Loop**: Iterative execution of *Thought*, *Action*, and *Observation*.
        * **Self-Correction**: The agent catches run-time bugs (e.g. missing files, type mismatch) and dynamically modifies its plan DAG.
        ### 🛠️ Step-by-Step Instructions
        1. **Select a Scenario** from the drop-down (e.g. *Flask Web Deployment*, *SQLite Database*, *Pandas Pipeline*).
        2. Click **Advance Loop Cycle ➡️** to step through. Watch the checklist status, bash console logs, and Mock IDE code buffer update dynamically.
        3. Click **Reset Container 🔄** to clear the sandbox state.
        """)
        
    # Scenario Selector
    devin_case_select = st.selectbox(
        "Select Sandbox Scenario:",
        ["Flask Web Deployment", "Database Migration (SQLite)", "Data Pipeline (Pandas)"],
        key="devin_case_select_box"
    )
    
    # Reset helper
    def devin_reset():
        case = st.session_state.current_devin_case
        st.session_state.devin_step = 0
        st.session_state.devin_logs = ["System initialized. Awaiting task initiation..."]
        st.session_state.devin_code = ""
        st.session_state.devin_insights = []
        
        if case == "Flask Web Deployment":
            st.session_state.devin_plan = [
                {"id": 1, "task": "Create app.py and write basic Flask server code", "status": "pending"},
                {"id": 2, "task": "Verify code by running the Flask server", "status": "pending"},
                {"id": 3, "task": "Verify route / returns success code", "status": "pending"}
            ]
        elif case == "Database Migration (SQLite)":
            st.session_state.devin_plan = [
                {"id": 1, "task": "Create db.py to connect and query SQLite database", "status": "pending"},
                {"id": 2, "task": "Verify database query by executing the script", "status": "pending"},
                {"id": 3, "task": "Verify user records count matches expected target", "status": "pending"}
            ]
        elif case == "Data Pipeline (Pandas)":
            st.session_state.devin_plan = [
                {"id": 1, "task": "Create pipeline.py to read and clean employees dataset", "status": "pending"},
                {"id": 2, "task": "Verify processing by executing the pipeline script", "status": "pending"},
                {"id": 3, "task": "Verify average salary statistics match expected values", "status": "pending"}
            ]
            
    # Trigger reset if case changed
    if 'current_devin_case' not in st.session_state or st.session_state.current_devin_case != devin_case_select:
        st.session_state.current_devin_case = devin_case_select
        devin_reset()
        
    def devin_next_cycle():
        step = st.session_state.devin_step + 1
        st.session_state.devin_step = step
        case = st.session_state.current_devin_case
        
        if case == "Flask Web Deployment":
            # Cycle 1: Create File
            if step == 1:
                st.session_state.devin_plan[0]["status"] = "completed"
                st.session_state.devin_code = """import flask
app = flask.Flask(__name__)

@app.route('/')
def index()
    return 'Hello from Devin Sandbox!'

if __name__ == '__main__':
    app.run()"""
                st.session_state.devin_logs.append("[Reasoning] Current focal task is Task 1: Create app.py.\n[Action] Creating flask web app and injecting code with intent-based syntax error to verify safety checks...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ echo '...' > app.py\n[Observation] Bash Code 0: Successfully wrote to file.")
                
            # Cycle 2: Attempt Python execution (throws ModuleNotFoundError)
            elif step == 2:
                st.session_state.devin_logs.append("[Reasoning] Task 1 done. Commencing Task 2: Verify code inside container.\n[Action] Launching Python execution runtime...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ python app.py\n[Observation] Bash Code 1: ERROR DETECTED.\n\nTraceback (most recent call last):\n  File \"app.py\", line 1, in <module>\n    import flask\nModuleNotFoundError: No module named 'flask'")
                st.session_state.devin_logs.append("[Self-Correction] Critical module 'flask' is missing in environment.")
                st.session_state.devin_logs.append("[Planning Router] Inserting dynamic sub-task 'Task 1.5: Install Flask' into plan DAG.")
                st.session_state.devin_plan.insert(1, {"id": 1.5, "task": "Install missing package 'flask' via pip", "status": "pending"})
                st.session_state.devin_insights.append("Insight: Flask was absent in baseline sandbox container. Formulated package insertion task.")

            # Cycle 3: Install Package
            elif step == 3:
                st.session_state.devin_plan[1]["status"] = "completed"
                st.session_state.devin_logs.append("[Reasoning] Focal sub-task is Task 1.5: Install missing packages.\n[Action] Invoking package manager actuator...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ pip install flask\n[Observation] Bash Code 0: Collection download complete.\nSuccessfully installed flask-3.0.2")

            # Cycle 4: Re-attempt Python (throws SyntaxError)
            elif step == 4:
                st.session_state.devin_logs.append("[Reasoning] Resuming Task 2: Verify app compiled in container.\n[Action] Invoking Python runtime executor...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ python app.py\n[Observation] Bash Code 1: COMPILATION FAILED.\n\n  File \"app.py\", line 4\n    def index()\n               ^\nSyntaxError: expected ':'")
                st.session_state.devin_logs.append("[Self-Correction] Syntax defect detected: missed colon in function declaration at line 4.")
                st.session_state.devin_logs.append("[Planning Router] Inserting dynamic correction sub-task 'Task 1.8: Fix Syntax Error' into plan DAG.")
                st.session_state.devin_plan.insert(2, {"id": 1.8, "task": "Fix syntax error in app.py (add missing colon after function declaration)", "status": "pending"})
                st.session_state.devin_insights.append("Insight: Syntax compiler check failed (def index() missing colon). Formulated codebase patching.")

            # Cycle 5: Patch Code
            elif step == 5:
                st.session_state.devin_plan[2]["status"] = "completed"
                st.session_state.devin_code = """import flask
app = flask.Flask(__name__)

@app.route('/')
def index():
    return 'Hello from Devin Sandbox!'

if __name__ == '__main__':
    app.run()"""
                st.session_state.devin_logs.append("[Reasoning] Focal task is Task 1.8: Fix syntax error.\n[Action] Patching app.py to append missing colon...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ echo '...' > app.py\n[Observation] Bash Code 0: Patch delta successfully committed.")

            # Cycle 6: Re-run app (Success)
            elif step == 6:
                st.session_state.devin_plan[3]["status"] = "completed"
                st.session_state.devin_logs.append("[Reasoning] Re-evaluating Task 2: Verify app compiler state.\n[Action] Running Python server thread...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ python app.py\n[Observation] Bash Code 0: Server thread launched successfully.\n* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)")

            # Cycle 7: Verify Route (Finish)
            elif step == 7:
                st.session_state.devin_plan[4]["status"] = "completed"
                st.session_state.devin_logs.append("[Reasoning] Task 2 completed. Initiating Task 3: Verify server response.\n[Action] Triggering Chromium visual/http parser to crawl http://127.0.0.1:5000/...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ curl -i http://127.0.0.1:5000/\n[Observation] Bash Code 0: Response code retrieved.\nHTTP/1.1 200 OK\nContent-Type: text/html\n\nHello from Devin Sandbox!")
                st.session_state.devin_logs.append("[SUCCESS] All architectural goals achieved! Shutting down server thread...")

        elif case == "Database Migration (SQLite)":
            # Cycle 1: Create File
            if step == 1:
                st.session_state.devin_plan[0]["status"] = "completed"
                st.session_state.devin_code = """import sqlite3
conn = sqlite3.connect('test.db')
cursor = conn.cursor()
# Syntax error near FROM
cursor.execute("SELECT * FROM FROM users")
print("Users queried successfully")"""
                st.session_state.devin_logs.append("[Reasoning] Current focal task is Task 1: Create db.py.\n[Action] Creating SQLite database connect script and inserting code with syntax error...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ echo '...' > db.py\n[Observation] Bash Code 0: Successfully wrote to file.")
                
            # Cycle 2: Attempt Python execution (throws no such table: users)
            elif step == 2:
                st.session_state.devin_logs.append("[Reasoning] Task 1 done. Commencing Task 2: Verify database schema.\n[Action] Executing script...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ python db.py\n[Observation] Bash Code 1: ERROR DETECTED.\n\nsqlite3.OperationalError: no such table: users")
                st.session_state.devin_logs.append("[Self-Correction] Database table 'users' does not exist in context.")
                st.session_state.devin_logs.append("[Planning Router] Inserting dynamic sub-task 'Task 1.5: Create schema table' into plan DAG.")
                st.session_state.devin_plan.insert(1, {"id": 1.5, "task": "Create database table schema for users table", "status": "pending"})
                st.session_state.devin_insights.append("Insight: SQLite table 'users' was missing. Formulated migration script.")

            # Cycle 3: Run Database migration
            elif step == 3:
                st.session_state.devin_plan[1]["status"] = "completed"
                st.session_state.devin_logs.append("[Reasoning] Focal sub-task is Task 1.5: Create schema table.\n[Action] Patching database connection code to create schema...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ python -c 'import sqlite3; conn=sqlite3.connect(\"test.db\"); conn.cursor().execute(\"CREATE TABLE users (id int, name text, active int)\"); conn.commit()'\n[Observation] Bash Code 0: Migration commit successful.")

            # Cycle 4: Re-attempt Python (throws SELECT * FROM FROM users syntax error)
            elif step == 4:
                st.session_state.devin_logs.append("[Reasoning] Resuming Task 2: Verify script queries database.\n[Action] Launching script execution...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ python db.py\n[Observation] Bash Code 1: SQL EXCEPTION.\n\nsqlite3.OperationalError: near \"FROM\": syntax error")
                st.session_state.devin_logs.append("[Self-Correction] SQL syntax error found: repeated 'FROM' keyword.")
                st.session_state.devin_logs.append("[Planning Router] Inserting dynamic correction sub-task 'Task 1.8: Fix SQL query syntax' into plan DAG.")
                st.session_state.devin_plan.insert(2, {"id": 1.8, "task": "Fix SQL query syntax in db.py (remove duplicate FROM keyword)", "status": "pending"})
                st.session_state.devin_insights.append("Insight: Found SQL syntax bug (SELECT * FROM FROM users). Formulated query patching.")

            # Cycle 5: Patch SQL query
            elif step == 5:
                st.session_state.devin_plan[2]["status"] = "completed"
                st.session_state.devin_code = """import sqlite3
conn = sqlite3.connect('test.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, active INTEGER)")
cursor.execute("INSERT INTO users VALUES (1, 'Alice', 1), (2, 'Bob', 1)")
conn.commit()
cursor.execute("SELECT * FROM users")
print("Query output:", cursor.fetchall())"""
                st.session_state.devin_logs.append("[Reasoning] Focal task is Task 1.8: Fix SQL query syntax.\n[Action] Rewriting query select command to correct format...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ echo '...' > db.py\n[Observation] Bash Code 0: Query patch successfully committed.")

            # Cycle 6: Re-run script (Success)
            elif step == 6:
                st.session_state.devin_plan[3]["status"] = "completed"
                st.session_state.devin_logs.append("[Reasoning] Re-evaluating Task 2: Verify db.py connection outputs.\n[Action] Invoking Python executor...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ python db.py\n[Observation] Bash Code 0: Script executed successfully.\nQuery output: [(1, 'Alice', 1), (2, 'Bob', 1)]")

            # Cycle 7: Verify User Records (Finish)
            elif step == 7:
                st.session_state.devin_plan[4]["status"] = "completed"
                st.session_state.devin_logs.append("[Reasoning] Task 2 completed. Commencing Task 3: Verify records match targets.\n[Action] Aggregating queried array length...")
                st.session_state.devin_logs.append("[Observation] Count matches target: 2 user records successfully found in test.db.")
                st.session_state.devin_logs.append("[SUCCESS] SQLite database setup and query validation completed successfully.")

        elif case == "Data Pipeline (Pandas)":
            # Cycle 1: Create File
            if step == 1:
                st.session_state.devin_plan[0]["status"] = "completed"
                st.session_state.devin_code = """# read employees.csv
with open('employees.csv', 'r') as f:
    data = f.read()
# type addition error
val = data.split('\\n')[1].split(',')[1] + 1000
print('Salary calculated:', val)"""
                st.session_state.devin_logs.append("[Reasoning] Current focal task is Task 1: Create pipeline.py.\n[Action] Creating data cleaning script and reading employees dataset...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ echo '...' > pipeline.py\n[Observation] Bash Code 0: Successfully wrote to file.")
                
            # Cycle 2: Attempt Python execution (throws FileNotFoundError)
            elif step == 2:
                st.session_state.devin_logs.append("[Reasoning] Task 1 done. Commencing Task 2: Verify data cleaning run.\n[Action] Executing script...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ python pipeline.py\n[Observation] Bash Code 1: ERROR DETECTED.\n\nFileNotFoundError: [Errno 2] No such file or directory: 'employees.csv'")
                st.session_state.devin_logs.append("[Self-Correction] Missing input dataset 'employees.csv'.")
                st.session_state.devin_logs.append("[Planning Router] Inserting dynamic sub-task 'Task 1.5: Generate mock employees.csv' into plan DAG.")
                st.session_state.devin_plan.insert(1, {"id": 1.5, "task": "Create mock employees.csv dataset file", "status": "pending"})
                st.session_state.devin_insights.append("Insight: Employees CSV was absent in working folder. Formulated mock data creation.")

            # Cycle 3: Generate CSV data
            elif step == 3:
                st.session_state.devin_plan[1]["status"] = "completed"
                st.session_state.devin_logs.append("[Reasoning] Focal sub-task is Task 1.5: Create mock employees.csv.\n[Action] Creating CSV text representation...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ echo -e 'name,salary\\nAlice,5000\\nBob,6000' > employees.csv\n[Observation] Bash Code 0: CSV file generated successfully.")

            # Cycle 4: Re-attempt Python (throws TypeError)
            elif step == 4:
                st.session_state.devin_logs.append("[Reasoning] Resuming Task 2: Verify processing engine compiles.\n[Action] Running Python script...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ python pipeline.py\n[Observation] Bash Code 1: TYPE EXCEPTION.\n\nTypeError: can only concatenate str (not \"int\") to str")
                st.session_state.devin_logs.append("[Self-Correction] Script failed because salary was read as string, not parsed as int.")
                st.session_state.devin_logs.append("[Planning Router] Inserting dynamic correction sub-task 'Task 1.8: Fix salary type casting' into plan DAG.")
                st.session_state.devin_plan.insert(2, {"id": 1.8, "task": "Fix salary calculation type casting in pipeline.py (cast string column to integer)", "status": "pending"})
                st.session_state.devin_insights.append("Insight: Type mismatch bug found. Implementing type conversion casting.")

            # Cycle 5: Patch Pipeline code
            elif step == 5:
                st.session_state.devin_plan[2]["status"] = "completed"
                st.session_state.devin_code = """with open('employees.csv', 'r') as f:
    lines = f.readlines()
salaries = [int(line.split(',')[1]) for line in lines[1:] if line.strip()]
avg = sum(salaries) / len(salaries)
print("Average Salary calculated:", avg)"""
                st.session_state.devin_logs.append("[Reasoning] Focal task is Task 1.8: Fix salary type casting.\n[Action] Injecting integer type conversions into calculations...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ echo '...' > pipeline.py\n[Observation] Bash Code 0: Type delta successfully committed.")

            # Cycle 6: Re-run script (Success)
            elif step == 6:
                st.session_state.devin_plan[3]["status"] = "completed"
                st.session_state.devin_logs.append("[Reasoning] Re-evaluating Task 2: Verify data pipeline output results.\n[Action] Running Python executor...")
                st.session_state.devin_logs.append("Executing Sandbox CLI:\n$ python pipeline.py\n[Observation] Bash Code 0: Script executed successfully.\nAverage Salary calculated: 5500.0")

            # Cycle 7: Verify output stats (Finish)
            elif step == 7:
                st.session_state.devin_plan[4]["status"] = "completed"
                st.session_state.devin_logs.append("[Reasoning] Task 2 completed. Commencing Task 3: Verify calculated statistics.\n[Action] Extracting Average Salary output...")
                st.session_state.devin_logs.append("[Observation] Average Salary matches target check: 5500.0.")
                st.session_state.devin_logs.append("[SUCCESS] Employee data cleaning pipeline executed successfully.")
            
    # Layout columns
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("📋 Devin checklist")
        # Render plan checkbox checklist dynamically
        for t in st.session_state.devin_plan:
            icon = "⚪" if t["status"] == "pending" else "🟢"
            st.markdown(f"**{icon} Task {t['id']}**: {t['task']}")
            
        st.divider()
        st.subheader("🕹️ Simulation Controls")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.session_state.devin_step < 7:
                st.button("Advance Loop Cycle ➡️", on_click=devin_next_cycle, use_container_width=True)
            else:
                st.button("Advance Loop Cycle ➡️", disabled=True, use_container_width=True)
        with col_btn2:
            st.button("Reset Container 🔄", on_click=devin_reset, use_container_width=True)
            
        if st.session_state.devin_step == 0:
            st.caption("Click 'Advance Loop Cycle' to begin the ReAct sandbox compilation simulation.")
        elif st.session_state.devin_step >= 7:
            st.success("🎉 Simulation Finished! Devin successfully deployed and patched the system.")
            
        # Insights
        if st.session_state.devin_insights:
            st.subheader("💡 Retained Epistemic Insights")
            for ins in st.session_state.devin_insights:
                st.info(ins)
                
    with col_right:
        st.subheader("🖥️ Isolated Sandbox Workspace")
        
        # Render Terminal Console
        terminal_txt = "\n".join(st.session_state.devin_logs)
        st.markdown("**Bash Console (stdout/stderr)**")
        st.markdown(f'<div class="terminal-console">{terminal_txt}</div>', unsafe_allow_html=True)
        
        # Render IDE Editor
        ide_filename = "app.py"
        if st.session_state.current_devin_case == "Database Migration (SQLite)":
            ide_filename = "db.py"
        elif st.session_state.current_devin_case == "Data Pipeline (Pandas)":
            ide_filename = "pipeline.py"
            
        st.markdown(f"**Mock Editor IDE (`{ide_filename}`)**")
        code_text = st.session_state.devin_code if st.session_state.devin_code else "# Editor buffer is empty"
        st.code(code_text, language="python")

elif nav_selection == "🔍 Perplexity Search Agent":
    st.markdown('<div class="title-gradient">Perplexity Pro Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Interactive Simulation of Parallel Search, HTML Scraping, Information-Gap Detection, and Source Citation Synthesizer</div>', unsafe_allow_html=True)
    
    with st.expander("📖 User Guide: Multi-Hop Search Walkthrough", expanded=False):
        st.markdown("""
        ### 💡 Key Concepts
        * **Semantic Parsing**: Decomposing a complex user query into independent sub-problems.
        * **Gap Detection**: Evaluating whether primary crawl results contain all necessary details, and triggering secondary searches if needed.
        ### 🛠️ Step-by-Step Instructions
        1. **Type a Question** in the search field (e.g. the default piracy question or Oscar wins question).
        2. Click **Start Pro Search 🚀** to parse the semantic intent.
        3. Step through using **Advance Search Step ➡️** or complete instantly using **Instant Resolve ⚡**.
        4. Review the final response with cited numbers, the clickable visited sources, and the cached memory drawer.
        """)
    
    # Perplexity Reset
    def perp_reset():
        st.session_state.perp_step = 0
        st.session_state.perp_logs = ["System initialized. Awaiting search query initiation..."]
        st.session_state.perp_episodic_memory = {}
        st.session_state.perp_citations = []
        st.session_state.perp_gap_detected = False
        st.session_state.perp_answer = ""
        st.session_state.perp_query = ""
        if 'last_perp_query' in st.session_state:
            st.session_state.last_perp_query = ""

    # UI Query Search Action
    query_input = st.text_input(
        "Ask a complex, multi-hop question:",
        value="what is the best solution for piracy and its technical importance?",
        placeholder="Type search topic..."
    )
    
    # Auto-reset if query changes
    if 'last_perp_query' not in st.session_state:
        st.session_state.last_perp_query = ""
    if query_input != st.session_state.last_perp_query:
        st.session_state.last_perp_query = query_input
        st.session_state.perp_step = 0
        st.session_state.perp_logs = ["System initialized. Awaiting search query initiation..."]
        st.session_state.perp_episodic_memory = {}
        st.session_state.perp_citations = []
        st.session_state.perp_gap_detected = False
        st.session_state.perp_answer = ""
        st.session_state.perp_query = query_input

    def perp_next_step():
        step = st.session_state.perp_step + 1
        st.session_state.perp_step = step
        
        # Capture the query to ensure stability during step-through
        if step == 1:
            st.session_state.perp_query = query_input
            
        query = st.session_state.perp_query
        query_clean = query.lower().strip()
        
        # Determine Scenario
        if "oscar" in query_clean or "dune" in query_clean:
            scenario = "oscars"
        elif "piracy" in query_clean or "solution" in query_clean:
            scenario = "piracy"
        else:
            scenario = "fallback"
            
        # Step 1: Semantic Intent Analysis
        if step == 1:
            st.session_state.perp_logs = ["🔍 **Step 1: Semantic Intent Analysis**"]
            if scenario == "oscars":
                st.session_state.perp_logs.append("Decomposing complex query into sub-problems:\n- Sub-problem 1: Find the movie with the most Oscar wins in 2026.\n- Sub-problem 2: Find the budget of that specific Oscar winner.\nReasoning: Sub-problem 2 depends on the output of Sub-problem 1. Formulating sequential multi-hop search plan.")
                st.session_state.perp_logs.append("Query formulation: stage 1 target term is `'2026 Oscar winners'`.")
            elif scenario == "piracy":
                st.session_state.perp_logs.append("Decomposing complex query into sub-problems:\n- Sub-problem 1: Identify key technical solutions for software/media piracy.\n- Sub-problem 2: Determine the technical importance of the best solution.\nReasoning: Identifying the 'best' solution requires establishing overview categories, then querying why its hardware enclaves are important. Formulating multi-hop search plan.")
                st.session_state.perp_logs.append("Query formulation: stage 1 target term is `'piracy solutions'`.")
            else:
                keywords = [w for w in re.sub(r'[^a-zA-Z0-9 ]', '', query).split() if len(w) > 3]
                kw1 = keywords[0] if len(keywords) > 0 else "technology"
                kw2 = keywords[1] if len(keywords) > 1 else "implementation"
                st.session_state.perp_logs.append(f"Decomposing complex query into sub-problems:\n- Sub-problem 1: Search overview facts for '{query}'.\n- Sub-problem 2: Identify structural importance of '{kw1}'.\nReasoning: Decomposing keyword concepts to build plan.")
                st.session_state.perp_logs.append(f"Query formulation: stage 1 target term is `'{kw1}'`.")
                
        # Step 2: Actuating Primary Search & Web Crawling
        elif step == 2:
            st.session_state.perp_logs.append("\n🌎 **Step 2: Actuating Primary Search & Web Crawling**")
            st.session_state.perp_logs.append("Launching parallel search engine index queries...")
            if scenario == "oscars":
                results = WEB_INDEX["2026 Oscar winners"]
                st.session_state.perp_logs.append(f"Search engines returned {len(results)} matches. Crawling URL payloads:\n")
                for res in results:
                    st.session_state.perp_logs.append(f"Visited URL: {res['url']} (Scraped title: \"{res['title']}\")")
                    st.session_state.perp_episodic_memory[res["url"]] = res["content"]
                    st.session_state.perp_citations.append(res["url"])
            elif scenario == "piracy":
                results = WEB_INDEX["piracy solutions"]
                st.session_state.perp_logs.append(f"Search engines returned {len(results)} matches. Crawling URL payloads:\n")
                for res in results:
                    st.session_state.perp_logs.append(f"Visited URL: {res['url']} (Scraped title: \"{res['title']}\")")
                    st.session_state.perp_episodic_memory[res["url"]] = res["content"]
                    st.session_state.perp_citations.append(res["url"])
            else:
                keywords = [w for w in re.sub(r'[^a-zA-Z0-9 ]', '', query).split() if len(w) > 3]
                kw1 = keywords[0] if len(keywords) > 0 else "technology"
                kw2 = keywords[1] if len(keywords) > 1 else "implementation"
                url1 = f"https://tech-portal.org/search?q={kw1}"
                url2 = f"https://encyclopedia-online.net/wiki/{kw2}"
                st.session_state.perp_logs.append("Search engines returned 2 matches. Crawling URL payloads:\n")
                st.session_state.perp_logs.append(f"Visited URL: {url1} (Scraped title: \"Overview of {kw1.capitalize()} and {kw2.capitalize()}\")")
                st.session_state.perp_logs.append(f"Visited URL: {url2} (Scraped title: \"Semantic details for {query[:20]}...\")")
                st.session_state.perp_episodic_memory[url1] = f"This reference provides general context on {kw1} systems. It details how they integrate into user environments."
                st.session_state.perp_episodic_memory[url2] = f"This document covers the functional implementation of {kw2} systems and their common architecture."
                st.session_state.perp_citations.append(url1)
                st.session_state.perp_citations.append(url2)

        # Step 3: Reasoning & Knowledge Synthesis
        elif step == 3:
            st.session_state.perp_logs.append("\n🧠 **Step 3: Reasoning & Knowledge Synthesis**")
            if scenario == "oscars":
                st.session_state.perp_logs.append("Extracted fact: Dune: Part Three won 6 Oscars (most awards of the evening).")
                st.session_state.perp_logs.append("Evaluating data completeness:\n\nOscar Winner: FOUND (Dune: Part Three)\nBudget: MISSING (No budget metrics present in Variety or Hollywood Reporter contents).")
                st.session_state.perp_logs.append("🚩 [Gap Detected] Secondary search query triggered: Dune: Part Three movie budget")
                st.session_state.perp_gap_detected = True
            elif scenario == "piracy":
                st.session_state.perp_logs.append("Extracted fact: Hardware-backed DRM (Widevine L1) is identified as the most secure anti-piracy solution.")
                st.session_state.perp_logs.append("Evaluating data completeness:\n\nBest Solution: FOUND (Widevine L1 enclaves)\nTechnical Importance Details: MISSING (Need detailed cryptographic isolation logic).")
                st.session_state.perp_logs.append("🚩 [Gap Detected] Secondary search query triggered: technical importance of secure enclaves")
                st.session_state.perp_gap_detected = True
            else:
                keywords = [w for w in re.sub(r'[^a-zA-Z0-9 ]', '', query).split() if len(w) > 3]
                kw1 = keywords[0] if len(keywords) > 0 else "technology"
                st.session_state.perp_logs.append("Evaluating data completeness:\n\nTopic overview: FOUND\nPractical engineering implications: MISSING.")
                st.session_state.perp_logs.append(f"🚩 [Gap Detected] Secondary search query triggered: {kw1} technical engineering implications")
                st.session_state.perp_gap_detected = True

        # Step 4: Actuating Secondary Search & Web Crawling
        elif step == 4:
            st.session_state.perp_logs.append("\n🌎 **Step 4: Actuating Secondary Search & Web Crawling**")
            if scenario == "oscars":
                sec_results = WEB_INDEX["Dune: Part Three movie budget"]
                st.session_state.perp_logs.append(f"Crawl database returned {len(sec_results)} secondary matches. Fetching full HTML pages:\n")
                for res in sec_results:
                    st.session_state.perp_logs.append(f"Visited URL: {res['url']} (Scraped title: \"{res['title']}\")")
                    st.session_state.perp_episodic_memory[res["url"]] = res["content"]
                    st.session_state.perp_citations.append(res["url"])
            elif scenario == "piracy":
                sec_results = WEB_INDEX["technical importance of secure enclaves"]
                st.session_state.perp_logs.append(f"Crawl database returned {len(sec_results)} secondary matches. Fetching full HTML pages:\n")
                for res in sec_results:
                    st.session_state.perp_logs.append(f"Visited URL: {res['url']} (Scraped title: \"{res['title']}\")")
                    st.session_state.perp_episodic_memory[res["url"]] = res["content"]
                    st.session_state.perp_citations.append(res["url"])
            else:
                keywords = [w for w in re.sub(r'[^a-zA-Z0-9 ]', '', query).split() if len(w) > 3]
                kw1 = keywords[0] if len(keywords) > 0 else "technology"
                url3 = f"https://tech-reviewer.com/articles/{kw1}-impact"
                st.session_state.perp_logs.append("Crawl database returned 1 secondary match. Fetching HTML page:")
                st.session_state.perp_logs.append(f"Visited URL: {url3} (Scraped title: \"Analysis of {kw1.capitalize()} Systems\")")
                st.session_state.perp_episodic_memory[url3] = f"Analyzing the engineering impact of {kw1} models. The technical importance resides in its modular flexibility and real-time execution speeds."
                st.session_state.perp_citations.append(url3)

        # Step 5: Final Joint Analysis & Citation Synthesis
        elif step == 5:
            st.session_state.perp_logs.append("\n🧠 **Step 5: Final Joint Analysis & Citation Synthesis**")
            st.session_state.perp_logs.append("Joint correlation completed. Formatting output citing all crawled references...")
            if scenario == "oscars":
                st.session_state.perp_answer = """At the 98th Academy Awards in 2026, the movie that won the most Oscars was **Dune: Part Three**, taking home a total of **6 Oscars** including Best Director for Denis Villeneuve and sweeping the technical categories [1][2].
The production budget for Dune: Part Three was approximately **190 million USD** [3][4], which was co-financed by Legendary Pictures and Warner Bros. The film proved to be a major financial success, grossing over 720 million worldwide [3]."""
            elif scenario == "piracy":
                st.session_state.perp_answer = """The best modern technical solution for preventing software and media piracy is **hardware-rooted DRM (such as Google Widevine L1)** combined with secure enclaves [1][2].

The **technical importance** of this solution lies in its hardware-enforced isolation:
1. **Isolated Cryptographic Registers**: The decryption keys and processes are executed inside isolated CPU enclaves, separating them entirely from the host operating system [3][4].
2. **Preventing Memory Exploits**: Because the decryption happens at the hardware layer, OS-level debuggers, kernel hooks, or system memory dumps cannot read the raw cryptographic keys [3].
3. **Untrusted Host Protection**: Even if the client device's operating system is completely compromised, the digital assets remain secure within the hardware trust boundary [4]."""
            else:
                keywords = [w for w in re.sub(r'[^a-zA-Z0-9 ]', '', query).split() if len(w) > 3]
                kw1 = keywords[0] if len(keywords) > 0 else "technology"
                st.session_state.perp_answer = f"""Regarding your query **\"{query}\"**, the research synthesizes the following findings:

1. **Core Overview**: The architecture of **{kw1.capitalize()}** provides the fundamental framework for modern systems [1]. Its integration focuses on modular configurations to scale [2].
2. **Technical Importance**: The main engineering importance resides in its **modular flexibility** and **real-time execution speeds** [3]. By decoupling parameters, it prevents state lock issues and allows systems to scale independently [3]."""

    def perp_instant_resolve():
        while st.session_state.perp_step < 5:
            perp_next_step()

    # Layout controls
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.session_state.perp_step == 0:
            st.button("Start Pro Search 🚀", on_click=perp_next_step, use_container_width=True)
        elif st.session_state.perp_step < 5:
            st.button("Advance Search Step ➡️", on_click=perp_next_step, use_container_width=True)
        else:
            st.button("Search Complete ✅", disabled=True, use_container_width=True)
    with col_btn2:
        if st.session_state.perp_step > 0 and st.session_state.perp_step < 5:
            st.button("Instant Resolve ⚡", on_click=perp_instant_resolve, use_container_width=True)
        else:
            st.button("Instant Resolve ⚡", disabled=True, use_container_width=True)
    with col_btn3:
        st.button("Reset Simulator 🔄", on_click=perp_reset, use_container_width=True)
        
    if st.session_state.perp_step == 0:
        st.caption("Click 'Start Pro Search 🚀' to begin the step-by-step multi-hop search simulation.")
    elif st.session_state.perp_step >= 5:
        st.success("🎉 Search complete! Output synthesized using cross-reference citations.")

    # Display results UI
    col_logs, col_synth = st.columns([1, 1])
    
    with col_logs:
        st.subheader("⚙️ Pro Search Execution Trace")
        logs_txt = "\n".join(st.session_state.perp_logs)
        st.markdown(f'<div class="terminal-console" style="height: 480px;">{logs_txt}</div>', unsafe_allow_html=True)
        
    with col_synth:
        st.subheader("✨ Synthesized Search Response")
        if st.session_state.perp_step >= 5:
            st.markdown(f'<div class="card" style="min-height: 250px;">{st.session_state.perp_answer}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="card" style="min-height: 250px; color: #718096; display: flex; align-items: center; justify-content: center;">Awaiting synthesis completion... (Step {st.session_state.perp_step}/5)</div>', unsafe_allow_html=True)
        
        st.subheader("🔗 Visited Sources")
        if st.session_state.perp_citations:
            for i, url in enumerate(st.session_state.perp_citations):
                st.markdown(f"**[{i+1}]** `{url}`")
        else:
            st.caption("No sources visited yet in this cycle.")
            
        # Mock Scraped Snippets Cards
        with st.expander("📂 Cached Web Data in Episodic Memory"):
            if st.session_state.perp_episodic_memory:
                for url, content in st.session_state.perp_episodic_memory.items():
                    st.caption(f"**Source**: {url}")
                    st.write(content)
                    st.divider()
            else:
                st.caption("Episodic memory cache is currently empty.")

# ----------------- PAGE 4: LAB SESSIONS (L1.1 & L1.2) -----------------
elif nav_selection == "🧪 Lab Sessions (L1.1 & L1.2)":
    st.markdown('<div class="title-gradient">Module 1 Lab Sessions</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Interactive Execution & Study of Labs L1.1 (Minimal ReAct Agent) and L1.2 (LangChain vs LlamaIndex)</div>', unsafe_allow_html=True)
    
    with st.expander("📖 User Guide: Interactive Agent Lab Playground", expanded=False):
        st.markdown("""
        ### 💡 Key Concepts
        * **Lab 1.1**: Demonstrates a simple python implementation of the ReAct (Reason + Action) loop using arithmetic and mock web searches.
        * **Lab 1.2**: Focuses on comparing the coding models of LangChain (flow orchestration) versus LlamaIndex (data indexing).
        ### 🛠️ How to Play with Lab 1.1
        1. Input a combined calculation and search task (e.g. `Calculate (45 * 2) - 10 and find the capital of Italy.`).
        2. Click **Run ReAct Loop 🚀** to execute the loop.
        3. View the generated cycle execution logs and final response.
        """)
    
    tab1, tab2 = st.tabs(["🧪 Lab 1.1: Minimal ReAct", "🧪 Lab 1.2: LangChain vs LlamaIndex"])
    
    with tab1:
        st.subheader("L1.1: Minimal ReAct Agent from Scratch")
        st.markdown("""
        This lab demonstrates building a **Reason + Action (ReAct)** loop without any high-level frameworks.
        The agent decomposes tasks, selects tools, and parses outputs iteratively.
        """)
        
        lab_query = st.text_input(
            "Enter ReAct Goal:",
            value="Calculate (45 * 23) + 12 and verify the capital of France.",
            key="lab_1_1_query_input"
        )
        
        if 'lab_logs' not in st.session_state:
            st.session_state.lab_logs = ["Awaiting execution..."]
        if 'lab_ans' not in st.session_state:
            st.session_state.lab_ans = ""
            
        # Helper tools for dynamic ReAct
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

        def math_tool(expression: str) -> str:
            cleaned_expr = re.sub(r'[^0-9\+\-\*\/\(\)\. ]', '', expression)
            try:
                result = eval(cleaned_expr, {"__builtins__": None}, {})
                return str(result)
            except Exception as e:
                return f"Error evaluating math expression: {e}"

        def search_tool(q_str: str) -> str:
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
            q_clean = q_str.lower().strip()
            for key in db:
                if key in q_clean or q_clean in key:
                    return db[key]
            return f"{q_str.capitalize()} info retrieved (mock database result)."

        col_run_lab, col_reset_lab = st.columns([1, 4])
        with col_run_lab:
            if st.button("Run ReAct Loop 🚀", key="btn_run_lab_1_1"):
                query = lab_query
                math_expr = extract_math_expr(query)
                search_q = extract_search_query(query)
                
                st.session_state.lab_logs = [f"[ReAct Agent Initialized] Goal: {query}"]
                
                # Cycle 1
                st.session_state.lab_logs.append("\n--- CYCLE 1 ---")
                if math_expr:
                    st.session_state.lab_logs.append(f"[Thought] I need to calculate the mathematical expression: {math_expr}. I will call the Math tool.")
                    st.session_state.lab_logs.append(f"[Action] Math[{math_expr}]")
                    math_res = math_tool(math_expr)
                    st.session_state.lab_logs.append(f"[Observation] {math_res}")
                else:
                    st.session_state.lab_logs.append("[Thought] No mathematical expression detected. Proceeding to search queries.")
                    math_res = "N/A"
                    
                # Cycle 2
                st.session_state.lab_logs.append("\n--- CYCLE 2 ---")
                if search_q:
                    thought_str = f"[Thought] "
                    if math_expr:
                        thought_str += f"The calculation output is {math_res}. "
                    thought_str += f"Now I need to verify the info for '{search_q}'. I should use the Search tool."
                    st.session_state.lab_logs.append(thought_str)
                    st.session_state.lab_logs.append(f"[Action] Search[{search_q}]")
                    search_res = search_tool(search_q)
                    st.session_state.lab_logs.append(f"[Observation] {search_res}")
                else:
                    st.session_state.lab_logs.append("[Thought] No search queries detected. Wrapping up task.")
                    search_res = "N/A"
                    
                # Cycle 3
                st.session_state.lab_logs.append("\n--- CYCLE 3 ---")
                st.session_state.lab_logs.append("[Thought] I have completed the tool executions and gathered the required observations. Ready to synthesize the final answer.")
                
                final_ans = ""
                if math_expr and math_res != "N/A" and not math_res.startswith("Error"):
                    final_ans += f"The mathematical calculation yields {math_res}. "
                if search_q and search_res != "N/A":
                    final_ans += f"{search_res}"
                if not final_ans:
                    final_ans = "Task completed successfully with no additional actions."
                    
                st.session_state.lab_logs.append(f"[Final Answer] {final_ans}")
                st.session_state.lab_ans = final_ans
                
        with col_reset_lab:
            if st.button("Clear Logs 🔄", key="btn_reset_lab_1_1"):
                st.session_state.lab_logs = ["Awaiting execution..."]
                st.session_state.lab_ans = ""
                
        col_term, col_ans = st.columns([2, 1])
        with col_term:
            st.markdown("**Interactive Terminal Logs**")
            log_text = "\n".join(st.session_state.lab_logs)
            st.markdown(f'<div class="terminal-console" style="height: 300px;">{log_text}</div>', unsafe_allow_html=True)
            
        with col_ans:
            st.markdown("**Synthesized Answer**")
            ans_box = st.session_state.lab_ans if st.session_state.lab_ans else "Awaiting agent execution..."
            st.markdown(f'<div class="card" style="min-height: 120px;">{ans_box}</div>', unsafe_allow_html=True)
            
    with tab2:
        st.subheader("L1.2: LangChain vs LlamaIndex Comparison")
        st.markdown("""
        Compare the developer experience and system architectures of the two major frameworks.
        """)
        
        col_lc, col_li = st.columns(2)
        with col_lc:
            st.markdown("### 🔗 LangChain Chain Paradigm")
            st.markdown("""
            **Focus**: Prompt templates, explicit chains, and sequential execution.
            """)
            st.code("""
# LangChain LCEL Syntax Example
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

prompt = PromptTemplate.from_template(
    "Suggest a name for a company making {product}"
)
model = ChatOpenAI(model="gpt-4")

chain = prompt | model | StrOutputParser()
response = chain.invoke({"product": "agentic software"})
            """, language="python")
            
            st.info("💡 LangChain is optimized for orchestrating customizable loops, workflows, and multi-agent systems.")
            
        with col_li:
            st.markdown("### 🗂️ LlamaIndex Data Paradigm")
            st.markdown("""
            **Focus**: Vector indices, document chunks, and RAG architectures.
            """)
            st.code("""
# LlamaIndex Indexing Syntax Example
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Ingest and create vector index
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Create query engine and retrieve facts
query_engine = index.as_query_engine()
response = query_engine.query("Explain Devin architecture")
            """, language="python")
            
            st.info("💡 LlamaIndex is optimized for search-augmenting LLMs (RAG) on top of complex structured or unstructured files.")


elif nav_selection == "📖 Workspace Documentation":
    st.markdown('<div class="title-gradient">Workspace Documentation</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Comprehensive study guides, PEAS matrices, system schematics, and test benchmarks.</div>', unsafe_allow_html=True)
    
    doc_tab1, doc_tab2, doc_tab3, doc_tab4 = st.tabs([
        "📄 Coursework Brief", 
        "💻 Devin Test Suite", 
        "🔍 Perplexity Test Suite", 
        "🧪 Lab ReAct Test Suite"
    ])
    
    with doc_tab1:
        st.subheader("📚 Coursework Overview & Brief")
        st.markdown("""
        This interactive workspace consolidates the foundational elements of **Module 1 (Agent Architectures & Design)** and **Module 2 (Reasoning & Tool Use)**. 
        It serves as a visual and functional cognitive simulator comparing closed-loop code synthesis systems with open-world search agents.
        """)
        
        st.subheader("📊 Architecture Comparison & PEAS Rationale")
        st.markdown("""
        The architecture comparison module details two primary paradigms:
        
        1. **Devin (Closed-Loop Coder)**:
           - **Operational Flow**: Reads a coding goal, creates a Directed Acyclic Graph (DAG) plan, executes commands, intercepts compiler error outputs, and self-corrects code files dynamically inside a Docker environment.
           - **Environments**: Highly stateful, local filesystem, write-access command shell.
           - **Actuators**: File editor patcher, bash terminal, browser controller.
           
        2. **Perplexity Pro Search (Information Synthesizer)**:
           - **Operational Flow**: Decomposes a user query, triggers parallel primary crawlers, evaluates data completeness (Gap Check), replans/triggers secondary crawls if facts are missing, and synthesizes a final cited response.
           - **Environments**: Read-only, open web indexes, search API catalogs, session caches.
           - **Actuators**: Multi-hop query router, scraper indexer, citation formatter.
        """)
        
        st.info("💡 Tip: Navigate to the individual workspace pages in the sidebar to run interactive loop cycle simulations for each agent!")

    with doc_tab2:
        st.subheader("💻 Devin Task Agent Test Suite")
        st.markdown("Below are three dynamic benchmark scenarios evaluated inside the isolated Devin Sandbox container.")
        
        # Test Case 1 Table
        st.markdown("### 🟢 Test Case 1: Flask Web Deployment")
        st.markdown("""
| Dimension | Value / Details |
| :--- | :--- |
| **Input Prompt** | Set up a basic Flask server inside `app.py` and verify it running on route `/`. |
| **Expected Outcome** | 1. Write draft Flask server with a syntax error.<br>2. Execute script and catch `ModuleNotFoundError`.<br>3. Install missing package `flask` via pip.<br>4. Catch `SyntaxError` (missing colon).<br>5. Patch code to append colon.<br>6. Start server thread and verify HTTP status 200 via curl check. |
| **Actual / Real Result** | Successfully installed `flask-3.0.2`, identified syntax bug (`def index()`) at cycle 4, applied patch, and curl returned HTTP 200 payload `"Hello from Devin Sandbox!"`. |
| **Technical Rationale** | Demonstrates compiler traceback parsing and dynamic package-manager installation triggers to heal broken runtime environments. |
        """)
        
        st.markdown("**Detailed Cycle Execution Trace & State Mutation**")
        st.markdown("""
| Cycle / Step | Agent Thought & Goal | Actuator Command | Sandbox Observation / Error | Workspace State / Result |
| :--- | :--- | :--- | :--- | :--- |
| **Cycle 1** | Set up flask server, write file `app.py` | `$ echo '...' > app.py` | Bash Code 0: Successfully wrote to file | Writes initial draft containing intent-based syntax error `def index()` (missing colon) |
| **Cycle 2** | Run `app.py` to check baseline compilation | `$ python app.py` | `ModuleNotFoundError: No module named 'flask'` | Code unchanged; flags missing package `flask` |
| **Cycle 3** | Install missing package `flask` using pip actuator | `$ pip install flask` | Successfully installed `flask-3.0.2` | Flask package loaded into container environment |
| **Cycle 4** | Re-verify Flask compilation in container | `$ python app.py` | `SyntaxError: expected ':'` at `def index()` | Code compilation fails; flags missing colon; schedules patch |
| **Cycle 5** | Apply patch to `app.py` adding missing colon | Code editor patch applied | Bash Code 0: Patch successfully committed | Updates function declaration to `def index():` |
| **Cycle 6** | Re-run `app.py` to start server thread | `$ python app.py` | Server thread launched on `http://127.0.0.1:5000/` | Flask server runs in background |
| **Cycle 7** | Check index route response using curl actuator | `$ curl -i http://127.0.0.1:5000/` | `HTTP 200 OK` with `"Hello from Devin Sandbox!"` | Output matches target. Shutdown server. Success! |
""")
        st.divider()

        # Test Case 2 Table
        st.markdown("### 🟢 Test Case 2: Database Migration (SQLite)")
        st.markdown("""
| Dimension | Value / Details |
| :--- | :--- |
| **Input Prompt** | Connect and query active records in a SQLite table named `users`. |
| **Expected Outcome** | 1. Connect to SQLite database.<br>2. Catch `sqlite3.OperationalError` (no such table: users).<br>3. Run DDL schema migration to create `users` table.<br>4. Catch SQL query syntax error (double `FROM` keywords).<br>5. Patch query to use a single `FROM` keyword.<br>6. Query successfully and count queried record rows. |
| **Actual / Real Result** | Traced missing table exception, created SQLite table `users` inserting Alice & Bob records, corrected `FROM FROM` to `FROM`, and successfully fetched 2 records. |
| **Technical Rationale** | Shows how agents interact with external relational database APIs and recover from schema mismatch operational exceptions. |
        """)
        
        st.markdown("**Detailed Cycle Execution Trace & State Mutation**")
        st.markdown("""
| Cycle / Step | Agent Thought & Goal | Actuator Command | Sandbox Observation / Error | Workspace State / Result |
| :--- | :--- | :--- | :--- | :--- |
| **Cycle 1** | Write file `db.py` to connect and query SQLite | `$ echo '...' > db.py` | Bash Code 0: Successfully wrote to file | Code contains syntax error (double `FROM` keywords: `SELECT * FROM FROM users`) |
| **Cycle 2** | Execute query check inside container | `$ python db.py` | `sqlite3.OperationalError: no such table: users` | database connection opens, but query fails due to missing table |
| **Cycle 3** | Run DDL schema migration to build `users` table | Run sqlite CREATE TABLE schema | Migration commit successful | SQLite `users` table created with columns `id`, `name`, `active` |
| **Cycle 4** | Re-run database verification script | `$ python db.py` | `sqlite3.OperationalError: near "FROM": syntax error` | Query syntax error identified on repeated `FROM` |
| **Cycle 5** | Patch SQL query syntax inside `db.py` | Code editor patch applied | Bash Code 0: Patch successfully committed | Corrects query to single `FROM` and inserts mock records (Alice, Bob) |
| **Cycle 6** | Execute query verification script | `$ python db.py` | `Query output: [(1, 'Alice', 1), (2, 'Bob', 1)]` | 2 records successfully fetched from SQLite database |
| **Cycle 7** | Validate output count against target checks | Verify fetched array length | Count matches expected target (2 records) | Target verified. Success! |
""")
        st.divider()

        # Test Case 3 Table
        st.markdown("### 🟢 Test Case 3: Data Pipeline (Pandas)")
        st.markdown("""
| Dimension | Value / Details |
| :--- | :--- |
| **Input Prompt** | Read and compute average salary stats from an `employees.csv` spreadsheet. |
| **Expected Outcome** | 1. Attempt CSV read.<br>2. Catch `FileNotFoundError` exception.<br>3. Generate mock `employees.csv` database file.<br>4. Catch `TypeError` (string concatenation error on salary addition).<br>5. Patch calculation code to cast salary column values to integers.<br>6. Calculate statistical average salary. |
| **Actual / Real Result** | Caught file not found, generated CSV via command execution, resolved type mismatch using integer casting, and computed average salary of `5500.0`. |
| **Technical Rationale** | Validates the agent's capability to resolve data ingestion blockers, handle format mismatches, and perform numerical analytics. |
        """)
        
        st.markdown("**Detailed Cycle Execution Trace & State Mutation**")
        st.markdown("""
| Cycle / Step | Agent Thought & Goal | Actuator Command | Sandbox Observation / Error | Workspace State / Result |
| :--- | :--- | :--- | :--- | :--- |
| **Cycle 1** | Write file `pipeline.py` to read/calculate salaries | `$ echo '...' > pipeline.py` | Bash Code 0: Successfully wrote to file | Initial code reads CSV but contains string-int concatenation bug |
| **Cycle 2** | Run data ingestion pipeline to check data | `$ python pipeline.py` | `FileNotFoundError: [Errno 2] No such file... 'employees.csv'` | Input dataset file is missing from working directory |
| **Cycle 3** | Generate mock dataset `employees.csv` in workspace | `$ echo -e '...' > employees.csv` | CSV file generated successfully | `employees.csv` created containing salaries for Alice (5000) and Bob (6000) |
| **Cycle 4** | Re-run pipeline to check calculations | `$ python pipeline.py` | `TypeError: can only concatenate str (not "int") to str` | Value read from CSV as string, causing crash on integer addition |
| **Cycle 5** | Patch `pipeline.py` to cast salary column to int | Code editor patch applied | Bash Code 0: Patch successfully committed | Implements type conversion: `salaries = [int(line.split(',')[1]) ...]` |
| **Cycle 6** | Re-run pipeline script | `$ python pipeline.py` | `Average Salary calculated: 5500.0` | Math logic executes successfully |
| **Cycle 7** | Verify computed average stats | Extract output statistics | Average salary matches check target (5500.0) | Target verified. Success! |
""")

    with doc_tab3:
        st.subheader("🔍 Perplexity Search Agent Test Suite")
        st.markdown("Below are three dynamic benchmark scenarios evaluated by the Perplexity Pro Search multi-hop engine.")
        
        # Test Case 1 Table
        st.markdown("### 🟢 Test Case 1: Software Piracy Solutions")
        st.markdown("""
| Dimension | Value / Details |
| :--- | :--- |
| **Input Query** | *what is the best solution for piracy and its technical importance?* |
| **Expected Outcome** | 1. Decompose query into sub-problems: piracy countermeasures and enclave details.<br>2. Scrape TechCrunch and Wired standards databases.<br>3. Identify Hardware-backed DRM (Widevine L1) as the best solution.<br>4. Detect information gap: missing enclave cryptographic details.<br>5. Trigger secondary crawl on Wikipedia and IEEE secure enclaves.<br>6. Synthesize final answer detailing isolated registers and memory dump protection. |
| **Actual / Real Result** | Extracted `piracy solutions`, crawled TechCrunch and Wired, flagged missing technical importance details, crawled Wikipedia and IEEE enclaves, and synthesized response detailing isolated registers. |
| **Technical Rationale** | Shows dynamic gap-detection triggers. If primary scrape yields no implementation mechanics, the search engine automatically replans and schedules secondary crawl sweeps. |
        """)
        
        st.markdown("**Detailed Multi-Hop Trace Contents**")
        st.markdown("""
| Step / Phase | Semantic Intent & Focus | Search Query & Source Visited | Scraped Knowledge Snippet | Gap Detection & Re-planning |
| :--- | :--- | :--- | :--- | :--- |
| **Step 1: Semantic Intent** | Decompose query into independent sub-problems | *what is the best solution for piracy...* | N/A (Decomposition phase) | Formulates sequential multi-hop plan. Stage 1 query: `'piracy solutions'`. |
| **Step 2: Primary Crawl** | Query and crawl search engines for general overview | `'piracy solutions'` (TechCrunch, Wired) | "Hardware-backed DRM (Widevine L1) is the industry standard for media protection..." | Visited 2 sources. Extracted Widevine L1 as best anti-piracy solution. |
| **Step 3: Gap Check** | Evaluate database response completeness | Core Reasoning engine | "Widevine L1 enclaves identify as best solution." | **GAP DETECTED**: Details on cryptographic/secure enclave importance are missing. Triggers: `'technical importance of secure enclaves'`. |
| **Step 4: Secondary Crawl** | Query and crawl details for detected gaps | `'technical importance of secure enclaves'` (Wikipedia, IEEE) | "Secure enclaves use isolated CPU registers, cryptographic keys, and separate execution memory..." | Visited secondary sources to acquire isolation and memory dump protection details. |
| **Step 5: Synthesized Citation** | Merge facts and generate cited output | LLM Synthesis engine | Compiled primary + secondary findings | Formulates cited answer detailing isolated registers, memory dump prevention, and untrusted host protection. |
""")
        st.divider()

        # Test Case 2 Table
        st.markdown("### 🟢 Test Case 2: Oscars Winners & Budgets (2026)")
        st.markdown("""
| Dimension | Value / Details |
| :--- | :--- |
| **Input Query** | *Who won the most Oscars in 2026, and what was their budget?* |
| **Expected Outcome** | 1. Decompose query: most Oscar wins and movie production financials.<br>2. Crawl Variety and Hollywood Reporter list pages.<br>3. Identify Dune: Part Three as winner (6 wins).<br>4. Detect knowledge gap: missing budget statistics.<br>5. Trigger secondary crawl on Box Office Mojo and Wikipedia.<br>6. Synthesize response citing Warner Bros/Legendary co-financing budget. |
| **Actual / Real Result** | Crawled winners list, retrieved Dune: Part Three wins fact, flagged budget gap, crawled Box Office Mojo details page, and synthesized cited response outlining the $190M production budget. |
| **Technical Rationale** | Demonstrates sequential multi-hop dependency resolution, where sub-problem 2 (budget search query) is constructed dynamically using the output of sub-problem 1 (movie name). |
        """)
        
        st.markdown("**Detailed Multi-Hop Trace Contents**")
        st.markdown("""
| Step / Phase | Semantic Intent & Focus | Search Query & Source Visited | Scraped Knowledge Snippet | Gap Detection & Re-planning |
| :--- | :--- | :--- | :--- | :--- |
| **Step 1: Semantic Intent** | Decompose query into sub-problems | *Who won the most Oscars in 2026, and what was their budget?* | N/A | Sub-problem 2 (budget) depends on Sub-problem 1 (winner). Stage 1 query: `'2026 Oscar winners'`. |
| **Step 2: Primary Crawl** | Crawl winners list database | `'2026 Oscar winners'` (Variety, Hollywood Reporter) | "Dune: Part Three dominated the Oscars with 6 wins..." | Visited 2 sources. Extracted winner: Dune: Part Three. |
| **Step 3: Gap Check** | Evaluate retrieved info for missing facts | Core Reasoning engine | "Dune: Part Three won most Oscars (6 wins)." | **GAP DETECTED**: Film budget stats missing. Triggers secondary query: `'Dune: Part Three movie budget'`. |
| **Step 4: Secondary Crawl** | Retrieve production budget details | `'Dune: Part Three movie budget'` (Box Office Mojo, Wikipedia) | "Dune: Part Three had a production budget of approximately $190 million USD..." | Visited Box Office Mojo. Scraped co-financing budget. |
| **Step 5: Synthesized Citation** | Format final cited response | LLM Synthesis engine | Compiled wins + budget facts | Outputs cited answer detailing Denis Villeneuve's film, 6 wins, $190M budget, and $720M gross. |
""")
        st.divider()

        # Test Case 3 Table
        st.markdown("### 🟢 Test Case 3: Fallback Search (General Topic)")
        st.markdown("""
| Dimension | Value / Details |
| :--- | :--- |
| **Input Query** | *Explain quantum computing hardware enclaves* |
| **Expected Outcome** | 1. Filter out punctuation and extract keywords (`quantum`, `hardware`).<br>2. Formulate primary crawl queries on general tech portals.<br>3. Retrieve base overview facts.<br>4. Flag engineering implications gap.<br>5. Run secondary crawl on research reviewers.<br>6. Synthesize answer explaining modular flexibility and decoupling. |
| **Actual / Real Result** | Extracted keywords `quantum` and `hardware`, visited tech portals, identified missing engineering details, crawled secondary articles, and compiled answer citing modular flexibility. |
| **Technical Rationale** | Verifies the robustness of the fallback routing engine, allowing the search simulator to process and resolve arbitrary queries gracefully without crashing. |
        """)
        
        st.markdown("**Detailed Multi-Hop Trace Contents**")
        st.markdown("""
| Step / Phase | Semantic Intent & Focus | Search Query & Source Visited | Scraped Knowledge Snippet | Gap Detection & Re-planning |
| :--- | :--- | :--- | :--- | :--- |
| **Step 1: Semantic Intent** | Parse keywords and decompose query | *Explain quantum computing hardware enclaves* | N/A | Filters noise. Extracts keyword target terms: `'quantum'`, `'hardware'`. Stage 1 query: `'quantum'`. |
| **Step 2: Primary Crawl** | Crawl base overview facts | `'quantum'` (Tech Portal, Online Encyclopedia) | "Quantum computing systems integrate modular environments to scale..." | Visited 2 general sources. Extracted baseline architectural overview. |
| **Step 3: Gap Check** | Evaluate data completeness | Core Reasoning engine | "Base context on quantum hardware enclaves." | **GAP DETECTED**: Practical engineering implications are missing. Triggers: `'quantum technical engineering implications'`. |
| **Step 4: Secondary Crawl** | Crawl engineering/reviewer articles | `'quantum technical engineering implications'` (Tech Reviewer) | "Main engineering importance resides in its modular flexibility and real-time execution speeds..." | Visited secondary source. Scraped modular coupling and speed performance details. |
| **Step 5: Synthesized Citation** | Compile findings | LLM Synthesis engine | Combined overview + modular details | Outputs cited response explaining quantum hardware architecture, highlighting modular flexibility and speed. |
""")

    with doc_tab4:
        st.subheader("🧪 Lab ReAct Agent Test Suite")
        st.markdown("Below are three dynamic runs evaluated by our Lab 1.1 Minimal ReAct Agent from scratch.")
        
        # Test Case 1 Table
        st.markdown("### 🟢 Run 1: Combined Arithmetic & Capital Check")
        st.markdown("""
| Dimension | Value / Details |
| :--- | :--- |
| **Input Goal** | *Calculate (45 * 23) + 12 and verify the capital of France.* |
| **Expected Outcome** | - **Cycle 1**: Parse math `(45 * 23) + 12`. Call Math tool. Get observation `1047`.<br>- **Cycle 2**: Parse search `capital of France`. Call Search tool. Get observation `Paris is the capital of France`.<br>- **Cycle 3**: Read observations and generate final synthesized response. |
| **Actual / Real Result** | Math tool output: `1047`. Search database hit: `Paris is the capital of France.` Final answer: `"The mathematical calculation yields 1047. Paris is the capital of France."` |
| **Technical Rationale** | Standard ReAct sequence demonstrating sequential reasoning, execution, and synthesis cycles without high-level wrapper frameworks. |
        """)
        
        st.markdown("**Detailed ReAct Trace Contents**")
        st.markdown("""
| Cycle | Reasoning / Thought | Action & Target Tool | Observation / Result | Workspace State / Result |
| :--- | :--- | :--- | :--- | :--- |
| **Cycle 1** | Parse mathematical expression and call Math tool | `Math[(45 * 23) + 12]` | `1047` | Arithmetic result cached in episodic memory |
| **Cycle 2** | Verify target country capital using Search tool | `Search[capital of France]` | `"Paris is the capital of France."` | Geographic fact cached in episodic memory |
| **Cycle 3** | Read observations and compile final response | N/A | N/A | Synthesizes response: `"The mathematical calculation yields 1047. Paris is the capital of France."` |
""")
        st.divider()

        # Test Case 2 Table
        st.markdown("### 🟢 Run 2: Alternative Math & German Capital")
        st.markdown("""
| Dimension | Value / Details |
| :--- | :--- |
| **Input Goal** | *Calculate (10 + 20) * 30 and find the capital of Germany.* |
| **Expected Outcome** | - **Cycle 1**: Parse math `(10 + 20) * 30`. Call Math tool. Get observation `900`.<br>- **Cycle 2**: Parse search `capital of Germany`. Call Search tool. Get observation `Berlin is the capital of Germany`.<br>- **Cycle 3**: Synthesize calculations and facts into final answer. |
| **Actual / Real Result** | Math tool output: `900`. Search database hit: `Berlin is the capital of Germany.` Final answer: `"The mathematical calculation yields 900. Berlin is the capital of Germany."` |
| **Technical Rationale** | Validates the regex arithmetic parser and mock search keyword match loops on varied country keys. |
        """)
        
        st.markdown("**Detailed ReAct Trace Contents**")
        st.markdown("""
| Cycle | Reasoning / Thought | Action & Target Tool | Observation / Result | Workspace State / Result |
| :--- | :--- | :--- | :--- | :--- |
| **Cycle 1** | Parse mathematical expression and call Math tool | `Math[(10 + 20) * 30]` | `900` | Arithmetic result cached in episodic memory |
| **Cycle 2** | Verify target country capital using Search tool | `Search[capital of Germany]` | `"Berlin is the capital of Germany."` | Geographic fact cached in episodic memory |
| **Cycle 3** | Read observations and compile final response | N/A | N/A | Synthesizes response: `"The mathematical calculation yields 900. Berlin is the capital of Germany."` |
""")
        st.divider()

        # Test Case 3 Table
        st.markdown("### 🟢 Run 3: Geography-Only Queries")
        st.markdown("""
| Dimension | Value / Details |
| :--- | :--- |
| **Input Goal** | *Verify the population of Paris and locate Rome.* |
| **Expected Outcome** | - **Cycle 1**: Detect no arithmetic formula. Skip Math tool and immediately search `population of Paris`. Retrieve observation `2.1 million`.<br>- **Cycle 2**: Parse search `locate Rome`. Retrieve mock search result.<br>- **Cycle 3**: Synthesize search facts into final answer. |
| **Actual / Real Result** | Math tool call skipped. Search 1 hit: `The population of Paris is approximately 2.1 million.` Search 2 hit: `Locate Rome info retrieved (mock database result).` Final answer: `"The population of Paris is approximately 2.1 million. Locate Rome info retrieved (mock database result)."` |
| **Technical Rationale** | Confirms task-branching logic where math tools are dynamically skipped when arithmetic expressions are missing from the input prompt. |
        """)
        
        st.markdown("**Detailed ReAct Trace Contents**")
        st.markdown("""
| Cycle | Reasoning / Thought | Action & Target Tool | Observation / Result | Workspace State / Result |
| :--- | :--- | :--- | :--- | :--- |
| **Cycle 1** | No math formula detected; parse and query population | `Search[population of Paris]` | `"The population of Paris is approximately 2.1 million."` | Population statistics cached in episodic memory |
| **Cycle 2** | Parse second query concept and search | `Search[locate Rome]` | `"Rome info retrieved (mock database result)."` | Location data cached in episodic memory |
| **Cycle 3** | Read observations and compile final response | N/A | N/A | Synthesizes response: `"The population of Paris is approximately 2.1 million. Locate Rome info retrieved..."` |
""")

# Footer
st.divider()
st.markdown("<p style='text-align: center; color: #718096;'>Agentic AI Lab  •  Research Intern - Ada Lovelace  •  Gradebook Syllabus CS-AAI-402</p>", unsafe_allow_html=True)
