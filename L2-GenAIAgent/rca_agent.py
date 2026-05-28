# ============================================================
# L2 GenAI Agent — RCA Generator Step 3
# Concept: JSON Structured Output + File Saving + Incident Log
# ============================================================

import ollama
import datetime
import json
import os
import csv

# ---- FOLDER SETUP ----
RCA_DIR = "rca_reports"
LOG_FILE = "rca_log.csv"

def setup():
    if not os.path.exists(RCA_DIR):
        os.makedirs(RCA_DIR)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "TicketID", "Timestamp", "Priority", 
                "Confidence", "AffectedArea", 
                "EscalateTo", "Incident"
            ])

# ---- PROMPT ENGINEERING — JSON MODE ----
def build_prompt(incident):
    system_prompt = """You are a senior IT production support engineer with 10 years experience.
Analyse IT incidents and return a Root Cause Analysis.

You MUST respond with ONLY valid JSON. No explanation. No markdown. No code blocks.
Exactly this structure:

{
  "summary": "one line summary",
  "root_cause": "most likely root cause",
  "confidence": "HIGH or MEDIUM or LOW",
  "priority": "P1 or P2 or P3",
  "affected_area": "which system or component",
  "immediate_action": "single most important action right now",
  "escalate_to": "which team",
  "additional_steps": [
    "step 1",
    "step 2",
    "step 3"
  ],
  "prevention": "how to prevent this in future"
}"""

    user_prompt = f"Analyse this incident: {incident}"
    
    return system_prompt, user_prompt

# ---- LLM CALL ----
def call_llm(incident):
    system_prompt, user_prompt = build_prompt(incident)
    
    print("\n⏳ Analysing with llama3.1...\n")
    
    response = ollama.chat(
        model="llama3.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response["message"]["content"]

# ---- JSON PARSER — SAFE ----
def parse_response(raw_response):
    try:
        # Clean response — remove markdown code blocks if LLM added them
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()
        
        data = json.loads(cleaned)
        return data, None
        
    except json.JSONDecodeError as e:
        return None, f"JSON parse failed: {str(e)}"

# ---- DISPLAY ----
def display_rca(ticket_id, timestamp, incident, data):
    priority = data.get("priority", "UNKNOWN")
    confidence = data.get("confidence", "UNKNOWN")
    
    print("╔══════════════════════════════════════════════════════╗")
    print("║         RCA AGENT — ROOT CAUSE ANALYSIS              ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  Ticket ID       : {ticket_id}")
    print(f"  Timestamp       : {timestamp}")
    print(f"  Priority        : {priority}")
    print(f"  Confidence      : {confidence}")
    print("──────────────────────────────────────────────────────")
    print(f"  INCIDENT        : {incident}")
    print("──────────────────────────────────────────────────────")
    print(f"  Summary         : {data.get('summary', 'N/A')}")
    print(f"  Root Cause      : {data.get('root_cause', 'N/A')}")
    print(f"  Affected Area   : {data.get('affected_area', 'N/A')}")
    print(f"  Immediate Action: {data.get('immediate_action', 'N/A')}")
    print(f"  Escalate To     : {data.get('escalate_to', 'N/A')}")
    print("──────────────────────────────────────────────────────")
    print("  Additional Steps:")
    for i, step in enumerate(data.get("additional_steps", []), 1):
        print(f"    {i}. {step}")
    print("──────────────────────────────────────────────────────")
    print(f"  Prevention      : {data.get('prevention', 'N/A')}")
    print("══════════════════════════════════════════════════════")

# ---- FILE OPERATIONS ----
def save_report(ticket_id, incident, data):
    filepath = os.path.join(RCA_DIR, f"{ticket_id}.json")
    report = {
        "ticket_id": ticket_id,
        "incident": incident,
        "analysis": data
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return filepath

def log_rca(ticket_id, timestamp, priority, confidence, data, incident):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            ticket_id,
            timestamp,
            priority,
            confidence,
            data.get("affected_area", "N/A"),
            data.get("escalate_to", "N/A"),
            incident
        ])

# ---- STATISTICS ----
def show_statistics():
    if not os.path.exists(LOG_FILE):
        print("No incidents logged yet.")
        return

    priorities = {"P1": 0, "P2": 0, "P3": 0}
    confidence_count = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    total = 0

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            p = row["Priority"]
            c = row["Confidence"]
            if p in priorities:
                priorities[p] += 1
            if c in confidence_count:
                confidence_count[c] += 1

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║              RCA AGENT STATISTICS                    ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  Total Analysed  : {total}")
    print(f"  P1 Critical     : {priorities['P1']}")
    print(f"  P2 High         : {priorities['P2']}")
    print(f"  P3 Medium       : {priorities['P3']}")
    print("──────────────────────────────────────────────────────")
    print(f"  HIGH Confidence : {confidence_count['HIGH']}")
    print(f"  MED  Confidence : {confidence_count['MEDIUM']}")
    print(f"  LOW  Confidence : {confidence_count['LOW']}")
    print("══════════════════════════════════════════════════════\n")

# ---- MAIN AGENT LOOP ----
def run_agent(incident):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ticket_id = f"RCA{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    raw = call_llm(incident)
    data, error = parse_response(raw)

    if error:
        print(f"\n⚠ Could not parse LLM response: {error}")
        print("Raw response:")
        print(raw)
        return

    display_rca(ticket_id, timestamp, incident, data)

    filepath = save_report(ticket_id, incident, data)
    log_rca(ticket_id, timestamp, 
            data.get("priority", "P3"),
            data.get("confidence", "LOW"),
            data, incident)

    print(f"\n  ✓ Report saved to : {filepath}")
    print(f"  ✓ Logged to       : {LOG_FILE}\n")

# ---- ENTRY POINT ----
if __name__ == "__main__":
    setup()
    print("RCA Agent v3 — Powered by llama3.1 (local)")
    print("Commands: 'stats' for statistics, 'exit' to quit\n")

    while True:
        user_input = input("Describe the incident: ").strip()
        if user_input.lower() == "exit":
            print("Agent shutting down.")
            break
        elif user_input.lower() == "stats":
            show_statistics()
        elif user_input == "":
            continue
        else:
            run_agent(user_input)