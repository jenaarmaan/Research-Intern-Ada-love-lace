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
    st.session_state.perp_logs = []
if 'perp_episodic_memory' not in st.session_state:
    st.session_state.perp_episodic_memory = {}
if 'perp_citations' not in st.session_state:
    st.session_state.perp_citations = []
if 'perp_gap_detected' not in st.session_state:
    st.session_state.perp_gap_detected = False
if 'perp_answer' not in st.session_state:
    st.session_state.perp_answer = ""
if 'perp_winner' not in st.session_state:
    st.session_state.perp_winner = None
if 'perp_budget' not in st.session_state:
    st.session_state.perp_budget = None

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
        options=["📊 Architecture Comparison", "💻 Devin Task Agent", "🔍 Perplexity Search Agent", "🧪 Lab Sessions (L1.1 & L1.2)"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.markdown("### Student Intern State")
    st.info("💡 **Active Branch**: `assignment-1`\n\n🎯 **Coursework Status**: Fully Completed\n\n📈 **Weightage**: 15%")

# ----------------- PAGE 1: COMPARATIVE ARCHITECTURE -----------------

if nav_selection == "📊 Architecture Comparison":
    st.markdown('<div class="title-gradient">Agent Architecture Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">A rigorous comparative analysis of Devin (Action-Oriented Task Solver) and Perplexity Pro Search (Information Synthesizer)</div>', unsafe_allow_html=True)
    
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
    
    # Devin Sandbox Control Functions
    def devin_reset():
        st.session_state.devin_step = 0
        st.session_state.devin_logs = ["System reset. Awaiting task initiation..."]
        st.session_state.devin_code = ""
        st.session_state.devin_insights = []
        st.session_state.devin_sandbox_installed = set(["pip", "python"])
        st.session_state.devin_plan = [
            {"id": 1, "task": "Create app.py and write basic Flask server code", "status": "pending"},
            {"id": 2, "task": "Verify code by running the Flask server", "status": "pending"},
            {"id": 3, "task": "Verify route / returns success code", "status": "pending"}
        ]
        
    def devin_next_cycle():
        step = st.session_state.devin_step + 1
        st.session_state.devin_step = step
        
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
            
            # Dynamic Plan update
            st.session_state.devin_plan.insert(1, {"id": 1.5, "task": "Install missing package 'flask' via pip", "status": "pending"})
            st.session_state.devin_insights.append("Insight: Flask was absent in baseline sandbox container. Formulated package insertion task.")

        # Cycle 3: Install Package
        elif step == 3:
            st.session_state.devin_plan[1]["status"] = "completed"
            st.session_state.devin_sandbox_installed.add("flask")
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
        st.markdown("**Mock Editor IDE (`app.py`)**")
        code_text = st.session_state.devin_code if st.session_state.devin_code else "# Editor buffer is empty"
        st.code(code_text, language="python")

# ----------------- PAGE 3: PERPLEXITY SEARCH AGENT SIMULATION -----------------

elif nav_selection == "🔍 Perplexity Search Agent":
    st.markdown('<div class="title-gradient">Perplexity Pro Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Interactive Simulation of Parallel Search, HTML Scraping, Information-Gap Detection, and Source Citation Synthesizer</div>', unsafe_allow_html=True)
    
    # Perplexity Reset
    def perp_reset():
        st.session_state.perp_step = 0
        st.session_state.perp_logs = []
        st.session_state.perp_episodic_memory = {}
        st.session_state.perp_citations = []
        st.session_state.perp_gap_detected = False
        st.session_state.perp_answer = ""
        st.session_state.perp_winner = None
        st.session_state.perp_budget = None

    # UI Query Search Action
    query_input = st.text_input(
        "Ask a complex, multi-hop question:",
        value="Who won the most Oscars in 2026, and what was their budget?",
        placeholder="Type search topic..."
    )
    
    col_run, col_reset = st.columns([1, 5])
    with col_run:
        run_search = st.button("Pro Search 🚀", use_container_width=True)
    with col_reset:
        st.button("Clear Cache 🔄", on_click=perp_reset)
        
    if run_search or st.session_state.perp_step > 0:
        if st.session_state.perp_step == 0:
            st.session_state.perp_step = 1
            
            # Step 1: Semantic Query Parse
            st.session_state.perp_logs.append("🔍 **Step 1: Semantic Intent Analysis**")
            st.session_state.perp_logs.append("Decomposing complex query into sub-problems:\n- Sub-problem 1: Find the movie with the most Oscar wins in 2026.\n- Sub-problem 2: Find the budget of that specific Oscar winner.\nReasoning: Sub-problem 2 depends on the output of Sub-problem 1. Formulating sequential multi-hop search plan.")
            st.session_state.perp_logs.append("Query formulation: stage 1 target term is `'2026 Oscar winners'`.")
            
            # Step 2: Actuate Primary Search & Scrape
            st.session_state.perp_logs.append("\n🌎 **Step 2: Actuating Primary Search & Web Crawling**")
            st.session_state.perp_logs.append("Launching parallel search engine index queries...")
            time.sleep(0.5)
            
            results = WEB_INDEX["2026 Oscar winners"]
            st.session_state.perp_logs.append(f"Search engines returned {len(results)} matches. Crawling URL payloads:")
            for res in results:
                st.session_state.perp_logs.append(f"  - Visited URL: `{res['url']}` (Scraped title: *\"{res['title']}\"*)")
                st.session_state.perp_episodic_memory[res["url"]] = res["content"]
                st.session_state.perp_citations.append(res["url"])
                
            # Step 3: Analysis of facts
            st.session_state.perp_logs.append("\n🧠 **Step 3: Reasoning & Knowledge Synthesis**")
            # Discover winner in logs
            st.session_state.perp_winner = "Dune: Part Three"
            st.session_state.perp_logs.append(f"Extracted fact: **Dune: Part Three** won 6 Oscars (most awards of the evening).")
            st.session_state.perp_logs.append("Evaluating data completeness:\n- Oscar Winner: FOUND (Dune: Part Three)\n- Budget: MISSING (No budget metrics present in Variety or Hollywood Reporter contents).")
            
            # Step 4: Gap Detection & Dynamic query update
            st.session_state.perp_gap_detected = True
            secondary_term = "Dune: Part Three movie budget"
            st.session_state.perp_logs.append(f"🚩 **[Gap Detected]** Secondary search query triggered: `{secondary_term}`")
            
            # Step 5: Actuate Secondary Search
            st.session_state.perp_logs.append("\n🌎 **Step 4: Actuating Secondary Search & Web Crawling**")
            time.sleep(0.5)
            sec_results = WEB_INDEX["Dune: Part Three movie budget"]
            st.session_state.perp_logs.append(f"Crawl database returned {len(sec_results)} secondary matches. Fetching full HTML pages:")
            for res in sec_results:
                st.session_state.perp_logs.append(f"  - Visited URL: `{res['url']}` (Scraped title: *\"{res['title']}\"*)")
                st.session_state.perp_episodic_memory[res["url"]] = res["content"]
                st.session_state.perp_citations.append(res["url"])
                
            # Step 6: Synthesis
            st.session_state.perp_budget = "$190 million"
            st.session_state.perp_logs.append("\n🧠 **Step 5: Final Joint Analysis & Citation Synthesis**")
            st.session_state.perp_logs.append("Joint correlation completed. Formatting output citing all crawled references...")
            
            st.session_state.perp_answer = f"""At the 98th Academy Awards in 2026, the movie that won the most Oscars was **Dune: Part Three**, taking home a total of **6 Oscars** including Best Director for Denis Villeneuve and sweeping the technical categories [1][2]. 

The production budget for **Dune: Part Three** was approximately **$190 million USD** [3][4], which was co-financed by Legendary Pictures and Warner Bros. The film proved to be a major financial success, grossing over $720 million worldwide [3]."""

        # Display results UI
        col_logs, col_synth = st.columns([1, 1])
        
        with col_logs:
            st.subheader("⚙️ Pro Search Execution Trace")
            logs_txt = "\n".join(st.session_state.perp_logs)
            st.markdown(f'<div class="terminal-console" style="height: 480px;">{logs_txt}</div>', unsafe_allow_html=True)
            
        with col_synth:
            st.subheader("✨ Synthesized Search Response")
            st.markdown(f'<div class="card" style="min-height: 250px;">{st.session_state.perp_answer}</div>', unsafe_allow_html=True)
            
            st.subheader("🔗 Visited Sources")
            for i, url in enumerate(st.session_state.perp_citations):
                st.markdown(f"**[{i+1}]** `{url}`")
                
            # Mock Scraped Snippets Cards
            with st.expander("📂 Cached Web Data in Episodic Memory"):
                for url, content in st.session_state.perp_episodic_memory.items():
                    st.caption(f"**Source**: {url}")
                    st.write(content)
                    st.divider()

# ----------------- PAGE 4: LAB SESSIONS (L1.1 & L1.2) -----------------
elif nav_selection == "🧪 Lab Sessions (L1.1 & L1.2)":
    st.markdown('<div class="title-gradient">Module 1 Lab Sessions</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Interactive Execution & Study of Labs L1.1 (Minimal ReAct Agent) and L1.2 (LangChain vs LlamaIndex)</div>', unsafe_allow_html=True)
    
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
            
        col_run_lab, col_reset_lab = st.columns([1, 4])
        with col_run_lab:
            if st.button("Run ReAct Loop 🚀", key="btn_run_lab_1_1"):
                st.session_state.lab_logs = ["[ReAct Agent Initialized] Goal: Calculate (45 * 23) + 12 and verify capital of France."]
                
                # Cycle 1: Thought & Action
                st.session_state.lab_logs.append("\n--- CYCLE 1 ---")
                st.session_state.lab_logs.append("[Thought] I need to calculate the math expression: (45 * 23) + 12. I will call the Math tool.")
                st.session_state.lab_logs.append("[Action] Math[(45 * 23) + 12]")
                st.session_state.lab_logs.append("[Observation] 1047")
                
                # Cycle 2: Thought & Action
                st.session_state.lab_logs.append("\n--- CYCLE 2 ---")
                st.session_state.lab_logs.append("[Thought] I have the math output: 1047. Now I need to search for the capital of France.")
                st.session_state.lab_logs.append("[Action] Search[capital of France]")
                st.session_state.lab_logs.append("[Observation] Paris is the capital of France.")
                
                # Cycle 3: Final Answer
                st.session_state.lab_logs.append("\n--- CYCLE 3 ---")
                st.session_state.lab_logs.append("[Thought] I have the calculation (1047) and the capital (Paris). I can now synthesize the response.")
                st.session_state.lab_logs.append("[Final Answer] The calculation yields 1047, and the capital of France is Paris.")
                st.session_state.lab_ans = "The calculation of (45 * 23) + 12 yields 1047, and the capital of France is Paris."
                
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

# Footer
st.divider()
st.markdown("<p style='text-align: center; color: #718096;'>Agentic AI Lab  •  Research Intern - Ada Lovelace  •  Gradebook Syllabus CS-AAI-402</p>", unsafe_allow_html=True)
