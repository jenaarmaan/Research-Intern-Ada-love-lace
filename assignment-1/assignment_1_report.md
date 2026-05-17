# Agent Architecture Design & Analysis
## A Comparative Technical Report: Devin (Software Engineering) vs. Perplexity Pro Search (Information Retrieval)

---

### Executive Summary

In the evolution of Artificial Intelligence, a critical paradigm shift is occurring: transitioning from passive, single-turn conversational chatbots to **Autonomous Agentic Systems**. Agents do not merely respond; they perceive their environment, maintain an internal state, formulate multi-step plans, invoke external tools, and dynamically adapt their actions to achieve long-horizon goals.

This technical report provides a rigorous comparative architectural analysis of two state-of-the-art deployed agentic products:
1. **Devin (by Cognition Labs)**: An autonomous software engineering agent representing the *Task-Solving / Action-Oriented* category.
2. **Perplexity Pro Search (by Perplexity AI)**: An advanced search-and-retrieval agent representing the *Information-Synthesizing / Web-Scale Sensing* category.

Through the lenses of the **PEAS (Performance, Environment, Actuators, Sensors) framework** and the **Cognitive Agent Loop (Perceive-Reason-Plan-Act-Observe)**, this paper unpacks their core components (LLM brains, memory structures, tool integrations, planning strategies), delineates their architectural limitations, and provides formal design schematics for both systems.

---

### 1. PEAS Framework Analysis

The PEAS framework is a foundational methodology in Artificial Intelligence for defining, analyzing, and designing intelligent agents. Below is a structured comparative analysis of Devin and Perplexity Pro Search.

| PEAS Dimension | Devin (Cognition Labs) | Perplexity Pro Search |
| :--- | :--- | :--- |
| **Performance Measure (P)** | • Task completion rate on software benchmarks (e.g., SWE-bench)<br>• Code correctness & syntax accuracy<br>• Execution efficiency (time to solve, token consumption)<br>• Self-correction capability (compilation error resolution rate)<br>• User-rated task satisfaction | • Synthesis accuracy & factuality (minimized hallucinations)<br>• Source retrieval relevance and authority<br>• Query-to-answer latency (speed of response)<br>• Depth of exploration (comprehensive multi-hop answering)<br>• User feedback (upvotes, follow-up clarification rate) |
| **Environment (E)** | • **Highly Dynamic & Partially Observable**<br>• **Virtual Environment**: Isolated Docker container containing Linux OS, file systems, compilers, interpreters (Python, Node.js, etc.)<br>• **Remote Repository**: Git histories, dependency trees<br>• **Public Internet**: Browsing package registries, docs<br>• **Human-in-the-loop**: Interactive user chat | • **Highly Dynamic & Open-World**<br>• **World Wide Web**: Public index of billions of pages, search API backends (Google, Bing)<br>• **Live Data Streams**: News API feeds, real-time databases<br>• **Conversation Context**: User-provided query and session thread |
| **Actuators (A)** | • **Bash Terminal**: Executing system commands, scripts, builds<br>• **Code Editor**: Writing, patching, deleting files<br>• **Browser Engine**: Clicking, scrolling, navigating Chromium<br>• **User Chat Interface**: Querying user for credentials or clarifying instructions | • **Search Engine Queries**: Launching keyword/vector searches<br>• **Web Scrapers/HTTP Clients**: Fetching full HTML/Markdown text<br>• **Wolfram Alpha / Calculator**: Solving math equations<br>• **Response Generator**: Rendering structured answers with citations<br>• **UI Interface**: Providing interactive follow-up questions |
| **Sensors (S)** | • **Standard Streams**: Output of terminal executions (stdout, stderr)<br>• **File Reader**: Reading text/binary logs and code files<br>• **Web Browser View**: DOM hierarchy and screenshots of web pages<br>• **Compiler Logs & Test Harness Outputs**<br>• **Chat Inputs**: Receiving direct user messages | • **Search API Payloads**: Metadata, snippets, and page URLs<br>• **Web Scraping Outputs**: Raw webpage text contents<br>• **User Query Parser**: Semantic representation of user prompt<br>• **Conversation History Token Stream** |

#### PEAS Deep-Dive: Action vs. Retrieval
The differences in PEAS highlight their architectural divergence. 
- **Devin’s environment** is *active* and *generative*. Its actuators can modify the environment directly (e.g., writing a file, installing a library), creating immediate feedback loops. If Devin installs a library incorrectly, the compiler (sensor) provides an error (observation), requiring Devin to update its plan. This is a classic closed-loop control system.
- **Perplexity's environment**, by contrast, is *passive* and *read-only*. Its actuators do not change the web; they merely extract information from it. The primary engineering challenge for Perplexity is sorting through extremely noisy, high-volume open-world data (web search results) and synthesizing it into high-fidelity, factually accurate answers under strict latency constraints (seconds, compared to Devin's minutes or hours).

---

### 2. The Cognitive Agent Loop

Both agents operate on an infinite state machine loop based on the classic agentic cycle: **Perceive $\rightarrow$ Reason $\rightarrow$ Plan $\rightarrow$ Act $\rightarrow$ Observe**. However, their structural execution of this loop varies significantly to suit their task profiles.

```
                      +-----------------------------+
                      |          PERCEIVE           |
                      | (Collect Environment State) |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |           REASON            |
                      |  (Analyze & Evaluate Gaps)  |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |            PLAN             |
                      | (Hierarchical Task List/ToT)|
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |             ACT             |
                      |   (Call Actuators/Tools)    |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |           OBSERVE           |
                      |  (Inspect tool execution)  |
                      +--------------+--------------+
                                     |
                                     +-----------------------+
                                                             |
                                                             v
                                                   [Goal Accomplished?]
                                                    /               \
                                                  Yes                No
                                                  /                    \
                                       +-------------+        +-------------+
                                       | Return Task |        | Loop Again  |
                                       |   Result    |        | (Re-plan if |
                                       +-------------+        |   needed)   |
                                                              +-------------+
```

#### Devin's Execution Loop (Dynamic Action Loop)
Devin leverages a deep, recursive planning loop called **ReAct** (Reason + Action) blended with hierarchical tree-search (similar to LATS - Language Agent Tree Search):
1. **Perceive**: Collects current sandbox terminal stdout, editor buffer states, and compiler exit codes.
2. **Reason**: Analyzes the latest command output. If an error is detected (e.g., `ModuleNotFoundError: No module named 'flask'`), it reasons that the dependency is missing in the local environment.
3. **Plan**: Consults its hierarchical plan. Inserts a new sub-task: `"Install flask using pip"` immediately before the main run task.
4. **Act**: Invokes the `Bash` actuator, executing `pip install flask` inside the Docker sandbox.
5. **Observe**: Captures the installation logs and exit status ($0$ for success, non-zero for failure). The loop repeats.

#### Perplexity Pro Search's Loop (Information Routing Loop)
Perplexity uses a multi-hop reasoning loop (a hybrid of **Plan-and-Solve** and **Search Refinement**):
1. **Perceive**: Receives a complex user query (e.g., *"Compare the Q3 financial results of Apple and Microsoft and explain how AI capital expenditure impacted their margins"*).
2. **Reason**: Evaluates query complexity. It reasons that it cannot answer this in a single search because Q3 earnings reports are separate documents and financial metrics must be calculated sequentially.
3. **Plan**: Formulates a multi-stage search strategy:
   - *Sub-query 1*: "Apple Q3 earnings report CapEx and margins"
   - *Sub-query 2*: "Microsoft Q3 earnings report CapEx and margins"
   - *Sub-query 3*: "Comparison of Apple vs Microsoft margins AI CapEx impact"
4. **Act**: Simultaneously fires search API queries for Sub-query 1 and 2, collects top URLs, and fetches their contents.
5. **Observe**: Inspects parsed HTML pages. Extracted numerical figures (e.g., Apple CapEx = \$X billion, Microsoft = \$Y billion) are fed back into the reasoning engine.
6. **Reason (Phase 2)**: Processes the extracted figures. It notices that Apple's margin calculation is missing a specific component (e.g., research and development overheads).
7. **Re-Plan & Act**: Dynamically spins up a follow-up query: *"Apple Q3 R&D spending AI infrastructure"*, fetches the page, and observes the answer.
8. **Synthesize**: Once all steps are complete, it formats a highly organized Markdown response citing all sources.

---

### 3. Cognitive Subsystems

An autonomous agent's capabilities depend on three core cognitive abstractions: **Memory Systems**, **Tool-Use Mechanisms**, and **Planning Algorithms**.

```
                       +------------------------------+
                       |          LLM BRAIN           |
                       | (Cognitive Routing Engine)   |
                       +-------+------+.------+-------+
                               |      |       |
         +---------------------+      |       +---------------------+
         |                            |                             |
         v                            v                             v
+------------------+         +------------------+         +------------------+
|  MEMORY SYSTEMS  |         |    TOOL SYSTEM   |         |  PLANNING ENGINE |
| - Short-Term     |         | - Local Shell    |         | - Tree-of-Thought|
| - Episodic Logs  |         | - Web Browsing   |         | - ReAct / LATS   |
| - Vector Cache   |         | - Search APIs    |         | - Self-Correction|
+------------------+         +------------------+         +------------------+
```

#### A. Memory Systems
Memory architectures differentiate standard LLM prompt-completion patterns from production-grade agents.

- **Devin’s Memory Architecture**:
  - **Short-Term (Working Memory)**: Managed via context window sliding buffers. Contains the active codebase file paths, open terminal sessions, and current syntax errors.
  - **Episodic Memory**: A highly structured execution history log. Devin tracks all commands run, screenshots taken, and code changes made. If a plan path fails, Devin can "rewind" to a previous episodic state, restoring the workspace and trying an alternative path.
  - **Long-Term Memory**: Devin maintains a semantic database of common engineering patterns, API definitions, and previous successful runs across long sessions.
- **Perplexity Pro Search's Memory Architecture**:
  - **Short-Term**: Conversational state memory, passing previous query turns to keep context in multi-turn follow-up questions.
  - **Episodic (Session Memory)**: Tracks all URLs visited, summaries extracted, and search terms used *within the current query pipeline*. This prevents the agent from crawling the same webpage multiple times.
  - **Long-Term**: User profiles (custom instructions, search history trends) to personalize source preferences (e.g., prioritizing scholarly journals over social forums for scientific queries).

#### B. Tool-Use Mechanisms
Agents achieve real-world utility by interfacing with external tools.

- **Devin’s Tool Suite**:
  - *Actuator Tools*: A robust `BashTerminal` tool to execute makefiles, run test suites, or launch compilers. A `FileEditor` tool that doesn't just overwrite files but applies atomic `diff` patches, optimizing token transfer.
  - *Perception Tools*: A `WebBrowser` tool backed by Playwright/Chromium that takes visual screenshots and parses DOM elements, allowing Devin to test frontend changes or research online documentation.
- **Perplexity’s Tool Suite**:
  - *Retrieval Tools*: Aggregated Search Engines (Bing, Google, DuckDuckGo) used to identify index hits.
  - *Extraction Tools*: Custom high-performance web scrapers that bypass JS walls, cookie banners, and paywalls, delivering clean markdown segments.
  - *Computation Tools*: A sandboxed Python code interpreter or Wolfram Alpha API used to verify complex arithmetic calculations extracted from financial PDFs, preventing LLM arithmetic hallucination.

#### C. Planning Algorithms
Planning is the execution backbone that guides the LLM through complex multi-step objectives.

- **Devin’s Planning**: Devin relies heavily on **LATS (Language Agent Tree Search)** and hierarchical decompose-and-solve patterns. Given a task, it establishes a high-level DAG (Directed Acyclic Graph) of goals. During execution, it runs continuous evaluation functions ("LLM-as-a-Judge") to assess if the output of a step meets criteria. If a step fails, it backtracks on the plan graph and branches a new path.
- **Perplexity’s Planning**: Perplexity utilizes a linear **Plan-and-Execute** paradigm, layered with conditional branch evaluations. The planner decomposes the user query into sub-queries, executes them in parallel, evaluates the completeness of the compiled data, and conditionally issues additional queries if there are information gaps.

---

### 4. Architectural Limitations & Production Bottlenecks

Despite their advanced capabilities, both systems encounter critical engineering bottlenecks in real-world deployment.

#### Devin's Bottlenecks
1. **State Drift & Sandbox Pollution**: Running long-lived terminal sessions can pollute the virtual environment. A broken dependency installation on step 3 might break compilation on step 40, leading to "cascading degradation" of the sandbox state.
2. **Context Window Exhaustion**: Analyzing a large codebase causes rapid expansion of the active context window. Despite vector retrieval (RAG) of relevant code, complex bugs often require cross-file contexts that saturate context windows, increasing both latency and operational costs.
3. **Execution Loop Lock / Hallucination Traps**: If a unit test continues to fail, Devin can fall into "debugging loops"—repeatedly changing the same lines of code back and forth, burning tokens without making progress. It requires human-in-the-loop interrupts to break these cycles.

#### Perplexity Pro Search's Bottlenecks
1. **Information Quality & Synthesis Hallucination**: If the top search results contain conflicting or false information (e.g., SEO-optimized blog posts with inaccurate facts), Perplexity struggles to distinguish truth from authoritative-sounding falsehoods. It runs the risk of synthesizing incorrect data with polished, convincing prose.
2. **Search API Latency**: Issuing multi-hop searches sequentially compounds network latency. If one query takes $2$ seconds, a $3$-stage search takes $6+$ seconds, which is dangerously high for user-facing interactive apps.
3. **Dynamic Scraper Blocking**: Heavy anti-bot platforms (Cloudflare, Akamai) continuously block Perplexity's scraping IP ranges. If a critical source is blocked, the agent is blinded to that information, leading to degraded synthesis quality.

---

### 5. Architectural Comparison Matrix

| Architectural Feature | Devin (Task Solver) | Perplexity Pro Search (Info Retriever) |
| :--- | :--- | :--- |
| **Primary LLM Focus** | Code generation, reasoning, system debug | Fact extraction, synthesis, routing |
| **Execution Environment** | Stateful, write-access virtual sandbox | Stateless, read-only web scraper |
| **Planning Paradigm** | Non-linear Tree Search, Hierarchical DAG | Linear multi-hop decomposition, Parallel search |
| **Primary Tooling** | Shell terminal, File patcher, Browser | Web search APIs, HTML scrapers, Calculator |
| **Execution Duration** | Minutes to hours (long-lived state) | Seconds (real-time stream) |
| **Cost Profile** | High ($1-$10 per complex run) | Extremely low (sub-cent per search) |
| **Human-in-the-loop** | High (pauses for feedback, file shares) | Minimal (only post-response follow-up) |

---

### Conclusion & Future Paradigms

Devin and Perplexity Pro Search represent two highly successful but fundamentally distinct branches of Agentic AI. 

**Devin** excels at **manipulating local system state** to achieve generative coding outcomes. Its architecture is built around state management, execution feedback, and hierarchical non-linear planning.

**Perplexity Pro Search** excels at **distilling global open-world knowledge** under extreme latency requirements. Its architecture is optimized for fast web sensing, parallel multi-hop search routing, and clean synthesis.

As LLM context windows expand to millions of tokens and processing costs plummet, these two architectures are starting to merge. We are beginning to see coding agents equipped with web-scale search sensors, and search agents running long-lived local python sandboxes to analyze live datasets. The future belongs to hybrid, multi-agent frameworks where specialized agents like Devin and Perplexity collaborate dynamically to solve complex enterprise problems.
