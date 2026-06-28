# Assignment 4: Multi-Agent Software Development Pipeline

This directory contains the codebase, evaluation framework, and interactive Streamlit dashboard for the **Multi-Agent Software Development Pipeline** (Module 4 Coursework).

---

## Project Structure

```bash
assignment-4/
├── streamlit_app.py                 # Main visual Streamlit dashboard
├── requirements.txt                 # Runtime dependencies list
├── README.md                        # Setup and operation guidelines
└── supporting_code/
    ├── multi_agent_system.py        # PM, Architect, Developer, QA Agent profiles & orchestration
    ├── evaluation.py                # Comparative benchmark suite execution runner
    └── generated/                   # Directory containing report summaries
        ├── evaluation_report.json   # Benchmark raw data logs
        └── evaluation_report.md     # Comparative markdown report
```

---

## Installation & Setup

1. Ensure you have python and standard development tools installed.
2. Install the required dependencies:

   ```bash
   pip install -r assignment-4/requirements.txt
   ```

3. Set up your Google Gemini API Key in the `.env` file at the repository root:

   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```

---

## Running the Application

To start the interactive DevOps simulation dashboard:

```bash
streamlit run assignment-4/streamlit_app.py
```

---

## Dashboard Core Tabs

1. **Interactive Company Sandbox**: Ingest requirements, configure QA repair loops, watch real-time node transitions (Sarah ➔ David ➔ Alex ➔ Rachel), view generated files, and read live unit test printouts.
2. **Evaluation Sandbox**: Run head-to-head metrics comparing pipeline performance with correction active vs inactive.
3. **User Manual & Docs**: Full technical specifications of subprocess scopes, test run gates, and state flow models.

---

## Command Line Benchmarks

You can also run evaluations directly from the shell:

```bash
python assignment-4/supporting_code/evaluation.py
```

This runs the 5-task benchmark sequence and automatically updates the report documents.
