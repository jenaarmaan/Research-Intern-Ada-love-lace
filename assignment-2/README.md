# Assignment 2: Autonomous Task-Solving Agent with Tools
**Module 2 Coursework  •  Weightage: 20%**

---

## Overview

This directory contains the complete implementation for **Assignment 2: Autonomous Task-Solving Agent with Tools**.

The project builds an autonomous ReAct (Reason + Act) agent that solves complex multi-step reasoning tasks and dynamically re-plans its actions when tool executions fail (e.g., catching code exceptions or HTTP scrape timeouts). It incorporates:
1. **Tool-Use Integration**: Integrates Search, Web Scraping, and a sandboxed Python REPL execution tool.
2. **Dynamic Re-planning**: Intercepts observations, catches failures, dynamically updates remaining plan steps, and inserts self-correction sequences.
3. **10 Benchmark Scenarios**: Automatically evaluates on financial multihops, flaky scraper recovery, division by zero runtime fixes, recursive search population averages, and math puzzles.
4. **Interactive Streamlit Dashboard**: A premium visual interface featuring metrics counters, an animated cognitive node highlighter, a dynamic re-planning warning alert banner, and a scrolling interactive console terminal.

---

## Directory Structure

- `requirements.txt`: Package dependencies for Streamlit Cloud.
- `README.md`: This user guide.
- `streamlit_app.py`: Immersive Streamlit dashboard.
- `supporting_code/`:
  - `agent.py`: The ReAct agent state machine and planning router.
  - `tools.py`: Safe Python REPL sandbox, flaky scraper scraper, and mock search databases.
  - `evaluation_report.md`: Markdown evaluation summaries.
  - `server.py`: Legacy HTTP server (alternative raw HTML launch).

---

## Getting Started

### 🖥️ Local Installation
Install the required packages in your Python environment:

```bash
pip install -r assignment-2/requirements.txt
```

### 🚀 Running the Streamlit Web Application
Launch the Streamlit dashboard from the repository root:

```bash
streamlit run assignment-2/streamlit_app.py
```

### 💻 Running Console Benchmark Evaluations
To execute the automated evaluations directly in the terminal:

```bash
python assignment-2/supporting_code/run_5_tests.py
python assignment-2/supporting_code/benchmark.py
```
