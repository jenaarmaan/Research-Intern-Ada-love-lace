# Capstone Project (Assignment 5): AI Research Assistant with HITL Safety Gates

This directory contains the codebase, safety structures, automated evaluations, and interactive Streamlit dashboard for the **AI Research & Code-Gen Assistant** (Final Capstone Project - Module 5 Coursework).

---

## Project Structure

```bash
assignment-5/
├── streamlit_app.py                 # Main visual Streamlit dashboard
├── requirements.txt                 # Runtime dependencies list
├── README.md                        # Setup and operation guidelines
└── supporting_code/
    ├── research_pipeline.py         # Multi-agent roles, memory layers, guardrails, & subprocess REPL
    ├── evaluation.py                # Automated evaluation suite verifying standard/adversarial tasks
    └── generated/                   # Directory containing report summaries
        ├── evaluation_report.json   # Benchmark raw data logs
        └── evaluation_report.md     # Comparative markdown report
```

---

## Installation & Setup

1. Ensure you have python and standard development tools installed.
2. Install the required dependencies:

   ```bash
   pip install -r assignment-5/requirements.txt
   ```

3. Set up your Google Gemini API Key in the `.env` file at the repository root:

   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```

---

## Running the Application

To start the interactive Capstone dashboard:

```bash
streamlit run assignment-5/streamlit_app.py
```

---

## Dashboard Core Tabs

1. **Research Lab Sandbox**: Input research data requests, select scenario templates, monitor active agent nodes (Dr. Liam ➔ Dr. Elena ➔ Marcus ➔ Clara), check safety scans, and interact with the **Human-in-the-Loop (HITL)** permission panel to approve or block shell subprocess execution.
2. **Safety & Eval Inspector**: Gauges showing functional test success rates, prompt injection blocks, and average execution latencies.
3. **Project User Manual**: Detailed technical documentation of sandboxing boundaries and guardrail keywords.

---

## Command Line Benchmarks

You can also run evaluations directly from the shell:

```bash
python assignment-5/supporting_code/evaluation.py
```

This runs the 6-task benchmark sequence (5 functional research tasks + 1 prompt injection exploit) and automatically updates the report documents.
