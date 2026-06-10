# Assignment 1: Agent Architecture Design & Analysis
**Module 1 Coursework  •  Weightage: 15%**

---

## Overview

This directory contains the complete deliverables for **Assignment 1: Agent Architecture Design & Analysis** of the Agentic AI Curriculum. 

The assignment focuses on a comparative analysis of two leading deployed agentic architectures representing two different paradigms of autonomous operations:
1. **Devin (by Cognition Labs)**: An autonomous software engineering task-solving agent operating in a dynamic, write-access sandbox.
2. **Perplexity Pro Search (by Perplexity AI)**: An autonomous search-and-retrieval synthesizing agent operating at web scale under real-time constraints.

In addition to academic text papers and diagrams, this branch includes a **premium, interactive Streamlit Web Laboratory Dashboard** that lets you run and visualize the cognitive loops of both agents in real-time right inside your web browser!

---

## Deliverables Checklist

All required files have been fully implemented, verified, and placed on the `assignment-1` branch:

*   [x] **Comparative Technical Report**: A comprehensive, graduate-level 4-page academic analysis.
    *   File Path: [assignment_1_report.md](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/assignment_1_report.md)
*   [x] **Architecture Diagrams**: High-resolution, standalone Mermaid system layouts.
    *   Devin Schema: [devin_architecture.mermaid](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/devin_architecture.mermaid)
    *   Perplexity Schema: [perplexity_architecture.mermaid](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/perplexity_architecture.mermaid)
*   [x] **Interactive Web Laboratory (Streamlit)**: A browser-based GUI visualizer detailing plan DAG updates, glowing CRT consoles, local IDE editors, and search crawl logs.
    *   Web App: [streamlit_app.py](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/streamlit_app.py)
    *   Manifest: [requirements.txt](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/requirements.txt)
*   [x] **Console Simulations (CLI)**: Python scripts modeling the real-world cognitive loops of both agents with ANSI colored logging outputs.
    *   Devin Simulation: [mock_devin_agent.py](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/supporting_code/mock_devin_agent.py)
    *   Perplexity Simulation: [mock_perplexity_agent.py](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/supporting_code/mock_perplexity_agent.py)
*   [x] **Lab Sessions (Completed)**: Runnable Python scripts representing the Module 1 Lab tasks.
    *   Lab 1.1 (ReAct from Scratch): [lab_1_1_minimal_react.py](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/supporting_code/lab_1_1_minimal_react.py)
    *   Lab 1.2 (LangChain vs LlamaIndex Comparison): [lab_1_2_langchain_vs_llamaindex.py](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/supporting_code/lab_1_2_langchain_vs_llamaindex.py)

---

## Interactive Web Dashboard Features

Our Streamlit laboratory (`streamlit_app.py`) provides an immersive, educational simulation interface:
*   **Architecture Dashboard**: An elegant layout comparing the two agent systems under the PEAS framework, embedded with markdown code blocks showing Mermaid system routing graphs.
*   **Devin Sandbox Experience**: Runs the self-healing compiler loop step-by-step. You will see:
    *   A **Checklist Tracker** that updates colors (Pending $\rightarrow$ Completed) as goals are achieved.
    *   A **Glowing CRT Bash Terminal** outputs compiling trace errors and package installations in real time.
    *   A **Mock IDE Editor Window** displaying the active files of `app.py` as Devin edits it and patches errors.
*   **Perplexity Pro Search Console**: Allows entering complex queries and viewing:
    *   **Semantic Decompositions**: Breaking queries down into multi-hop plans.
    *   **Web Crawler Logs**: Visualizing active crawls, URL hits, page scrapes, and information-gap discovery.
    *   **Synthesized Citations**: Rendering final formatted responses cited with interactive clickable web indices.

---

## Execution and Local Launching

### 🖥️ Launching the Streamlit Web App Locally
Make sure you have Streamlit installed, then run the launcher script:

```bash
cd assignment-1
streamlit run streamlit_app.py
```

### 💻 Launching Console Scripts (Alternative)
Both agent simulation scripts can also be executed directly in your standard CLI shell:

```bash
cd assignment-1/supporting_code
python mock_devin_agent.py
python mock_perplexity_agent.py
```

---

## Cloud Deployment (Streamlit Community Cloud)

This app is 100% prepared for **zero-cost public hosting** via Streamlit Community Cloud:
1.  Push the `assignment-1` branch to your GitHub repository.
2.  Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3.  Click **"Deploy an App"** and choose your repository.
4.  Set the **Branch** to `assignment-1`.
5.  Set the **Main File Path** to `assignment-1/streamlit_app.py`.
6.  Click **Deploy**! Streamlit Cloud will automatically build your dependencies from `requirements.txt` and launch your live lab portal.
