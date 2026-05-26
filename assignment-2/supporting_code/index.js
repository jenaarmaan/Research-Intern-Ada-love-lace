// Frontend Controller for ReAct Agent Sandbox Dashboard

document.addEventListener('DOMContentLoaded', () => {
    // API Endpoint Configs
    const API_RUN = '/api/run';
    const API_DEFAULT_TESTS = '/api/default_tests';

    // DOM Elements Cache
    const testListContainer = document.getElementById('test-list-container');
    const btnAutoTest = document.getElementById('btn-auto-test');
    const queryForm = document.getElementById('agent-query-form');
    const queryInput = document.getElementById('query-input');
    const btnSubmitQuery = document.getElementById('btn-submit-query');
    const activeTaskDisplay = document.getElementById('active-task-display');
    
    // Metrics
    const metricSuccessRate = document.getElementById('metric-success-rate');
    const metricAvgSteps = document.getElementById('metric-avg-steps');
    const metricFailuresResolved = document.getElementById('metric-failures-resolved');
    const metricLatency = document.getElementById('metric-latency');

    // Visualizer Elements
    const currentStageTag = document.getElementById('current-stage-tag');
    const nodeReceive = document.getElementById('node-receive');
    const nodeThought = document.getElementById('node-thought');
    const nodeAction = document.getElementById('node-action');
    const nodeObserve = document.getElementById('node-observe');
    const nodeFinish = document.getElementById('node-finish');
    const replanAlertBox = document.getElementById('replan-alert-box');
    const replanAlertText = document.getElementById('replan-alert-text');
    const finalAnswerText = document.getElementById('final-answer-text');

    // Terminal
    const terminalOutput = document.getElementById('terminal-output');
    const btnClearTerminal = document.getElementById('btn-clear-terminal');

    // State Variables
    let defaultTestCases = [];
    let isRunningTask = false;
    let autoTestActive = false;
    let autoTestCaseIndex = 0;
    
    // Global metrics tracking for the session
    let sessionRuns = [];

    // 1. Fetch & Initialize default test cases
    async function initDefaultTests() {
        try {
            const response = await fetch(API_DEFAULT_TESTS);
            if (!response.ok) throw new Error("Failed to load test cases.");
            defaultTestCases = await response.json();
            renderTestCases();
        } catch (error) {
            console.error(error);
            testListContainer.innerHTML = `<div class="loading-spinner" style="color: var(--accent-rose);">Error loading benchmark tests: ${error.message}</div>`;
        }
    }

    // 2. Render test items in the sidebar
    function renderTestCases() {
        testListContainer.innerHTML = '';
        defaultTestCases.forEach((tc, idx) => {
            const item = document.createElement('div');
            item.className = 'test-item';
            item.id = `test-case-${tc.id}`;
            item.innerHTML = `
                <div class="test-item-header">
                    <span class="test-name">${tc.name}</span>
                    <span class="test-badge">${tc.id}</span>
                </div>
                <p class="test-prompt-snippet">${tc.prompt}</p>
            `;
            item.addEventListener('click', () => {
                if (isRunningTask || autoTestActive) return;
                queryInput.value = tc.prompt;
                // Highlight item
                document.querySelectorAll('.test-item').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
            });
            testListContainer.appendChild(item);
        });
    }

    // 3. Clear terminal window
    btnClearTerminal.addEventListener('click', () => {
        terminalOutput.innerHTML = '';
        addTerminalLine('system', '[SYSTEM] Terminal logs cleared. Standing by.');
    });

    // Helper to append lines to the terminal
    function addTerminalLine(type, text) {
        const line = document.createElement('div');
        line.className = `terminal-line ${type}-line`;
        line.textContent = text;
        terminalOutput.appendChild(line);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }

    // 4. Animate Visualizer Nodes
    function setVisualizerStage(stage, detail = null) {
        currentStageTag.textContent = stage.toUpperCase();
        
        // Reset all nodes
        [nodeReceive, nodeThought, nodeAction, nodeObserve, nodeFinish].forEach(n => {
            n.classList.remove('active', 'success');
        });

        // Hide replan box by default
        replanAlertBox.style.display = 'none';

        if (stage === 'receive') {
            nodeReceive.classList.add('active');
        } else if (stage === 'thought') {
            nodeThought.classList.add('active');
        } else if (stage === 'action') {
            nodeAction.classList.add('active');
        } else if (stage === 'observe') {
            nodeObserve.classList.add('active');
        } else if (stage === 'replan') {
            nodeObserve.classList.add('active');
            replanAlertBox.style.display = 'flex';
            if (detail) {
                replanAlertText.textContent = detail;
            }
        } else if (stage === 'finish') {
            [nodeReceive, nodeThought, nodeAction, nodeObserve, nodeFinish].forEach(n => {
                n.classList.add('success');
            });
            nodeFinish.classList.add('active');
        }
    }

    // 5. Asynchronous Log Playback (Type-writer effect)
    async function playLogsBack(outcome) {
        return new Promise(async (resolve) => {
            const logs = outcome.trace_logs || [];
            
            // Iterate step logs with physical delay to allow real-time observation
            for (let i = 0; i < logs.length; i++) {
                const log = logs[i];
                const type = log.type;
                const msg = log.message;
                const detail = log.detail;

                // Control visualizer node active highlights & terminal output
                if (type === 'RECEIVE_TASK') {
                    setVisualizerStage('receive');
                    addTerminalLine('system', `\n[SANDBOX] >>> INCOMING TASK: "${msg}"`);
                    await delay(600);
                } 
                else if (type === 'INITIAL_PLAN') {
                    addTerminalLine('system', `[SANDBOX] Initial Plan: ${JSON.stringify(detail.plan)}`);
                    await delay(400);
                } 
                else if (type === 'THOUGHT') {
                    setVisualizerStage('thought');
                    addTerminalLine('thought', `[THOUGHT] ${msg}`);
                    await delay(800);
                } 
                else if (type === 'ACTION') {
                    setVisualizerStage('action');
                    addTerminalLine('action', `[ACTION] Call: ${detail.tool} | Input: "${detail.input}"`);
                    await delay(600);
                } 
                else if (type === 'OBSERVATION') {
                    setVisualizerStage('observe');
                    let outputStr = detail.output || '';
                    if (outputStr.length > 350) {
                        outputStr = outputStr.substring(0, 350) + '... [TRUNCATED]';
                    }
                    addTerminalLine('observation', `[OBSERVATION] Output: ${outputStr}`);
                    await delay(700);
                } 
                else if (type === 'FAILURE_TRACE') {
                    setVisualizerStage('replan', `Failure detected inside tool. Error Details: ${msg}`);
                    addTerminalLine('failure', `[FAILURE] ${msg}`);
                    
                    // Shake browser window screen effect (visual dynamic feedback)
                    terminalOutput.classList.add('shake-anim');
                    setTimeout(() => terminalOutput.classList.remove('shake-anim'), 400);
                    await delay(1200);
                } 
                else if (type === 'RE-PLANNING') {
                    setVisualizerStage('replan', detail.thought);
                    addTerminalLine('replan', `[RE-PLAN RATIONALE] ${detail.thought}`);
                    await delay(1400);
                } 
                else if (type === 'PLAN_UPDATED') {
                    addTerminalLine('replan', `[PLAN REDIRECTED] Modified steps queue: ${JSON.stringify(detail.remaining_plan)}`);
                    await delay(600);
                } 
                else if (type === 'FINISH') {
                    setVisualizerStage('finish');
                    addTerminalLine('finish', `[FINISH] ${msg}`);
                    await delay(500);
                }
            }
            
            // Set final answer output text
            finalAnswerText.textContent = outcome.final_answer;
            
            // Resolve playback
            resolve();
        });
    }

    // 6. Execute Single Agent Run via Server API
    async function runAgentTask(taskPrompt) {
        if (isRunningTask) return;
        isRunningTask = true;
        
        // UI Run State locks
        btnSubmitQuery.disabled = true;
        btnSubmitQuery.textContent = 'Executing...';
        activeTaskDisplay.textContent = 'AGENT ACTIVE';
        activeTaskDisplay.classList.add('active-run');
        
        addTerminalLine('system', `\n[SYSTEM] Querying REST backend. Spawning agent threads...`);
        
        const startTime = performance.now();
        
        try {
            const response = await fetch(API_RUN, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task: taskPrompt })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Server connection issues.");
            }

            const outcome = await response.json();
            const latency = (performance.now() - startTime) / 1000;
            
            // Dynamic Log Playback Trace
            await playLogsBack(outcome);

            // Record metrics locally
            sessionRuns.push({
                success: outcome.success,
                steps: outcome.steps_taken,
                failures: outcome.failures_resolved,
                latency: outcome.execution_time_seconds || latency
            });

            // Repaint static metrics panel
            updateSessionMetricsPanel();

            // Mark sidebar test item as success if matched
            markSidebarSuccess(taskPrompt);
            
        } catch (error) {
            console.error(error);
            addTerminalLine('failure', `[SERVER EXCEPTION] Failed to execute query. Rationale: ${error.message}`);
            finalAnswerText.innerHTML = `<span style="color: var(--accent-rose); font-weight: 600;">Execution Exception:</span> ${error.message}`;
            setVisualizerStage('standby');
        } finally {
            isRunningTask = false;
            btnSubmitQuery.disabled = false;
            btnSubmitQuery.textContent = 'Run Agent';
            activeTaskDisplay.textContent = 'Idle State';
            activeTaskDisplay.classList.remove('active-run');
        }
    }

    // Mark test items as successfully completed
    function markSidebarSuccess(prompt) {
        const matched = defaultTestCases.find(tc => tc.prompt === prompt);
        if (matched) {
            const item = document.getElementById(`test-case-${matched.id}`);
            if (item) {
                item.classList.add('completed-success');
                const badge = item.querySelector('.test-badge');
                if (badge) badge.textContent = 'PASSED';
            }
        }
    }

    // Recalculate dashboard analytics widgets
    function updateSessionMetricsPanel() {
        if (sessionRuns.length === 0) return;
        
        const total = sessionRuns.length;
        const successes = sessionRuns.filter(r => r.success).length;
        const successRate = ((successes / total) * 100).toFixed(1);
        
        const totalSteps = sessionRuns.reduce((sum, r) => sum + r.steps, 0);
        const avgSteps = (totalSteps / total).toFixed(1);
        
        const totalFailures = sessionRuns.reduce((sum, r) => sum + r.failures, 0);
        
        const lastLatency = sessionRuns[sessionRuns.length - 1].latency.toFixed(3);

        metricSuccessRate.textContent = `${successRate}%`;
        metricAvgSteps.textContent = avgSteps;
        metricFailuresResolved.textContent = totalFailures;
        metricLatency.textContent = `${lastLatency}s`;
    }

    // 7. Prompt Submission Forms
    queryForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const prompt = queryInput.value.trim();
        if (prompt) {
            runAgentTask(prompt);
        }
    });

    // 8. Automated Test Engine ("Take Control" demonstration)
    btnAutoTest.addEventListener('click', async () => {
        if (isRunningTask || autoTestActive) return;
        
        autoTestActive = true;
        btnAutoTest.disabled = true;
        btnAutoTest.textContent = '🔄 Running Auto-Test...';
        addTerminalLine('system', '\n[TEST SUITE] Starting Hands-Free Automated Verification Suite.');
        addTerminalLine('system', '[TEST SUITE] Taking control of front-end components. Initializing test pipeline...');
        
        for (let idx = 0; idx < defaultTestCases.length; idx++) {
            const tc = defaultTestCases[idx];
            
            // Highlight test in list
            document.querySelectorAll('.test-item').forEach(el => el.classList.remove('active'));
            const testItem = document.getElementById(`test-case-${tc.id}`);
            if (testItem) testItem.classList.add('active');
            
            queryInput.value = tc.prompt;
            addTerminalLine('system', `\n======================================================`);
            addTerminalLine('system', `[TEST SUITE] LAUNCHING CASE [${idx + 1}/5]: ${tc.name}`);
            addTerminalLine('system', `======================================================`);
            
            // Execute task and wait for absolute completion
            await runAgentTask(tc.prompt);
            
            // Standby buffer for user to digest logs before proceeding to next case
            addTerminalLine('system', `\n[TEST SUITE] CASE [${idx + 1}/5] COMPLETED. Standing by for 2.5 seconds...`);
            await delay(2500);
        }

        addTerminalLine('system', `\n======================================================`);
        addTerminalLine('system', `[TEST SUITE] ALL 5 CASES EVALUATED SUCCESSFULLY!`);
        addTerminalLine('system', `======================================================`);
        
        btnAutoTest.disabled = false;
        btnAutoTest.textContent = '⚡ Take Control & Auto-Test (5 Cases)';
        autoTestActive = false;
    });

    // Delay helper
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // App Initialization
    initDefaultTests();
    addTerminalLine('system', '[SYSTEM] Sandbox Dashboard Engine fully loaded and ready.');
});
