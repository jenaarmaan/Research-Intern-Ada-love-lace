# Assignment 3: Memory-Augmented Personal Assistant Agent

Module 3 Coursework  •  Weightage: 20%

---

## Overview

This directory contains the complete implementation for **Assignment 3: Memory-Augmented Personal Assistant Agent**.

The project builds a personal assistant agent that maintains state and remembers past user interactions across multiple discrete sessions. It incorporates:

1. **Vector-based Episodic Memory**: Stores raw user exchanges, parses them into semantic vectors (using Gemini embeddings or local fallback), and retrieves relevant past context using Cosine Similarity.
2. **Reflection Engine**: Automatically or manually compiles fine-grained episodic memories into structured, high-level user insights (e.g., user preferences, project details, coding choices) that adapt and optimize the assistant's helpfulness.
3. **Session Management**: Simulates separate conversation sessions to show memory retention, context retrieval, and performance improvement over time.
4. **Evaluation Benchmarks**: Runs head-to-head simulations of **Memory-On** vs. **Memory-Off** configurations to empirically measure retrieval accuracy, response relevance, and context growth.
5. **Interactive Streamlit Lab Dashboard**: A premium, visual web app to interact with the agent, inspect the vector database and reflection logs, visualize the Knowledge Graph, and run automated evaluations.

---

## Directory Structure

- `requirements.txt`: Package dependencies.
- `README.md`: This user guide.
- `assignment_3_report.md`: Core technical report detailing the design, implementation, and evaluation findings.
- `streamlit_app.py`: Immersive Streamlit dashboard.
- `supporting_code/`:
  - `memory_agent.py`: Ephemeral/persistent vector memory, Reflection engine, and LLM-agent coordination using the Gemini API.
  - `evaluation.py`: Automated performance evaluations and comparison benchmarks.
  - `lab_runners.py`: Simulations for L3.1 (Context Window Summarization), L3.2 (Long-Term Vector Memory), and L3.3 (Knowledge Graph NetworkX visualization).

---

## Getting Started

### 🖥️ Local Installation

Install the required packages in your Python environment:

```bash
pip install -r assignment-3/requirements.txt
```

### 🔑 API Key Configuration

The application automatically reads the Gemini API key from the `.env` file at the repository root. Ensure the file contains:

```env
GEMINI_API_KEY=your_gemini_api_key
```

### 🚀 Running the Streamlit Web Application

Launch the Streamlit app from the repository root:

```bash
streamlit run assignment-3/streamlit_app.py
```

### 💻 Running Console Benchmark Evaluations

To run the evaluation benchmarks and output reports directly in the terminal:

```bash
python assignment-3/supporting_code/evaluation.py
```
