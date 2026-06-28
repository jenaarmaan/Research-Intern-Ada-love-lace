import streamlit as st
import os
import sys
import time
import pandas as pd
import numpy as np

# Ensure supporting_code is in the python path
sys.path.append(os.path.join(os.path.dirname(__file__), "supporting_code"))
from agent import ReActAgent

# Set page config
st.set_page_config(
    page_title="ReAct Agent Sandbox Explorer",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium styling matching index.css
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .logo-orb {
        width: 15px;
        height: 15px;
        background: radial-gradient(circle, #00f0ff 0%, #ff4b4b 100%);
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.8);
    }
    
    .brand-title {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #00f0ff 0%, #ff4b4b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2rem;
        margin: 0;
    }

    .main-title {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(90deg, #00ff66 0%, #00f0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 1.8rem;
    }

    .glass-panel {
        background-color: rgba(26, 28, 36, 0.75);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2d313f;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    /* Terminal Console */
    .terminal-box {
        background-color: #0a0c10;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #1a1e26;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        color: #00ff66;
        height: 400px;
        overflow-y: auto;
        font-size: 0.85rem;
        line-height: 1.5;
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.8);
    }
    
    .terminal-line {
        margin-bottom: 5px;
    }
    .system-line { color: #8892b0; }
    .thought-line { color: #ffd700; }
    .action-line { color: #00f0ff; }
    .observe-line { color: #e5c07b; }
    .error-line { color: #ff4b4b; font-weight: bold; }
    .success-line { color: #00ff66; font-weight: bold; }

    /* Node Visualization */
    .nodes-row {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-top: 15px;
        margin-bottom: 20px;
        padding: 10px 0;
    }
    
    .node-item-st {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #2d313f;
        background-color: #1a1c24;
        width: 15%;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .node-active {
        border-color: #00f0ff;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
        background-color: rgba(0, 240, 255, 0.1);
    }
    
    .node-circle-st {
        font-size: 1.5rem;
        margin-bottom: 5px;
    }

    /* Warning alert */
    .replan-alert {
        background-color: rgba(255, 75, 75, 0.1);
        border: 1px solid #ff4b4b;
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
        box-shadow: 0 0 10px rgba(255, 75, 75, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State values for metrics and lists
if "agent_run_data" not in st.session_state:
    st.session_state.agent_run_data = None
if "run_history" not in st.session_state:
    st.session_state.run_history = []
if "sim_progress" not in st.session_state:
    st.session_state.sim_progress = False

# Sidebar Branding
st.sidebar.markdown(
    '<div><span class="logo-orb"></span><h2 style="display:inline;" class="brand-title">ReAct Agent</h2><br><span style="color:#8892b0; font-size:0.8rem; margin-left:25px;">Sandbox System v1.0</span></div>', 
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# Load default benchmark cases from agent's determine task flow mappings
default_cases = [
    {
        "id": "task_1",
        "name": "Multi-Hop Financial Query",
        "prompt": "Find Apple's 2024 annual revenue and Microsoft's 2024 annual revenue, and calculate the absolute difference between them."
    },
    {
        "id": "task_2",
        "name": "Flaky Scraper Recovery",
        "prompt": "Scrape financial statistics from the URL 'https://flaky-database.api/data' and recover using backup mirror endpoints if a failure occurs."
    },
    {
        "id": "task_3",
        "name": "Buggy Code Runtime Correction",
        "prompt": "Calculate the result of dividing 100 by the divisor variable (initially 0). Catch standard runtime exceptions (ZeroDivisionError) and correct it to divisor=5."
    },
    {
        "id": "task_4",
        "name": "Recursive Demographic Analysis",
        "prompt": "Search for the individual populations of Paris, Tokyo, and New York City, and calculate their mathematical average population using python."
    },
    {
        "id": "task_5",
        "name": "Missing Tool Input Query Refinement",
        "prompt": "Search for Google's 2024 annual revenue, handling an empty search string error initially, and recover using refined keywords."
    }
]

st.sidebar.markdown("### ⚡ Automated Benchmarks")
selected_case = st.sidebar.selectbox("Choose a benchmark task input:", [f"{c['name']} (Task {i+1})" for i, c in enumerate(default_cases)])

selected_prompt = ""
for case in default_cases:
    if case["name"] in selected_case:
        selected_prompt = case["prompt"]

if st.sidebar.button("Run Selected Benchmark", key="run_benchmark_btn"):
    st.session_state.query_value = selected_prompt
    st.session_state.execute_query_flag = True

st.sidebar.markdown("---")

# System specs sidebar
st.sidebar.markdown("### 🖥️ Sandbox Engine Status")
st.sidebar.markdown("""
- **Environment**: Windows Python 3.14
- **Safety Control**: Sandboxed Python REPL
- **Redirection Logic**: Active Stack Manipulation
""")

# Setup cumulative metrics calculations
success_rate = 0.0
avg_steps = 0.0
total_failures_resolved = 0

if st.session_state.run_history:
    total_runs = len(st.session_state.run_history)
    successful_runs = sum(1 for r in st.session_state.run_history if r["success"])
    success_rate = (successful_runs / total_runs) * 100
    avg_steps = sum(r["steps"] for r in st.session_state.run_history) / total_runs
    total_failures_resolved = sum(r["failures"] for r in st.session_state.run_history)

# Main Grid Headers
col_title_left, col_title_right = st.columns([3, 1])
with col_title_left:
    st.markdown('<div class="main-title">Agent Cognitive Playground</div>', unsafe_allow_html=True)
    st.write("Observe, trace, and debug dynamic re-planning on failures in real-time.")
with col_title_right:
    # State Display badge
    if st.session_state.sim_progress:
        st.markdown('<div class="glass-panel" style="padding: 10px; text-align: center; border-color: #ff9900; color: #ff9900; font-weight: bold; margin:0;">🛠️ Running Loop</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="glass-panel" style="padding: 10px; text-align: center; border-color: #00ff66; color: #00ff66; font-weight: bold; margin:0;">🟢 Idle State</div>', unsafe_allow_html=True)

st.write("")

# Metrics Row
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.markdown(f"""
    <div class="glass-panel" style="margin-bottom:0;">
        <div style="color:#8892b0; font-size:0.9rem;">Execution Success Rate</div>
        <div style="font-size:2.2rem; font-weight:800; color:#00ff66; font-family:'Outfit';">{success_rate:.0f}%</div>
        <div style="color:#8892b0; font-size:0.8rem; margin-top:2px;">Self-correcting code recovery</div>
    </div>
    """, unsafe_allow_html=True)
with col_m2:
    st.markdown(f"""
    <div class="glass-panel" style="margin-bottom:0;">
        <div style="color:#8892b0; font-size:0.9rem;">Average Cognitive Steps</div>
        <div style="font-size:2.2rem; font-weight:800; color:#ffd700; font-family:'Outfit';">{avg_steps:.1f}</div>
        <div style="color:#8892b0; font-size:0.8rem; margin-top:2px;">Reason-and-Act operations</div>
    </div>
    """, unsafe_allow_html=True)
with col_m3:
    st.markdown(f"""
    <div class="glass-panel" style="margin-bottom:0;">
        <div style="color:#8892b0; font-size:0.9rem;">Total Failures Resolved</div>
        <div style="font-size:2.2rem; font-weight:800; color:#ff4b4b; font-family:'Outfit';">{total_failures_resolved}</div>
        <div style="color:#8892b0; font-size:0.8rem; margin-top:2px;">Exceptions & HTTP errors bypassed</div>
    </div>
    """, unsafe_allow_html=True)
with col_m4:
    # Get last latency
    last_latency = 0.000
    if st.session_state.agent_run_data:
        last_latency = st.session_state.agent_run_data.get("execution_time_seconds", 0.0)
    st.markdown(f"""
    <div class="glass-panel" style="margin-bottom:0;">
        <div style="color:#8892b0; font-size:0.9rem;">Server Response Latency</div>
        <div style="font-size:2.2rem; font-weight:800; color:#00f0ff; font-family:'Outfit';">{last_latency:.3f}s</div>
        <div style="color:#8892b0; font-size:0.8rem; margin-top:2px;">Pure execution runtime</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Layout
col_main_left, col_main_right = st.columns([3, 2])

with col_main_left:
    # 1. Custom Query Executor panel
    st.markdown("### Custom Query Executor")
    
    # Query Form
    q_val = st.text_input("Enter a custom multi-step task or query:", value=st.session_state.get("query_value", ""), placeholder="e.g. Find Alan Turing birth year and country capital...", key="user_query_input")
    
    run_btn_main = st.button("Run ReAct Agent Engine", key="run_agent_btn")
    
    if run_btn_main or st.session_state.get("execute_query_flag", False):
        st.session_state.execute_query_flag = False
        st.session_state.query_value = q_val
        
        if q_val.strip():
            st.session_state.sim_progress = True
            
            # Execute Agent synchronously under the hood to get all traces
            agent = ReActAgent()
            with st.spinner("Executing agent logic..."):
                run_res = agent.run(q_val)
            
            # Save results to session state
            st.session_state.agent_run_data = run_res
            st.session_state.run_history.append({
                "success": run_res["success"],
                "steps": run_res["steps_taken"],
                "failures": run_res["failures_resolved"]
            })
            
            # Reset UI animation flags
            st.session_state.active_step_idx = 0
            st.session_state.sim_logs = []
            st.session_state.active_node = "Standby"
            st.session_state.replan_alert = None
            st.session_state.final_answer = ""
            
            # Start loop simulation
            trace_logs = run_res["trace_logs"]
            
            # Create progress bars and placeholders
            status_text = st.empty()
            
            for log in trace_logs:
                # Update simulation speed delay
                time.sleep(0.4)
                
                # Append to terminal logs
                st.session_state.sim_logs.append(log)
                
                # Set active node based on type
                log_type = log["type"]
                if log_type == "RECEIVE_TASK":
                    st.session_state.active_node = "Receive"
                elif log_type in ["THOUGHT", "RE-PLANNING"]:
                    st.session_state.active_node = "Thought"
                elif log_type == "ACTION":
                    st.session_state.active_node = "Action"
                elif log_type == "OBSERVATION":
                    st.session_state.active_node = "Observe"
                elif log_type == "FINISH":
                    st.session_state.active_node = "Finish"
                
                # Dynamic Re-planning warning detection
                if log_type == "RE-PLANNING":
                    st.session_state.replan_alert = log["message"] + ": " + log["detail"]["thought"]
                elif log_type == "PLAN_UPDATED":
                    pass # Keep warning active for a step
                elif log_type == "ACTION" and not "corrected" in log["message"].lower():
                    # Clear warning on next new regular action
                    st.session_state.replan_alert = None
                
                # Force rerun to animate the changes
                # In Streamlit, since we are inside a button trigger, we can render the animated containers
                # using st.empty containers, avoiding full page reruns for speed.
                
            st.session_state.final_answer = run_res["final_answer"]
            st.session_state.sim_progress = False
            st.rerun()

    # --- Live Rendering Area for Visuals ---
    st.markdown("### Cognitive Loop Visualizer")
    
    # Render Step node rows
    node = st.session_state.get("active_node", "Standby")
    
    # Compute active classes
    n_rec = "node-active" if node == "Receive" else ""
    n_tho = "node-active" if node == "Thought" else ""
    n_act = "node-active" if node == "Action" else ""
    n_obs = "node-active" if node == "Observe" else ""
    n_fin = "node-active" if node == "Finish" else ""
    
    st.markdown(f"""
    <div class="nodes-row">
        <div class="node-item-st {n_rec}">
            <div class="node-circle-st">📥</div>
            <div style="font-weight:bold; font-size:0.8rem; color:#ffffff;">Task Ingestion</div>
        </div>
        <div style="color:#8892b0; font-size:1.5rem;">➔</div>
        <div class="node-item-st {n_tho}">
            <div class="node-circle-st">🧠</div>
            <div style="font-weight:bold; font-size:0.8rem; color:#ffffff;">Cognitive Thought</div>
        </div>
        <div style="color:#8892b0; font-size:1.5rem;">➔</div>
        <div class="node-item-st {n_act}">
            <div class="node-circle-st">⚙</div>
            <div style="font-weight:bold; font-size:0.8rem; color:#ffffff;">Tool Action</div>
        </div>
        <div style="color:#8892b0; font-size:1.5rem;">➔</div>
        <div class="node-item-st {n_obs}">
            <div class="node-circle-st">👁</div>
            <div style="font-weight:bold; font-size:0.8rem; color:#ffffff;">Observation</div>
        </div>
        <div style="color:#8892b0; font-size:1.5rem;">➔</div>
        <div class="node-item-st {n_fin}">
            <div class="node-circle-st">🏁</div>
            <div style="font-weight:bold; font-size:0.8rem; color:#ffffff;">Goal Finish</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Re-planning alert
    replan_msg = st.session_state.get("replan_alert", None)
    if replan_msg:
        st.markdown(f"""
        <div class="replan-alert">
            <div style="display:flex; align-items:center; color:#ff4b4b; font-weight:bold; font-size:0.9rem; margin-bottom:5px;">
                <span style="font-size:1.2rem; margin-right:5px;">⚠️</span> DYNAMIC RE-PLANNING ACTIVE
            </div>
            <p style="color:#ffffff; font-size:0.85rem; margin:0;">{replan_msg}</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # Final Response Panel
    st.markdown("### Compiled Final Response")
    final_ans = st.session_state.get("final_answer", "")
    if final_ans:
        st.success(final_ans)
    else:
        st.info("Agent stands ready to accept tasks. Choose a benchmark test case on the sidebar or enter a custom prompt above to start the engine.")

with col_main_right:
    st.markdown("### Interactive Real-Time Terminal")
    
    # Compile terminal lines matching index.css class types
    sim_logs = st.session_state.get("sim_logs", [])
    
    terminal_content = ""
    if not sim_logs:
        terminal_content = """
        <div class="terminal-line system-line">[SYSTEM] Terminal initialized. Waiting for task queries...</div>
        <div class="terminal-line system-line">[SYSTEM] Ready to monitor cognitive processes, tools actions, and observations.</div>
        """
    else:
        for log in sim_logs:
            log_type = log["type"]
            msg = log["message"]
            detail = log.get("detail", "")
            
            line_class = "system-line"
            if log_type == "RECEIVE_TASK":
                line_class = "system-line"
                terminal_content += f'<div class="terminal-line {line_class}">[INGEST] {msg}</div>'
            elif log_type == "INITIAL_PLAN":
                line_class = "system-line"
                terminal_content += f'<div class="terminal-line {line_class}">[PLAN] {msg}: {detail.get("plan")}</div>'
            elif log_type == "THOUGHT":
                line_class = "thought-line"
                terminal_content += f'<div class="terminal-line {line_class}">[THOUGHT] {msg}</div>'
            elif log_type == "ACTION":
                line_class = "action-line"
                terminal_content += f'<div class="terminal-line {line_class}">[ACTION] {msg} (Input: {detail.get("input")})</div>'
            elif log_type == "OBSERVATION":
                line_class = "observe-line"
                # Trim long observations for readability
                obs_text = detail.get("output", "")
                if len(obs_text) > 150:
                    obs_text = obs_text[:150] + "..."
                terminal_content += f'<div class="terminal-line {line_class}">[OBSERVE] {msg} -> {obs_text}</div>'
            elif log_type == "RE-PLANNING":
                line_class = "error-line"
                terminal_content += f'<div class="terminal-line {line_class}">[RE-PLAN] {msg}: {detail.get("thought")}</div>'
            elif log_type == "PLAN_UPDATED":
                line_class = "system-line"
                terminal_content += f'<div class="terminal-line {line_class}">[PLAN UPDATE] {msg} (New Stack: {detail.get("remaining_plan")})</div>'
            elif log_type == "FAILURE_TRACE":
                line_class = "error-line"
                terminal_content += f'<div class="terminal-line {line_class}">[CRITICAL] {msg} (Obs: {detail.get("observation")[:80]})</div>'
            elif log_type == "FINISH":
                line_class = "success-line"
                terminal_content += f'<div class="terminal-line {line_class}">[SUCCESS] {msg}</div>'
                terminal_content += f'<div class="terminal-line success-line">--------------------------------------------------</div>'
                
    st.markdown(f"""
    <div style="background-color:#1a1e26; border-radius: 8px 8px 0 0; padding:10px 15px; border:1px solid #2d313f; border-bottom:none; display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; gap:6px;">
            <span style="width:12px; height:12px; border-radius:50%; background-color:#ff4b4b; display:inline-block;"></span>
            <span style="width:12px; height:12px; border-radius:50%; background-color:#ffd700; display:inline-block;"></span>
            <span style="width:12px; height:12px; border-radius:50%; background-color:#00ff66; display:inline-block;"></span>
        </div>
        <div style="font-family:'JetBrains Mono'; font-size:0.75rem; color:#8892b0;">agent@react-sandbox:~</div>
        <div></div>
    </div>
    <div class="terminal-box">
        {terminal_content}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🧹 Clear Terminal Logs", key="clear_terminal_btn"):
        st.session_state.sim_logs = []
        st.session_state.active_node = "Standby"
        st.session_state.replan_alert = None
        st.session_state.final_answer = ""
        st.rerun()
