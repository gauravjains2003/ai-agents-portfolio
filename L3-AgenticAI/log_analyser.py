# ============================================================
# L3 Agentic AI — Log Analyser (Custom Agent Loop)
# Concept: Manual ReAct loop — Thought, Action, Observation
# ============================================================

import json
import re
import os
import datetime
import ollama

# ============================================================
# TOOLS
# ============================================================

def read_log_file(filepath: str) -> str:
    """Read a log file and return its contents."""
    try:
        filepath = filepath.strip().strip('"').strip("'")
        if not os.path.exists(filepath):
            return f"ERROR: File not found at {filepath}"
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.split("\n")
        return f"Log file loaded. Total lines: {len(lines)}\n\n{content}"
    except Exception as e:
        return f"ERROR reading file: {str(e)}"

def search_errors(log_content: str) -> str:
    """Search log content and extract all error lines."""
    error_patterns = [
        "ERROR", "FATAL", "CRITICAL", "Exception",
        "ORA-", "SQLSTATE", "Connection refused",
        "Timeout", "OutOfMemory", "NullPointer"
    ]
    lines = log_content.split("\n")
    errors_found = []
    for i, line in enumerate(lines):
        for pattern in error_patterns:
            if pattern.upper() in line.upper():
                errors_found.append(f"Line {i+1}: {line.strip()}")
                break
    if not errors_found:
        return "No errors found."
    return f"Found {len(errors_found)} errors:\n" + "\n".join(errors_found)

def get_error_timeline(log_content: str) -> str:
    """Extract timestamps from error lines."""
    lines = log_content.split("\n")
    timeline = []
    for line in lines:
        is_error = any(p in line.upper() for p in
                      ["ERROR", "FATAL", "CRITICAL", "ORA-"])
        if is_error:
            match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", line)
            if match:
                timeline.append(f"[{match.group()}] {line.strip()[:80]}")
    if not timeline:
        return "No timestamped errors found."
    return f"Timeline ({len(timeline)} events):\n" + "\n".join(timeline)

def check_knowledge_base(error_code: str) -> str:
    """Look up known errors and fixes."""
    kb = {
        "ORA-12541": "TNS no listener. Fix: Run 'lsnrctl start'. Team: DBA",
        "ORA-00942": "Table not found. Fix: Check schema/privileges. Team: DBA",
        "ORA-01017": "Invalid credentials. Fix: Reset password/unlock account. Team: DBA",
        "CONNECTION REFUSED": "Service down. Fix: Check service status and firewall. Team: Infra",
        "OUTOFMEMORY": "Heap exhausted. Fix: Increase JVM heap -Xmx4g. Team: App Team",
        "TIMEOUT": "Operation timed out. Fix: Check DB/network performance. Team: Performance"
    }
    error_upper = error_code.upper().strip()
    for key, value in kb.items():
        if key in error_upper or error_upper in key:
            return f"KB Match [{key}]: {value}"
    return f"No KB entry for: {error_code}. Escalate to L2 Support."

def generate_report(summary: str) -> str:
    """Generate and save a formatted incident report."""
    ticket_id = f"AGT{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""
╔══════════════════════════════════════════════════════╗
║      L3 AGENTIC AI — INCIDENT REPORT                 ║
╚══════════════════════════════════════════════════════╝
  Ticket ID : {ticket_id}
  Generated : {timestamp}
──────────────────────────────────────────────────────
{summary}
══════════════════════════════════════════════════════"""
    os.makedirs("reports", exist_ok=True)
    filepath = f"reports/{ticket_id}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    return f"Report saved to {filepath}"

# Tool registry — agent looks up tools here
TOOLS = {
    "read_log_file": read_log_file,
    "search_errors": search_errors,
    "get_error_timeline": get_error_timeline,
    "check_knowledge_base": check_knowledge_base,
    "generate_report": generate_report
}

# ============================================================
# CUSTOM REACT AGENT LOOP
# ============================================================

def run_agent(goal: str):
    print(f"\n🤖 Agent Goal: {goal}")
    print("="*55)

    # Agent memory — stores everything that happened
    memory = []
    log_content_cache = ""

    # System prompt — simple and direct for llama3.1
    system_prompt = """You are an IT incident analyst agent. 
You solve problems step by step using tools.

Available tools:
- read_log_file: input = filepath
- search_errors: input = log content
- get_error_timeline: input = log content  
- check_knowledge_base: input = error code like ORA-12541
- generate_report: input = full summary text

Respond with ONLY this JSON format:
{
  "thought": "what you are thinking",
  "action": "tool_name or DONE",
  "input": "input for the tool"
}

When all investigation is complete, set action to DONE and input to final summary."""

    # Build initial message
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Goal: {goal}\n\nStart your investigation."}
    ]

    max_steps = 8
    step = 0

    while step < max_steps:
        step += 1
        print(f"\n--- Step {step} ---")

        # Call LLM
        response = ollama.chat(
            model="llama3.1",
            messages=messages
        )

        raw = response["message"]["content"].strip()

        # Clean JSON if LLM wrapped in markdown
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        # Parse JSON response
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group())
                except:
                    print(f"⚠ Could not parse response, retrying...")
                    messages.append({"role": "assistant", "content": raw})
                    messages.append({"role": "user", "content": 
                        "Respond with ONLY valid JSON in the format specified."})
                    continue
            else:
                print(f"⚠ No JSON found, retrying...")
                continue

        thought = parsed.get("thought", "")
        action = parsed.get("action", "")
        tool_input = parsed.get("input", "")

        print(f"💭 Thought: {thought}")
        print(f"⚡ Action : {action}")
        print(f"📥 Input  : {str(tool_input)[:80]}...")

        # Check if agent is done
        if action.upper() == "DONE":
            print("\n✅ Agent completed investigation.")
            generate_report(tool_input)
            break

        # Execute tool
        if action in TOOLS:
            # Use cached log content for tools that need it
            if action in ["search_errors", "get_error_timeline"] and log_content_cache:
                observation = TOOLS[action](log_content_cache)
            else:
                observation = TOOLS[action](str(tool_input))

            # Cache log content for reuse
            if action == "read_log_file" and "ERROR" not in observation[:20]:
                log_content_cache = observation

            print(f"👁 Result : {observation[:150]}...")

            # Add to conversation memory
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": 
                f"Observation: {observation}\n\nContinue your investigation."})

            memory.append({
                "step": step,
                "thought": thought,
                "action": action,
                "result": observation[:200]
            })
        else:
            print(f"⚠ Unknown tool: {action}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": 
                f"Tool '{action}' not found. Available: {list(TOOLS.keys())}"})

    if step >= max_steps:
        print("\n⚠ Max steps reached. Generating report with findings so far.")
        summary = "\n".join([f"Step {m['step']}: {m['action']} - {m['result'][:100]}" 
                            for m in memory])
        generate_report(summary)

# ============================================================
# SAMPLE LOG GENERATOR
# ============================================================

def create_sample_log():
    log_content = """2026-05-28 01:45:00 INFO  Application started successfully
2026-05-28 01:45:01 INFO  Database connection pool initialized (size=10)
2026-05-28 02:00:00 INFO  Batch job DAILY_RECONCILIATION started
2026-05-28 02:03:22 ERROR Database connection lost: ORA-12541 TNS no listener
2026-05-28 02:03:23 ERROR Batch job DAILY_RECONCILIATION failed after 3 retries
2026-05-28 02:03:24 FATAL Connection refused on port 1521 - database unreachable
2026-05-28 02:05:00 ERROR User login attempt failed - Connection refused to auth service
2026-05-28 02:05:45 ERROR OutOfMemory: Java heap space in SessionManager
2026-05-28 02:06:00 ERROR 142 concurrent users affected by auth service failure
2026-05-28 02:10:05 ERROR Reconnection timeout after 5000ms
2026-05-28 02:15:00 ERROR ORA-12541 persists - escalation required
2026-05-28 02:45:00 INFO  Database listener restarted by DBA team
2026-05-28 02:45:30 INFO  Connection pool re-established
2026-05-28 03:00:00 INFO  All systems operational"""

    with open("sample_app.log", "w") as f:
        f.write(log_content)
    print("✓ Sample log created: sample_app.log")

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("L3 Agentic AI — Log Analyser")
    print("Custom ReAct Loop + llama3.1 (local)\n")

    create_sample_log()

    run_agent(
    "Analyse the log file at this exact path: C:\\AIPortfolio\\L3-AgenticAI\\sample_app.log "
    "Find all errors, build a timeline, "
    "check knowledge base for ORA-12541 and Connection refused errors, "
    "then generate a full incident report."
)