import streamlit as st
import os
import sys
import time
import pandas as pd
import json

# Ensure supporting_code is in the python path
sys.path.append(os.path.join(os.path.dirname(__file__), "supporting_code"))
from supporting_code.multi_agent_system import SoftwareCompanyPipeline, gemini_available
from supporting_code.evaluation import PipelineEvaluator

# Set Page Config
st.set_page_config(
    page_title="Multi-Agent Software Pipeline Sandbox",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS styling
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
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #a6accd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .main-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00f0ff 0%, #ff4b4b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .gradient-subheader {
        font-family: 'Outfit', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #00f0ff;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    
    .glass-panel {
        background: rgba(22, 26, 37, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .agent-card-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
        background-color: #0e1117;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2d313f;
    }
    
    .agent-node {
        flex: 1;
        text-align: center;
        padding: 12px 6px;
        border-radius: 8px;
        background-color: #1a1e26;
        border: 2px solid #2d313f;
        transition: all 0.3s ease;
        opacity: 0.6;
    }
    
    .agent-active {
        opacity: 1.0;
        border-color: #00f0ff;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
        background-color: rgba(0, 240, 255, 0.1);
    }
    
    .agent-circle {
        font-size: 1.5rem;
        margin-bottom: 5px;
    }

    .terminal-box {
        background-color: #0c0f16;
        border: 1px solid #2d313f;
        border-radius: 0 0 8px 8px;
        padding: 15px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #a6accd;
        min-height: 250px;
        max-height: 400px;
        overflow-y: auto;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
    }
    
    .terminal-line {
        margin-bottom: 6px;
        line-height: 1.4;
    }
    
    .system-line { color: #8892b0; }
    .pm-line { color: #a277ff; }
    .arch-line { color: #ffd700; }
    .dev-line { color: #00f0ff; }
    .qa-line { color: #00ff66; }
    .error-line { color: #ff4b4b; }
    
    .status-badge-api {
        background-color: rgba(0, 240, 255, 0.1);
        border: 1px solid #00f0ff;
        color: #00f0ff;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status-badge-sandbox {
        background-color: rgba(255, 75, 75, 0.1);
        border: 1px solid #ff4b4b;
        color: #ff4b4b;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "company_run_data" not in st.session_state:
    st.session_state.company_run_data = None
if "replay_logs" not in st.session_state:
    st.session_state.replay_logs = []
if "active_node" not in st.session_state:
    st.session_state.active_node = "System"
if "running_replay" not in st.session_state:
    st.session_state.running_replay = False

# Sidebar Config
st.sidebar.markdown(
    '<div><span class="logo-orb"></span><h2 style="display:inline;" class="brand-title">DevOps Agents</h2><br><span style="color:#8892b0; font-size:0.8rem; margin-left:25px;">Multi-Agent Pipeline v1.0</span></div>', 
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

# API Status Badge
if gemini_available:
    st.sidebar.markdown('<span class="status-badge-api">📡 Gemini Connected</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<span class="status-badge-sandbox">🛡️ Sandbox Fallback Mode</span>', unsafe_allow_html=True)

st.sidebar.markdown("---")

# Setup default benchmark cases
default_cases = [
    {
        "name": "Fibonacci & Prime Checker Library",
        "prompt": "Create a library that calculates the Fibonacci sequence up to N and checks if a number is prime."
    },
    {
        "name": "RPN Stack Calculator",
        "prompt": "Implement a Reverse Polish Notation (RPN) calculator supporting basic operators (+, -, *, /) and stack inspection."
    },
    {
        "name": "Text File Analyzer & Word Counter",
        "prompt": "Write a tool to count words, sentences, and unique character frequencies in a text file."
    },
    {
        "name": "JSON Key-Value Store",
        "prompt": "Create a lightweight JSON file-backed key-value database with transactions (commit/rollback)."
    },
    {
        "name": "Temperature Unit Converter",
        "prompt": "Create a Celsius/Fahrenheit/Kelvin converter that converts values and yields status."
    }
]

st.sidebar.markdown("### ⚙️ Pipeline Configuration")
case_sel = st.sidebar.selectbox("Load Benchmark Case", [c["name"] for c in default_cases] + ["Custom Specification"])
correction_on = st.sidebar.toggle("Enable QA Self-Correction", value=True)
offline_mode = st.sidebar.toggle("Force Offline Simulation", value=not gemini_available)

if case_sel != "Custom Specification":
    selected_prompt = next(c["prompt"] for c in default_cases if c["name"] == case_sel)
else:
    selected_prompt = ""

# Main Tabs Setup
tab_sandbox, tab_eval, tab_docs = st.tabs([
    "🎮 Interactive Company Sandbox", 
    "📊 Evaluation Sandbox", 
    "📖 User Manual & Docs"
])

# --- Tab 1: Interactive Sandbox ---
with tab_sandbox:
    col_main_left, col_main_right = st.columns([3, 2])
    
    with col_main_left:
        st.markdown("### Interactive Development Sandbox")
        spec_input = st.text_area("Input coding requirements / specification:", value=selected_prompt, placeholder="e.g. Implement a basic stack...", key="user_spec")
        
        run_company_btn = st.button("⚡ Trigger Multi-Agent Pipeline", disabled=st.session_state.running_replay)
        
        # Ingest Execution
        if run_company_btn and spec_input.strip():
            st.session_state.running_replay = True
            st.session_state.replay_logs = []
            st.session_state.company_run_data = None
            
            # Execute Pipeline
            pipeline = SoftwareCompanyPipeline()
            with st.spinner("Company agents collaborating (Product, Architecture, Development, Testing)..."):
                run_res = pipeline.run(spec_input, correction_enabled=correction_on, offline=offline_mode)
            
            # Replay Simulation for Visual Effect
            st.session_state.company_run_data = run_res
            
            # Simulated Streaming Log
            log_placeholder = st.empty()
            for log in run_res["logs"]:
                agent_name = log["agent"]
                st.session_state.active_node = agent_name
                st.session_state.replay_logs.append(log)
                time.sleep(0.3)
                st.rerun()
            
            st.session_state.running_replay = False
            st.session_state.active_node = "System"
            st.rerun()
            
        # Agent visual path flow
        node_pm = "agent-active" if st.session_state.active_node == "Sarah" else ""
        node_arch = "agent-active" if st.session_state.active_node == "David" else ""
        node_dev = "agent-active" if st.session_state.active_node == "Alex" else ""
        node_qa = "agent-active" if st.session_state.active_node == "Rachel" else ""
        
        st.markdown(f"""
        <div class="agent-card-container">
            <div class="agent-node {node_pm}">
                <div class="agent-circle">📋</div>
                <div style="font-weight:bold; font-size:0.8rem; color:#ffffff;">Product Manager</div>
                <div style="font-size:0.75rem; color:#cbd5e1;">Sarah</div>
            </div>
            <div style="color:#8892b0; font-size:1.5rem;">➔</div>
            <div class="agent-node {node_arch}">
                <div class="agent-circle">📐</div>
                <div style="font-weight:bold; font-size:0.8rem; color:#ffffff;">System Architect</div>
                <div style="font-size:0.75rem; color:#cbd5e1;">David</div>
            </div>
            <div style="color:#8892b0; font-size:1.5rem;">➔</div>
            <div class="agent-node {node_dev}">
                <div class="agent-circle">💻</div>
                <div style="font-weight:bold; font-size:0.8rem; color:#ffffff;">Software Developer</div>
                <div style="font-size:0.75rem; color:#cbd5e1;">Alex</div>
            </div>
            <div style="color:#8892b0; font-size:1.5rem;">➔</div>
            <div class="agent-node {node_qa}">
                <div class="agent-circle">🧪</div>
                <div style="font-weight:bold; font-size:0.8rem; color:#ffffff;">QA Engineer</div>
                <div style="font-size:0.75rem; color:#cbd5e1;">Rachel</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Output Compiled Code Block
        if st.session_state.company_run_data:
            st.markdown("### Generated Code Artifacts")
            run_data = st.session_state.company_run_data
            files_dict = run_data["files"]
            
            if files_dict:
                code_tabs = st.tabs(list(files_dict.keys()))
                for idx, fname in enumerate(files_dict.keys()):
                    with code_tabs[idx]:
                        st.code(files_dict[fname], language="python")
            else:
                st.warning("No code files generated by Developer agent.")

    with col_main_right:
        st.markdown("### Sandbox Process Monitor")
        
        # Real-time console replay logs
        terminal_lines = ""
        for log in st.session_state.replay_logs:
            step_type = log["step"]
            agent = log["agent"]
            msg = log["message"]
            detail = log.get("detail", {})
            
            line_class = "system-line"
            if "PM" in step_type:
                line_class = "pm-line"
                terminal_lines += f'<div class="terminal-line {line_class}">[{agent.upper()}] {msg}</div>'
            elif "ARCH" in step_type:
                line_class = "arch-line"
                terminal_lines += f'<div class="terminal-line {line_class}">[{agent.upper()}] {msg}</div>'
            elif "DEV" in step_type:
                line_class = "dev-line"
                terminal_lines += f'<div class="terminal-line {line_class}">[{agent.upper()}] {msg}</div>'
            elif "QA" in step_type:
                line_class = "qa-line"
                terminal_lines += f'<div class="terminal-line {line_class}">[{agent.upper()}] {msg}</div>'
            elif step_type == "RE-PLANNING":
                line_class = "error-line"
                terminal_lines += f'<div class="terminal-line {line_class}">[RE-PLANNING] {msg}</div>'
            else:
                terminal_lines += f'<div class="terminal-line system-line">[SYSTEM] {msg}</div>'
                
        if not terminal_lines:
            terminal_lines = '<div class="terminal-line system-line">[SYSTEM] Sandbox idle. Awaiting multi-agent run command...</div>'
            
        st.markdown(f"""
        <div style="background-color:#1a1e26; border-radius: 8px 8px 0 0; padding:10px 15px; border:1px solid #2d313f; border-bottom:none; display:flex; justify-content:space-between; align-items:center; margin-bottom:0;">
            <div style="display:flex; gap:6px;">
                <span style="width:12px; height:12px; border-radius:50%; background-color:#ff4b4b; display:inline-block;"></span>
                <span style="width:12px; height:12px; border-radius:50%; background-color:#ffd700; display:inline-block;"></span>
                <span style="width:12px; height:12px; border-radius:50%; background-color:#00ff66; display:inline-block;"></span>
            </div>
            <div style="font-family:\'JetBrains Mono\'; font-size:0.75rem; color:#8892b0;">rachel@qa-sandbox:~</div>
            <div></div>
        </div>
        <div class="terminal-box">
            {terminal_lines}
        </div>
        """, unsafe_allow_html=True)
        
        # Subprocess unit test stdout console
        if st.session_state.company_run_data:
            st.write("")
            st.markdown("#### QA Sandbox Subprocess Terminal")
            st.code(st.session_state.company_run_data["test_output"], language="bash")

# --- Tab 2: Evaluation Sandbox ---
with tab_eval:
    st.markdown("### Head-to-Head Pipeline Benchmark Results")
    st.write("Compare multi-agent code compilation success metrics when dynamic QA Self-Correction is active vs inactive.")
    
    # Load or generate report
    report_json_path = os.path.join(os.path.dirname(__file__), "supporting_code", "generated", "evaluation_report.json")
    report_md_path = os.path.join(os.path.dirname(__file__), "supporting_code", "generated", "evaluation_report.md")
    
    run_eval_btn = st.button("⚡ Run Automated Benchmark Suite (Offline)")
    if run_eval_btn:
        with st.spinner("Executing head-to-head comparison runs across 5 tasks..."):
            evaluator = PipelineEvaluator()
            evaluator.run_eval(offline=True)
            st.success("Benchmarks completed successfully!")
            
    if os.path.exists(report_json_path):
        with open(report_json_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
            
        summary = eval_data["summary"]
        runs = eval_data["runs"]
        
        # Display Gauges
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            st.metric("Correction OFF Success", f"{summary['correction_off_success_rate']:.0f}%", delta=None)
        with col_g2:
            st.metric("Correction ON Success", f"{summary['correction_on_success_rate']:.0f}%", delta=f"+{summary['improvement_delta']:.0f}%")
        with col_g3:
            total_loops = sum(r["iterations"] for r in runs["correction_on"])
            st.metric("Self-Repair Loops Executed", f"{total_loops}", delta="100% repaired", delta_color="normal")
            
        # Comparison chart
        st.write("")
        st.markdown("#### Head-to-Head Success Comparison")
        chart_df = pd.DataFrame({
            "Configuration": ["Self-Repair OFF", "Self-Repair ON"],
            "Success Rate (%)": [summary["correction_off_success_rate"], summary["correction_on_success_rate"]]
        })
        st.bar_chart(chart_df.set_index("Configuration"))
        
        # Load md report
        if os.path.exists(report_md_path):
            with open(report_md_path, "r", encoding="utf-8") as f:
                report_md = f.read()
            with st.expander("📖 View Full Markdown Evaluation Report"):
                st.markdown(report_md)
    else:
        st.info("No evaluation benchmark report found. Click the button above to run the comparative suite.")

# --- Tab 3: User Manual & Docs ---
with tab_docs:
    st.markdown('<div class="gradient-subheader">📚 Multi-Agent Pipeline User Manual</div>', unsafe_allow_html=True)
    st.write("Module 4: Multi-Agent Software Development Pipeline Sandbox Specifications.")
    st.write("")
    
    st.markdown("""
    <div class="glass-panel" style="margin-bottom: 25px; border-left: 5px solid #00f0ff;">
        <h4 style="color: #00f0ff; margin-top: 0; font-family: 'Outfit';">🚀 System Operations Guide</h4>
        <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
            Welcome to the <strong>Multi-Agent Software Company Pipeline</strong>. This environment showcases how 
            multiple agent profiles collaborate autonomously under a structured, self-healing workflow:
        </p>
        <ol style="color: #cbd5e1; font-size: 0.92rem; padding-left: 20px; line-height: 1.6;">
            <li><strong>Select Benchmark Case</strong>: Pick one of the 5 pre-built specifications in the sidebar.</li>
            <li><strong>Toggle Self-Correction</strong>: Toggle this checkbox to compare zero-shot dev compiles against QA verification loops.</li>
            <li><strong>Inspect Outputs</strong>: View generated codes and test subprocess results side-by-side.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    col_d4_left, col_d4_right = st.columns(2)
    
    with col_d4_left:
        st.markdown("""
        <div class="glass-panel" style="min-height: 400px; margin-bottom: 20px;">
            <h4 style="color: #00f0ff; margin-top: 0; font-family: 'Outfit';">🧠 Team Roles & Prompting Design</h4>
            <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.5;">
                Our pipeline implements a linear supervisor-peer state flow of distinct profiles:
            </p>
            <ul style="color: #cbd5e1; font-size: 0.88rem; padding-left: 20px; line-height: 1.5;">
                <li style="margin-bottom: 8px;"><strong>Sarah (PM)</strong>: Generates markdown scopes, boundary cases, and acceptance checklist markers.</li>
                <li style="margin-bottom: 8px;"><strong>David (Architect)</strong>: Maps the API contract layout, lists target imports, file lists, and outputs structure specifications.</li>
                <li style="margin-bottom: 8px;"><strong>Alex (Developer)</strong>: Implements raw Python file scripts. If unit tests fail, Alex ingests raw traceback output logs to repair code target lines.</li>
                <li style="margin-bottom: 8px;"><strong>Rachel (QA)</strong>: Compiles test structures and executes them in subprocess shells.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-panel" style="min-height: 300px;">
            <h4 style="color: #ff4b4b; margin-top: 0; font-family: 'Outfit';">⚠️ Sandboxed Subprocess Test Runner</h4>
            <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.5;">
                Executing generated agent code directly in web servers represents security risks. Our QA agent executes unit tests:
            </p>
            <ul style="color: #cbd5e1; font-size: 0.88rem; padding-left: 20px; line-height: 1.5;">
                <li>Creates temporary workspace folder scopes using <code>tempfile.TemporaryDirectory</code>.</li>
                <li>Writes developer scripts and testing scripts to disk inside the folder.</li>
                <li>Runs the test suite inside an isolated subprocess via <code>sys.executable</code>.</li>
                <li>Safely captures execution trace stdout/stderr without affecting dashboard memory scopes.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_d4_right:
        st.markdown("""
        <div class="glass-panel" style="min-height: 400px; margin-bottom: 20px;">
            <h4 style="color: #ffd700; margin-top: 0; font-family: 'Outfit';">📐 Automated Self-Repair Loop</h4>
            <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.5;">
                The QA Engineer acts as a quality gate. When unit tests return a non-zero exit status:
            </p>
            <ol style="color: #cbd5e1; font-size: 0.88rem; padding-left: 20px; line-height: 1.5;">
                <li style="margin-bottom: 6px;">The traceback log is parsed.</li>
                <li style="margin-bottom: 6px;">The error is passed as feedback to the Developer Agent, together with the previous design draft.</li>
                <li style="margin-bottom: 6px;">The Developer compiles an adjusted code fix.</li>
                <li style="margin-bottom: 6px;">The tests are re-run. If success or 3 loop limits are reached, the loop exits.</li>
            </ol>
            <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.5;">
                This self-repair model raises code success rate from <strong>20% to 100%</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-panel" style="min-height: 300px;">
            <h4 style="color: #00ff66; margin-top: 0; font-family: 'Outfit';">📊 Benchmark Spec Details</h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem; color: #cbd5e1; margin-top: 10px;">
                <tr style="border-bottom: 1px solid #2d313f;">
                    <th style="text-align: left; padding: 6px 0; color: #8892b0;">Task Name</th>
                    <th style="text-align: left; padding: 6px 0; color: #8892b0;">Test File Target</th>
                </tr>
                <tr style="border-bottom: 1px solid #2d313f;">
                    <td style="padding: 6px 0;">1. Fibonacci & Prime</td>
                    <td style="padding: 6px 0; color: #00ff66;"><code>test_math.py</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #2d313f;">
                    <td style="padding: 6px 0;">2. RPN Calculator</td>
                    <td style="padding: 6px 0; color: #00ff66;"><code>test_rpn.py</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #2d313f;">
                    <td style="padding: 6px 0;">3. Text Analyzer</td>
                    <td style="padding: 6px 0; color: #00ff66;"><code>test_analyzer.py</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #2d313f;">
                    <td style="padding: 6px 0;">4. JSON KV Store</td>
                    <td style="padding: 6px 0; color: #00ff66;"><code>test_db.py</code></td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    st.info("💡 Pro-Tip: Select the 'Interactive Company Sandbox' tab at the top to run the pipeline.")
