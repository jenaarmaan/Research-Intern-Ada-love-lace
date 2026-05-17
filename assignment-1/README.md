# Assignment 1: Agent Architecture Design & Analysis
**Module 1 Coursework  •  Weightage: 15%**

---

## Overview

This directory contains the complete deliverables for **Assignment 1: Agent Architecture Design & Analysis** of the Agentic AI Curriculum. 

The assignment focuses on a comparative analysis of two leading deployed agentic architectures representing two different paradigms of autonomous operations:
1. **Devin (by Cognition Labs)**: An autonomous software engineering task-solving agent operating in a dynamic, write-access sandbox.
2. **Perplexity Pro Search (by Perplexity AI)**: An autonomous search-and-retrieval synthesizing agent operating at web scale under real-time constraints.

---

## Deliverables Checklist

All required files have been fully implemented, verified, and placed on the `assignment-1` branch:

*   [x] **Comparative Technical Report**: A comprehensive, graduate-level 4-page academic analysis.
    *   File Path: [assignment_1_report.md](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/assignment_1_report.md)
*   [x] **Architecture Diagrams**: High-resolution, standalone Mermaid system layouts.
    *   Devin Schema: [devin_architecture.mermaid](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/devin_architecture.mermaid)
    *   Perplexity Schema: [perplexity_architecture.mermaid](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/perplexity_architecture.mermaid)
*   [x] **Supporting Code (Simulations)**: Fully functional Python scripts modeling the real-world cognitive loops of both agents with ANSI colored logging outputs.
    *   Devin Simulation: [mock_devin_agent.py](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/supporting_code/mock_devin_agent.py)
    *   Perplexity Simulation: [mock_perplexity_agent.py](file:///d:/projects/Research%20Intern%20-%20Ada%20love%20lace/assignment-1/supporting_code/mock_perplexity_agent.py)

---

## Architectural Highlights

### PEAS Framework Quick-Comparison

| Dimension | Devin (Action-Oriented) | Perplexity Pro Search (Information-Oriented) |
| :--- | :--- | :--- |
| **Performance (P)** | Task completion rate (SWE-bench), compile success | Synthesis factuality, source relevance, latency |
| **Environment (E)** | Stateful, write-access virtual OS sandbox | Stateful, read-only open-world Wide Web index |
| **Actuators (A)** | Shell execution, File system patcher, Chromium Browser | Search query routing, HTML crawler, Calculator |
| **Sensors (S)** | Terminal streams (stdout/stderr), compiler exit codes | Search API payloads, HTML text scraper, query intent |

### Cognitive Subsystems

*   **Memory**: Devin utilizes deep **Episodic Memory Logs** to allow system state rewinds and plan backtracking on test failures. Perplexity utilizes a light **Episodic Session Cache** of visited URLs and extracted facts to resolve multi-hop information extraction without redundant crawls.
*   **Planning**: Devin uses non-linear **Language Agent Tree Search (LATS)** to construct hierarchical DAG plans. Perplexity utilizes a linear **Plan-and-Execute** routine with dynamic **Gap Detection** follow-up branches.
*   **Tool-Use**: Devin operates using local, state-modifying OS tool interfaces (Bash Shell, VS-Code Workspace APIs). Perplexity operates using globally distributed API search gateways and anti-bot scraping scrapers.

---

## Execution Instructions

Both agent simulation scripts are written in plain Python 3 with zero external package dependencies, ensuring they execute immediately in any terminal context without environment setups.

### Running Devin Sandbox Agent Simulation
Devin simulates a ReAct loop: writing a Flask script with a syntax error, executing it, receiving a compiler traceback, detecting a missing library, installing the library, re-running, receiving a syntax error, applying an editor patch, and successfully verifying routing.

```bash
cd assignment-1/supporting_code
python mock_devin_agent.py
```

### Running Perplexity Pro Search Agent Simulation
Perplexity simulates a multi-hop query: taking a complex request, decomposing it, executing parallel Google/Bing search APIs, crawling/scraping pages, identifying information gaps (missing budget figures), firing a targeted secondary query, calculating results, and rendering a markdown report with cited sources.

```bash
cd assignment-1/supporting_code
python mock_perplexity_agent.py
```
