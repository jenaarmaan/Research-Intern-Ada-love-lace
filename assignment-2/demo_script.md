# Video Demo Script: ReAct Agent Sandbox Explorer

**Role**: AI System Architect / DevOps Expert
**Duration**: ~5 Minutes
**Focus**: Demonstrating Autonomous Task-Solving, Sandboxed Tool Execution, and Dynamic Re-planning on Failure.

---

## Part 1: Introduction (0:00 - 0:45)

**[Visual: A professional AI Expert on camera, in front of a sleek dark-themed workspace. The background shows code diagrams or node trees.]**

**Speaker:**
> "Hello everyone! I'm an AI Systems Architect, and today I'm excited to walk you through our latest prototype: the **ReAct Agent Sandbox Explorer**.
>
> Modern autonomous systems are no longer just passive text engines. They need to perceive, think, plan, and execute actions in the real world.
>
> For Assignment 2, we built a fully autonomous task-solving agent modeled on the **ReAct (Reason and Act) paradigm**. What makes this agent unique is its ability to interact with isolated system tools, intercept traceback exceptions, and dynamically re-plan its strategy on the fly when things go wrong. Let's jump into the dashboard and see it in action."

---

## Part 2: Dashboard Overview & System Tools (0:45 - 1:45)

**[Visual: Screen recording showing the Streamlit dashboard on the 'Sandbox Playground' view. Highlight the Sidebar configurations and the Metrics Row.]**

**Speaker:**
> "This is our interactive playhouse. In the sidebar, you can load standard benchmarks or enter custom, multi-step queries.
>
> The system operates a dual-mode engine: it automatically uses Google's `google-genai` API when online, but degrades gracefully to an offline sandbox mode using string hashing when the network is down.
>
> Across the top metrics panel, you can monitor the agent's aggregate performance: the **Execution Success Rate**, the **Average Cognitive Steps**, and the count of **Total Failures Resolved** through dynamic self-repair."

**[Visual: Hover mouse over the tools list in the 'User Manual & Docs' tab.]**

**Speaker:**
> "The agent is equipped with three sandboxed tools:

1. Wikipedia Search Tool to fetch facts.
2. Resilient Web Scraper with automatic retry and mirror fallback mechanisms.
3. And an Isolated Python REPL Sandbox to execute code safely without risking parent server threads.

> Unlike standard linear pipelines, this tool suite allows the agent to check intermediate results and make decisions on the fly."

---

## Part 3: Live Run Demonstration (1:45 - 3:15)

**[Visual: Go back to the 'Sandbox Playground' tab, select the 'Buggy Code Runtime Correction' benchmark case, and click 'Run ReAct Agent Engine'.]**

**Speaker:**
> "Let's run a live demonstration. We'll load the **Buggy Code Runtime Correction** benchmark.
>
> The task spec is: *'Calculate the result of dividing 100 by the divisor variable (initially 0). Catch standard runtime exceptions (ZeroDivisionError) and correct it to divisor=5.'*
>
> When I click 'Run', notice the visual path visualizer glowing. The system cycles through state nodes: Standby ➔ Thought ➔ Action ➔ Observation."

**[Visual: Scroll down to the Interactive Real-Time Terminal on the right and point out the red warning lines and yellow update logs.]**

**Speaker:**
> "Look at the terminal output logs:

* The agent starts by thinking: *'I need to write a script to divide 100 by divisor 0.'*
* It executes the script in the Python REPL.
* The subprocess returns a **ZeroDivisionError** exception traceback.
* Instead of failing, the agent catches the traceback observation, triggers the **Re-planner**, updates the divisor variable to `5`, and updates its plan!
* The second execution compiles successfully, returning the final result of `20.0`."

---

## Part 4: Technical Specifications & Safety (3:15 - 4:30)

**[Visual: Switch navigation tabs to 'User Manual & Docs'. Point out the PEAS specification tables.]**

**Speaker:**
> "Under the hood, we formalize the agent using the PEAS framework. The sensors read text states, and the actuators commit changes to the sandbox.
>
> The web scraper simulates real-world network friction. If scraping the primary URL endpoint fails, the agent automatically shifts to a secondary mirror domain to pull data, ensuring 100% execution resilience.
>
> This prototype is fully verified against a suite of 10 distinct multi-step test runs, showing a massive increase in task completion rates when self-correcting logic is active."

---

## Part 5: Conclusion & Wrap-up (4:30 - 5:00)

**[Visual: Return to the AI expert on camera.]**

**Speaker:**
> "To summarize: we've developed an autonomous agent that doesn't just plan, but heals itself. By executing code in secure sub-processes, intercepting errors, and modifying execution stacks dynamically, this prototype is ready for real-world deployments.
>
> You can checkout the branch `assignment-2`, configure your Gemini API Key in the `.env` file, and run `streamlit run assignment-2/streamlit_app.py` to play with it yourself.
>
> Thank you so much for watching, and I look forward to taking any of your questions!"
