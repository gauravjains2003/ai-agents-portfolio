# ============================================================
# L3 Agentic AI — Intelligent Log Analyser
# Concept: ReAct Agent with Tools + Memory + Planning
# ============================================================

import json
import re
import os
import datetime
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain.prompts import PromptTemplate

# ============================================================
# TOOLS — What the agent can do
# Each @tool is a capability the agent can choose to use
# ============================================================

@tool
def read_log_file(filepath: str) -> str:
    """Read a log file and return its contents. 
    Use this to load log data before analysing it."""
    try:
        if not os.path.exists(filepath):
            return f"ERROR: File not found at {filepath}"
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.split("\n")
        return f"Log file loaded. Total lines: {len(lines)}\n\n{content}"
    except Exception as e:
        return f"ERROR reading file: {str(e)}"

@tool
def search_errors(log_content: str) -> str:
    """Search through log content and extract all error lines with timestamps.
    Use this after reading a log file to find problems."""
    error_patterns = [
        r"ERROR", r"FATAL", r"CRITICAL", r"Exception",
        r"ORA-\d+", r"SQLSTATE", r"Connection refused",
        r"Timeout", r"OutOfMemory", r"NullPointer"
    ]
    
    lines = log_content.split("\n")
    errors_found = []
    
    for i, line in enumerate(lines):
        for pattern in error_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                errors_found.append({
                    "line_number": i + 1,
                    "content": line.strip()
                })
                break
    
    if not errors_found:
        return "No errors found in log content."
    
    result = f"Found {len(errors_found)} error(s):\n\n"
    for err in errors_found:
        result += f"Line {err['line_number']}: {err['content']}\n"
    
    return result

@tool
def get_error_timeline(log_content: str) -> str:
    """Extract timestamps from error lines to build an error timeline.
    Use this to understand when errors started and their frequency."""
    timestamp_patterns = [
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
        r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}",
        r"\d{2}-\w{3}-\d{4} \d{2}:\d{2}:\d{2}"
    ]
    
    lines = log_content.split("\n")
    timeline = []
    
    for line in lines:
        is_error = any(p in line.upper() for p in 
                      ["ERROR", "FATAL", "CRITICAL", "EXCEPTION", "ORA-"])
        if is_error:
            for pattern in timestamp_patterns:
                match = re.search(pattern, line)
                if match:
                    timeline.append({
                        "timestamp": match.group(),
                        "event": line.strip()[:100]
                    })
                    break
    
    if not timeline:
        return "No timestamped errors found."
    
    result = f"Error Timeline ({len(timeline)} events):\n\n"
    for event in timeline:
        result += f"[{event['timestamp']}] {event['event']}\n"
    
    return result

@tool
def check_knowledge_base(error_code: str) -> str:
    """Look up known errors and their fixes in the knowledge base.
    Use this to find recommended solutions for specific error codes."""
    knowledge_base = {
        "ORA-12541": {
            "description": "TNS: no listener",
            "cause": "Oracle listener service is not running or misconfigured",
            "fix": "Start Oracle listener: lsnrctl start. Check tnsnames.ora configuration.",
            "team": "DBA Team"
        },
        "ORA-00942": {
            "description": "Table or view does not exist",
            "cause": "Missing table, wrong schema, or insufficient privileges",
            "fix": "Verify table exists, check schema name, grant SELECT privileges",
            "team": "DBA Team"
        },
        "ORA-01017": {
            "description": "Invalid username/password",
            "cause": "Wrong credentials or account locked",
            "fix": "Reset password, unlock account: ALTER USER username ACCOUNT UNLOCK",
            "team": "DBA Team"
        },
        "CONNECTION REFUSED": {
            "description": "Service not accepting connections",
            "cause": "Service down, wrong port, or firewall blocking",
            "fix": "Check service status, verify port, review firewall rules",
            "team": "Infrastructure Team"
        },
        "OUTOFMEMORY": {
            "description": "Java heap space exhausted",
            "cause": "Memory leak or insufficient heap allocation",
            "fix": "Increase JVM heap: -Xmx4g. Review for memory leaks.",
            "team": "Application Team"
        },
        "TIMEOUT": {
            "description": "Operation exceeded time limit",
            "cause": "Slow query, network latency, or resource contention",
            "fix": "Check DB query performance, network latency, increase timeout threshold",
            "team": "Performance Team"
        }
    }
    
    error_upper = error_code.upper().strip()
    
    # Direct match
    if error_upper in knowledge_base:
        kb = knowledge_base[error_upper]
        return (f"Knowledge Base Match: {error_upper}\n"
                f"Description : {kb['description']}\n"
                f"Cause       : {kb['cause']}\n"
                f"Fix         : {kb['fix']}\n"
                f"Escalate to : {kb['team']}")
    
    # Partial match
    for key in knowledge_base:
        if key in error_upper or error_upper in key:
            kb = knowledge_base[key]
            return (f"Knowledge Base Match: {key}\n"
                    f"Description : {kb['description']}\n"
                    f"Cause       : {kb['cause']}\n"
                    f"Fix         : {kb['fix']}\n"
                    f"Escalate to : {kb['team']}")
    
    return f"No knowledge base entry found for: {error_code}. Escalate to L2 Support."

@tool
def generate_report(analysis_summary: str) -> str:
    """Generate a formatted incident report from the analysis summary.
    Use this as the FINAL step after completing all investigation."""
    ticket_id = f"AGT{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
╔══════════════════════════════════════════════════════╗
║      L3 AGENTIC AI — INCIDENT REPORT                 ║
╚══════════════════════════════════════════════════════╝
  Ticket ID   : {ticket_id}
  Generated   : {timestamp}
  Agent       : Log Analyser (ReAct)
──────────────────────────────────────────────────────
{analysis_summary}
══════════════════════════════════════════════════════
"""
    
    # Save report
    os.makedirs("reports", exist_ok=True)
    filepath = f"reports/{ticket_id}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
    
    return f"Report generated and saved to {filepath}\n{report}"

# ============================================================
# SAMPLE LOG FILE GENERATOR
# Creates a realistic log file for testing
# ============================================================

def create_sample_log():
    log_content = """2026-05-28 01:45:00 INFO  Application started successfully
2026-05-28 01:45:01 INFO  Database connection pool initialized (size=10)
2026-05-28 01:45:02 INFO  Batch job scheduler started
2026-05-28 02:00:00 INFO  Batch job DAILY_RECONCILIATION started
2026-05-28 02:01:15 INFO  Processing 15420 records
2026-05-28 02:03:22 ERROR Database connection lost: ORA-12541 TNS no listener
2026-05-28 02:03:23 ERROR Batch job DAILY_RECONCILIATION failed after 3 retries
2026-05-28 02:03:24 FATAL Connection refused on port 1521 - database unreachable
2026-05-28 02:05:00 ERROR User login attempt failed - Connection refused to auth service
2026-05-28 02:05:01 ERROR User login attempt failed - Connection refused to auth service
2026-05-28 02:05:45 ERROR OutOfMemory: Java heap space in SessionManager
2026-05-28 02:06:00 ERROR 142 concurrent users affected by auth service failure
2026-05-28 02:10:00 INFO  Attempting database reconnection...
2026-05-28 02:10:05 ERROR Reconnection timeout after 5000ms
2026-05-28 02:15:00 ERROR ORA-12541 persists - escalation required
2026-05-28 02:20:00 INFO  DBA team notified
2026-05-28 02:45:00 INFO  Database listener restarted by DBA team
2026-05-28 02:45:30 INFO  Connection pool re-established
2026-05-28 02:46:00 INFO  Services recovering
2026-05-28 03:00:00 INFO  All systems operational"""
    
    with open("sample_app.log", "w") as f:
        f.write(log_content)
    
    print("✓ Sample log file created: sample_app.log")

# ============================================================
# AGENT SETUP — ReAct Pattern
# ============================================================

def create_agent():
    llm = ChatOllama(model="llama3.1", temperature=0)
    
    tools = [
        read_log_file,
        search_errors,
        get_error_timeline,
        check_knowledge_base,
        generate_report
    ]
    
    # ReAct prompt template
    react_prompt = PromptTemplate.from_template("""You are an expert IT incident analyst agent.
You have access to tools to investigate incidents thoroughly.

Always follow this approach:
1. Read the log file first
2. Search for errors
3. Build the error timeline  
4. Check knowledge base for each error found
5. Generate a final report

Available tools:
{tools}

Tool names: {tool_names}

Use this exact format:
Thought: [your reasoning about what to do next]
Action: [tool name]
Action Input: [input to the tool]
Observation: [tool result - filled automatically]
... (repeat Thought/Action/Observation as needed)
Thought: I now have enough information to generate the final report
Action: generate_report
Action Input: [complete summary of findings]
Final Answer: [confirmation that report has been generated]

Begin!

Task: {input}
{agent_scratchpad}""")

    agent = create_react_agent(llm, tools, react_prompt)
    
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True
    )
    
    return executor

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("L3 Agentic AI — Log Analyser Agent")
    print("Powered by llama3.1 + LangChain ReAct\n")
    
    # Create sample log for testing
    create_sample_log()
    
    # Create and run agent
    print("\n🤖 Agent starting analysis...\n")
    print("="*55)
    
    agent = create_agent()
    
    result = agent.invoke({
        "input": "Analyse the log file at sample_app.log. "
                 "Find all errors, build a timeline, check the knowledge base "
                 "for known fixes, and generate a full incident report."
    })
    
    print("\n" + "="*55)
    print("AGENT COMPLETED")
    print("="*55)
    print(result["output"])