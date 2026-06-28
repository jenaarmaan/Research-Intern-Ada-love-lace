import streamlit as st
import os
import sys
import time
import json
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Ensure supporting_code is in the python path
sys.path.append(os.path.join(os.path.dirname(__file__), "supporting_code"))

from memory_agent import PersonalAssistantAgent, VectorEpisodicMemory, ReflectionEngine, gemini_available, api_key
from lab_runners import ContextManager, VectorMemoryShowcase, ConceptKnowledgeGraph
from evaluation import MemoryEvaluator

# Set up Streamlit page configuration
st.set_page_config(
    page_title="Ada Lovelace Memory Lab",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS styling injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;700&display=swap');
    
    /* Main body typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Gradient Headers */
    .gradient-header {
        background: linear-gradient(135deg, #00f0ff 0%, #ff4b4b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .gradient-subheader {
        background: linear-gradient(135deg, #00ff66 0%, #00f0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    /* Cards */
    .premium-card {
        background-color: #1a1c24;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2d313f;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        margin-bottom: 15px;
    }
    
    .metric-val {
        font-size: 2.2rem;
        font-weight: 800;
        color: #00f0ff;
        font-family: 'Outfit', sans-serif;
    }

    /* Badges */
    .status-badge-api {
        background: linear-gradient(90deg, #00f0ff 0%, #00ff66 100%);
        color: #0e1117;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .status-badge-sandbox {
        background: linear-gradient(90deg, #ff9900 0%, #ff4b4b 100%);
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Define file storage location
DB_FOLDER = os.path.join(os.path.dirname(__file__), "supporting_code", "memory_store")
os.makedirs(DB_FOLDER, exist_ok=True)

# Initialize Session State values
if "agent" not in st.session_state:
    st.session_state.agent = PersonalAssistantAgent(DB_FOLDER)
if "session_id" not in st.session_state:
    st.session_state.session_id = f"user_session_{int(time.time())}" if 'time' in sys.modules else "user_session_1"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "demo_step" not in st.session_state:
    st.session_state.demo_step = 0
if "demo_history" not in st.session_state:
    st.session_state.demo_history = []
if "eval_run" not in st.session_state:
    st.session_state.eval_run = False

# Refresh helper
def refresh_agent_states():
    st.session_state.agent = PersonalAssistantAgent(DB_FOLDER)

# Header Section
col_header_left, col_header_right = st.columns([3, 1])
with col_header_left:
    st.markdown('<div class="gradient-header">🧠 Ada Lovelace Memory Laboratory</div>', unsafe_allow_html=True)
    st.write("Module 3 Lab Dashboard: Vector Episodic Memory, Reflection Engines & Automated Evaluation.")
with col_header_right:
    st.write("")
    st.write("")
    if gemini_available:
        st.markdown('<span class="status-badge-api">📡 Gemini Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge-sandbox">🛡️ Sandbox Fallback Mode</span>', unsafe_allow_html=True)

# Sidebar Configuration Layout
st.sidebar.markdown("### ⚙️ Memory Configuration")
memory_on = st.sidebar.toggle("Enable Memory Engine", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Storage Monitor")
num_memories = len(st.session_state.agent.memory.memories)
num_insights = len(st.session_state.agent.reflection_engine.insights)

st.sidebar.metric("Raw Memories Stored", num_memories)
st.sidebar.metric("Extracted Insights", num_insights)

if st.sidebar.button("🧹 Reset Memory Storage"):
    st.session_state.agent.memory.clear()
    st.session_state.agent.reflection_engine.clear()
    st.session_state.chat_history = []
    st.session_state.demo_step = 0
    st.session_state.demo_history = []
    st.session_state.eval_run = False
    st.sidebar.success("Memory cleared!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Multi-Session Actions")
new_session_btn = st.sidebar.button("🔄 Start New Session Boundary")
if new_session_btn:
    import time
    st.session_state.session_id = f"user_session_{int(time.time())}"
    st.session_state.chat_history.append({"role": "system", "content": f"New session boundary created: `{st.session_state.session_id}`"})
    st.sidebar.success("Session ID updated!")

# Main Tabs Setup
tab_chat, tab_walkthrough, tab_inspector, tab_eval, tab_labs = st.tabs([
    "💬 Interactive Assistant", 
    "📈 Multi-Session Demo Walkthrough", 
    "🔍 Memory & Insights Inspector", 
    "📊 Evaluation Sandbox",
    "🧪 Lab Playground (L3.1 - L3.3)"
])

# --- Tab 1: Interactive Assistant ---
with tab_chat:
    st.markdown('<div class="gradient-subheader">Conversational Interface</div>', unsafe_allow_html=True)
    st.write("Interact with the Personal Assistant Agent. You can toggle memory on/off in the sidebar to see the immediate difference.")
    
    # Display chat logs
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])
                # Show expandable cognitive details
                if "trace" in msg:
                    with st.expander("🔬 View Memory Retrieval Engine Trace"):
                        trace = msg["trace"]
                        st.markdown(f"**Retrieval Mode**: `{'API Embedding' if gemini_available else 'Hash Vector Embedding'}`")
                        st.markdown(f"**Memories Queried**: {len(trace['retrieved_memories'])} matched")
                        
                        if trace['retrieved_memories']:
                            for m in trace['retrieved_memories']:
                                st.markdown(f"- *From {m['session_id']}*: **{m['content']}**")
                        else:
                            st.write("*No relevant episodic memory retrieved.*")
                            
                        st.markdown("**Active Insights Injected**:")
                        if trace['insights']:
                            for ins in trace['insights']:
                                st.markdown(f"- `{ins}`")
                        else:
                            st.write("*No insights available.*")
        elif msg["role"] == "system":
            st.info(msg["content"])
            
    # Chat Input Box
    user_input = st.chat_input("Enter your request...")
    if user_input:
        st.chat_message("user").write(user_input)
        
        # Execute agent run
        with st.spinner("Agent reasoning..."):
            agent_res = st.session_state.agent.run(
                user_input, 
                st.session_state.session_id, 
                memory_enabled=memory_on
            )
            
        with st.chat_message("assistant"):
            st.write(agent_res["response"])
            
        # Store trace metadata
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": agent_res["response"],
            "trace": {
                "retrieved_memories": agent_res["retrieved_memories"],
                "insights": agent_res["insights"]
            }
        })
        st.rerun()


# --- Tab 2: Multi-Session Demo Walkthrough ---
with tab_walkthrough:
    st.markdown('<div class="gradient-subheader">Guided 5-Session Walkthrough</div>', unsafe_allow_html=True)
    st.write("This tab runs a step-by-step demonstration of the **5+ User Sessions scenario** mentioned in the PDF. It models the agent's progressive improvement over time as memory accumulates and insights reflect.")
    
    # 5 standard walkthrough steps
    walkthrough_steps = [
        {
            "title": "Session 1: Introduction of Preferences",
            "desc": "The user introduces themselves, their project, and UI framework preference.",
            "query": "Hi, I'm Armaan. I'm a research intern working on the Ada Lovelace agent project. I prefer using Streamlit for UI prototypes."
        },
        {
            "title": "Session 2: Knowledge Recall Test",
            "desc": "In a fresh session boundary, the user asks to recall their name, project, and UI choice. (Tests episodic memory retrieval across sessions).",
            "query": "What project am I working on again, and what UI framework do I prefer?"
        },
        {
            "title": "Session 3: Feedback and Correction Ingestion",
            "desc": "The user updates their stack, switching database from ChromaDB to a NumPy vector store to bypass C++ compilation blocks.",
            "query": "Actually, we should switch our database focus from ChromaDB to a lightweight NumPy-based vector store because it has fewer installation issues."
        },
        {
            "title": "Session 4: Specialized Stack Recommendation",
            "desc": "The user asks for a recommendation. The assistant must combine the initial UI preference (Session 1) with the database correction (Session 3).",
            "query": "Can you suggest how I should implement our UI and database for the internship project?"
        },
        {
            "title": "Session 5: Personalized Code Generation",
            "desc": "The user requests code boilerplate. The agent produces tailored Streamlit + NumPy vector store code.",
            "query": "Please write a boilerplate code template for my project."
        }
    ]
    
    # Progress visualization
    progress_val = min(1.0, float(st.session_state.demo_step / 5.0))
    st.progress(progress_val, text=f"Scenario Progress: Step {st.session_state.demo_step} of 5")
    
    col_demo_left, col_demo_right = st.columns([1, 1])
    
    with col_demo_left:
        st.markdown("### Run Scenario Steps")
        
        # Display active step description
        if st.session_state.demo_step < 5:
            step = walkthrough_steps[st.session_state.demo_step]
            st.info(f"**Upcoming Step: {step['title']}**\n\n*Description*: {step['desc']}\n\n*Query*: \"{step['query']}\"")
            
            run_btn = st.button("🚀 Execute Step", key="run_walkthrough_step")
            if run_btn:
                session_id = f"demo_session_{st.session_state.demo_step + 1}"
                with st.spinner("Executing Turn..."):
                    # Execute agent
                    res = st.session_state.agent.run(step["query"], session_id, memory_enabled=True)
                    
                    # Store log
                    st.session_state.demo_history.append({
                        "step": st.session_state.demo_step + 1,
                        "title": step["title"],
                        "query": step["query"],
                        "response": res["response"],
                        "retrieved": [m["content"] for m in res["retrieved_memories"]],
                        "insights": list(res["insights"])
                    })
                    
                    st.session_state.demo_step += 1
                st.rerun()
        else:
            st.success("🎉 You have completed all 5 walkthrough sessions! The memory agent successfully learned the user name, role, UI preference, and database correction, showing continuous improvement.")
            if st.button("🔄 Restart Walkthrough Scenario"):
                st.session_state.demo_step = 0
                st.session_state.demo_history = []
                # Clear databases
                st.session_state.agent.memory.clear()
                st.session_state.agent.reflection_engine.clear()
                st.rerun()
                
    with col_demo_right:
        st.markdown("### Scenario Dialogue Trace")
        if not st.session_state.demo_history:
            st.write("No session steps executed yet. Click 'Execute Step' to begin.")
        else:
            for item in reversed(st.session_state.demo_history):
                with st.chat_message("user"):
                    st.write(f"**{item['title']}**")
                    st.write(f"*{item['query']}*")
                with st.chat_message("assistant"):
                    st.write(item["response"])
                    with st.expander("Cognitive Recollections"):
                        st.write("**Retrieved Episodic Memories:**", item["retrieved"] if item["retrieved"] else "None (Initial session context)")
                        st.write("**Active Insights:**", item["insights"] if item["insights"] else "None (Building insights...)")


# --- Tab 3: Memory & Insights Inspector ---
with tab_inspector:
    st.markdown('<div class="gradient-subheader">Internal Databases Inspector</div>', unsafe_allow_html=True)
    st.write("Explore raw database tables stored in JSON format inside the `assignment-3/supporting_code/memory_store/` directory.")
    
    col_ins_left, col_ins_right = st.columns(2)
    
    with col_ins_left:
        st.markdown("### 💾 Episodic Vector Memory Rows")
        if not st.session_state.agent.memory.memories:
            st.write("Episodic database is currently empty. Run chats or walkthroughs to populate.")
        else:
            for m in reversed(st.session_state.agent.memory.memories):
                with st.container():
                    st.markdown(f"**ID:** `{m['id']}` | **Session:** `{m['session_id']}` | **Role:** `{m['role'].upper()}`")
                    st.write(f"**Content:** {m['content']}")
                    # Show vector sample
                    st.caption(f"Vector Dimensions: {len(m['embedding'])} | Sample (first 5 values): {m['embedding'][:5]}")
                    st.markdown("---")
                    
    with col_ins_right:
        st.markdown("### 💡 Reflection Insight Database")
        if not st.session_state.agent.reflection_engine.insights:
            st.write("No compiled insights yet. Complete user turns or click reflect below to trigger.")
        else:
            st.write("High-level insights synthesized from dialogue streams:")
            for idx, ins in enumerate(st.session_state.agent.reflection_engine.insights):
                st.info(f"💡 **Insight {idx+1}**: {ins}")
                
        st.write("")
        if st.button("⚡ Force Reflection Compilation"):
            with st.spinner("Synthesizing memories..."):
                st.session_state.agent.reflection_engine.reflect(st.session_state.agent.memory.memories)
                refresh_agent_states()
            st.success("Reflection complete!")
            st.rerun()


# --- Tab 4: Evaluation Sandbox ---
with tab_eval:
    st.markdown('<div class="gradient-subheader">Head-to-Head Performance Benchmark</div>', unsafe_allow_html=True)
    st.write("Runs the evaluator suite benchmarking **Memory-ON** vs **Memory-OFF** configurations across the 5 standard session queries.")
    
    run_eval_btn = st.button("🚀 Run Automated Evaluation Benchmark", key="run_evaluation")
    
    eval_json_path = os.path.join(DB_FOLDER, "evaluation_report.json")
    eval_md_path = os.path.join(DB_FOLDER, "evaluation_report.md")
    
    if run_eval_btn:
        with st.spinner("Running evaluations. Please wait..."):
            evaluator = MemoryEvaluator(os.path.join(os.path.dirname(DB_FOLDER), "memory_store_eval_temp"))
            report = evaluator.run_benchmark()
            evaluator.save_reports(report, eval_json_path, eval_md_path)
            st.session_state.eval_run = True
            refresh_agent_states()
        st.success("Evaluation complete! Reports saved.")
        
    if os.path.exists(eval_json_path):
        try:
            with open(eval_json_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
                
            summary = report_data["summary"]
            
            # Metrics Row
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.markdown(
                    f'<div class="premium-card">Memory-ON Accuracy<br><span class="metric-val">{summary["memory_on_average_accuracy"] * 100:.1f}%</span></div>', 
                    unsafe_allow_html=True
                )
            with col_m2:
                st.markdown(
                    f'<div class="premium-card">Memory-OFF Accuracy<br><span class="metric-val">{summary["memory_off_average_accuracy"] * 100:.1f}%</span></div>', 
                    unsafe_allow_html=True
                )
            with col_m3:
                st.markdown(
                    f'<div class="premium-card">Improvement Delta<br><span class="metric-val">+{summary["improvement_delta"] * 100:.1f}%</span></div>', 
                    unsafe_allow_html=True
                )
                
            # Plotly/Matplotlib Plot
            st.markdown("### Accuracy Over Sessions Graph")
            mem_on_accs = [r["recall_accuracy"] * 100 for r in report_data["runs"]["memory_on"]]
            mem_off_accs = [r["recall_accuracy"] * 100 for r in report_data["runs"]["memory_off"]]
            session_labels = [f"Session {i}" for i in range(1, 6)]
            
            fig, ax = plt.subplots(figsize=(10, 4), facecolor="#0e1117")
            ax.set_facecolor("#1a1c24")
            
            # Plot line
            ax.plot(session_labels, mem_on_accs, marker='o', linewidth=3, color='#00f0ff', label='Memory-ON (Episodic + Reflection)')
            ax.plot(session_labels, mem_off_accs, marker='x', linestyle='--', linewidth=2, color='#ff4b4b', label='Memory-OFF (Zero-shot Baseline)')
            
            ax.set_ylim(-10, 110)
            ax.set_ylabel("Recall Accuracy (%)", color="#ffffff", fontweight="bold")
            ax.set_title("Head-to-Head Context Recall Benchmark", color="#ffffff", fontweight="bold", pad=15)
            ax.tick_params(colors='#ffffff')
            ax.grid(color='#2d313f', linestyle=':', alpha=0.6)
            
            # Legend color fix
            legend = ax.legend(loc="lower left", facecolor="#1a1c24", edgecolor="#2d313f")
            for text in legend.get_texts():
                text.set_color("#ffffff")
                
            # Border styling
            for spine in ax.spines.values():
                spine.set_color("#2d313f")
                
            st.pyplot(fig)
            
            # Walkthrough Table
            st.markdown("### Comparative Results Table")
            comparison_rows = []
            for i in range(5):
                r_on = report_data["runs"]["memory_on"][i]
                r_off = report_data["runs"]["memory_off"][i]
                comparison_rows.append({
                    "Session": f"Session {i+1}",
                    "User Request": r_on["query"],
                    "Memory-ON Response": r_on["response"],
                    "Memory-ON Recall Accuracy": f"{r_on['recall_accuracy']*100:.0f}%",
                    "Memory-OFF Response": r_off["response"],
                    "Memory-OFF Recall Accuracy": f"{r_off['recall_accuracy']*100:.0f}%"
                })
                
            st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True)
            
            # View Report PDF-like link
            st.markdown(f"**Saved Artifacts:**")
            st.markdown(f"- JSON data: [evaluation_report.json](file:///{eval_json_path.replace(os.sep, '/')})")
            st.markdown(f"- Formatted Report: [evaluation_report.md](file:///{eval_md_path.replace(os.sep, '/')})")
            
        except Exception as e:
            st.error(f"Error loading evaluation report: {e}")
    else:
        st.info("No evaluation report found. Click 'Run Automated Evaluation Benchmark' to run the benchmark suites.")


# --- Tab 5: Lab Session Playground ---
with tab_labs:
    st.markdown('<div class="gradient-subheader">Module 3 Lab Session Simulations</div>', unsafe_allow_html=True)
    st.write("Execute standalone interactive modules corresponding to Module 3 Lab Sessions.")
    
    lab_sel = st.selectbox("Select Lab Session", ["L3.1 - Context Window Summarization", "L3.2 - Long-Term Memory (Vector Showcase)", "L3.3 - Knowledge Graph Visualizer"])
    
    if lab_sel == "L3.1 - Context Window Summarization":
        st.markdown("### L3.1 Context Window Summarization")
        st.write("Simulates sliding windows and summarizing/compressing conversation logs when the context size exceeds memory limits.")
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("#### Configure Context limit")
            max_toks = st.slider("Max Context Token Threshold", 100, 1000, 300)
            
            st.markdown("#### Sample Conversation turns")
            st.text_area("Turn 1 (User)", "Hi, I'm Armaan. I'm a research intern working on the Ada Lovelace agent project.", key="t1")
            st.text_area("Turn 2 (Assistant)", "Nice to meet you Armaan. I will assist you with the Ada Lovelace project.", key="t2")
            st.text_area("Turn 3 (User)", "I prefer using Streamlit for UI prototyping, and we should use a custom NumPy vector store for long-term memory backend to avoid ChromaDB installation issues.", key="t3")
            st.text_area("Turn 4 (Assistant)", "Got it! I will remember to recommend Streamlit and NumPy vector store.", key="t4")
            st.text_area("Turn 5 (User)", "Great! Now, could you summarize our current preferences?", key="t5")
            
        with col_c2:
            st.markdown("#### Compression Execution")
            run_compress_btn = st.button("⚡ Run Context Compression")
            if run_compress_btn:
                cm = ContextManager(max_toks)
                cm.add_message("user", st.session_state.t1)
                cm.add_message("assistant", st.session_state.t2)
                cm.add_message("user", st.session_state.t3)
                cm.add_message("assistant", st.session_state.t4)
                cm.add_message("user", st.session_state.t5)
                
                initial_toks = cm.get_total_tokens()
                st.write(f"**Total Tokens in Raw Chat History**: `{initial_toks}` words/tokens.")
                
                if initial_toks > max_toks:
                    st.warning(f"⚠️ Context limit exceeded! Threshold is {max_toks}. Triggering compression...")
                    # Initialize API client if available
                    api_client = None
                    if gemini_available:
                        from google import genai
                        api_client = genai.Client(api_key=api_key.strip())
                        
                    summary, b, a = cm.compress_context(api_client)
                    st.info(f"**Derived Summary Insight**:\n\n{summary}")
                    st.success(f"**Compression Ratio**: `{b}` tokens compressed down to `{a}` tokens! (Reduction: `{(1 - a/b)*100:.1f}%`)")
                    
                    st.markdown("**Compressed Active Context Queue:**")
                    st.json(cm.history)
                else:
                    st.success(f"✅ Total tokens `{initial_toks}` is under the limit of `{max_toks}`. No compression needed.")
                    
    elif lab_sel == "L3.2 - Long-Term Memory (Vector Showcase)":
        st.markdown("### L3.2 Long-Term Vector Memory Operations")
        st.write("Demonstrates how chunks of user profiles are parsed, embedded, and queried in a localized Vector Store.")
        
        showcase_docs = [
            {"id": "doc_1", "text": "Armaan is a Research Intern working on the Ada Lovelace agent project."},
            {"id": "doc_2", "text": "The user prefers using Streamlit for rapid UI prototyping."},
            {"id": "doc_3", "text": "To avoid installation blocks on Windows, the user corrected the database backend to a NumPy-based vector store."},
            {"id": "doc_4", "text": "Deep Learning architectures commonly use vector databases to manage conversational episodic streams."}
        ]
        
        # Instantiate agent memory embedding function wrapper
        embedding_fn = lambda txt: st.session_state.agent.memory.embed_text(txt)
        showcase = VectorMemoryShowcase(embedding_fn)
        
        st.markdown("#### Embedded Knowledge Store")
        for doc in showcase_docs:
            showcase.add_chunk(doc["id"], doc["text"])
            
        st.dataframe(pd.DataFrame([{"ID": d["id"], "Fact Chunk": d["text"]} for d in showcase_docs]), use_container_width=True)
        
        st.markdown("#### Semantic Query Sandbox")
        query_val = st.text_input("Enter a semantic query to search memory:", "What database is preferred for the Lovelace project?")
        
        if query_val:
            results = showcase.search(query_val, k=2)
            
            st.markdown("**Top Similarity Search Matches:**")
            for idx, (txt, sim) in enumerate(results):
                st.info(f"🎯 **Match {idx+1}** (Cosine Similarity: `{sim:.4f}`):\n\n> {txt}")
                
            # Sample Vector Values
            q_vector = embedding_fn(query_val)
            st.caption(f"Query Vector (Sample coordinates 1-5): {q_vector[:5]}")
            
    elif lab_sel == "L3.3 - Knowledge Graph Visualizer":
        st.markdown("### L3.3 Concept Knowledge Graph")
        st.write("Builds and visualizes a dynamic context Knowledge Graph mapping user identities, technologies, and rules.")
        
        col_g1, col_g2 = st.columns([1, 2])
        
        with col_g1:
            st.markdown("#### Add Graph Relationships")
            src = st.text_input("Source Node", "Armaan")
            tgt = st.text_input("Target Node", "Python")
            rel = st.text_input("Relationship Edge Label", "DEVELOP_IN")
            
            kg_maker = ConceptKnowledgeGraph()
            
            if st.button("➕ Add Node & Link to Graph"):
                kg_maker.add_concept(src, tgt, rel)
                st.success("Edge registered!")
                
        with col_g2:
            st.markdown("#### Generated NetworkX Graph")
            kg_maker = ConceptKnowledgeGraph()
            # If user added relationships in session state, we preserve them
            if "custom_edges" not in st.session_state:
                st.session_state.custom_edges = []
            if src and tgt and rel and st.button("Regenerate Plot"):
                st.session_state.custom_edges.append((src, tgt, rel))
                
            for s, t, r in st.session_state.custom_edges:
                kg_maker.add_concept(s, t, r)
                
            img_path = os.path.join(DB_FOLDER, "knowledge_graph.png")
            kg_maker.render_graph(img_path)
            
            if os.path.exists(img_path):
                st.image(img_path, caption="Active Memory-Augmented Knowledge Graph Visualization")
