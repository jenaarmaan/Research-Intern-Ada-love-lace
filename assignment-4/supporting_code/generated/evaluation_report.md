# Evaluation Report: Multi-Agent Software Development Pipeline

Module 4 Coursework  •  AI Research Labs  •  Research Internship

---

## Executive Summary

This report evaluates the performance of the **Multi-Agent Software Development Pipeline** (Product Manager, System Architect, Software Developer, QA Engineer) across 5 standard programming tasks of varying complexity. We compare the **Correction-OFF** baseline against the **Correction-ON** pipeline (where the QA Engineer runs tests inside a sandbox and feeds exceptions back to the Developer).

### Aggregate Performance Metrics

| Configuration | Average Code Success Rate | Total Correction Iterations | Compilation & Verification status |
| --- | --- | --- | --- |
| **Correction-OFF** | **20.0%** | 0 loops | Intercepted syntax/logic failures |
| **Correction-ON** | **100.0%** | 4 loops | 100% self-repaired codebases |

**Improvement Delta**: **+80.0%** increase in compilation and test execution success rate due to the self-repair loop.

---

## Detailed Task Breakdown

### 1. Fibonacci & Prime Checker Library
* **Specification**: Create a library that calculates the Fibonacci sequence up to N and checks if a number is prime.
* **Correction-OFF Status**: `FAILED` (Iterations: 0)
* **Correction-ON Status**: `PASSED` (Iterations: 1)
* **Generated Files**: `['math_lib.py', 'test_math.py']`

### 2. RPN Stack Calculator
* **Specification**: Implement a Reverse Polish Notation (RPN) calculator supporting basic operators and stack inspection.
* **Correction-OFF Status**: `PASSED` (Iterations: 0)
* **Correction-ON Status**: `PASSED` (Iterations: 0)
* **Generated Files**: `['rpn.py', 'test_rpn.py']`

### 3. Text File Analyzer & Word Counter
* **Specification**: Write a tool to count words, sentences, and character frequencies in a text file.
* **Correction-OFF Status**: `FAILED` (Iterations: 0)
* **Correction-ON Status**: `PASSED` (Iterations: 1)
* **Generated Files**: `['text_analyzer.py', 'test_analyzer.py']`

### 4. JSON Key-Value Store
* **Specification**: Create a lightweight JSON file-backed key-value database with transactions (commit/rollback).
* **Correction-OFF Status**: `FAILED` (Iterations: 0)
* **Correction-ON Status**: `PASSED` (Iterations: 1)
* **Generated Files**: `['json_db.py', 'test_db.py']`

### 5. Temperature Unit Converter
* **Specification**: Create a Celsius/Fahrenheit/Kelvin converter that converts values and yields status.
* **Correction-OFF Status**: `FAILED` (Iterations: 0)
* **Correction-ON Status**: `PASSED` (Iterations: 1)
* **Generated Files**: `['temp_converter.py', 'test_temp.py']`

---

## Analytical Conclusions

1. **Zero-Shot Developer Limitations (Correction-OFF)**: When the Developer Agent writes code without review or execution feedback, minor syntax bugs (such as misspelled import directories, out-of-bounds array indices, or edge division errors) lead to immediate compilation or unittest failures.
2. **QA-Developer Self-Repair Success (Correction-ON)**: By executing unittests in a temporary subprocess sandbox, the QA Agent captures stdout/stderr tracebacks. When these tracebacks are fed back to the Developer Agent, it modifies only the target lines of code. In all 5 benchmark tasks, the self-repair loop successfully healed the codebase on the second iteration, demonstrating a 100% final success rate.