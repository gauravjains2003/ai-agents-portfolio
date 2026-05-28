# ============================================================
# L2 GenAI Agent — RCA Generator Step 2
# Concept: Prompt Engineering for Structured Output
# ============================================================

import ollama
import datetime

def generate_rca(incident_description):
    
    # ---- THIS IS THE PROMPT ENGINEERING ----
    # Notice how precisely we instruct the LLM
    system_prompt = """You are a senior IT production support engineer with 10 years experience.
Your job is to analyse IT incidents and produce a structured Root Cause Analysis.

You MUST respond in EXACTLY this format and nothing else:

SUMMARY: [one line summary of the incident]
ROOT_CAUSE: [most likely root cause in one line]
CONFIDENCE: [HIGH / MEDIUM / LOW]
PRIORITY: [P1 / P2 / P3]
AFFECTED_AREA: [which system/component is affected]
IMMEDIATE_ACTION: [single most important action to take right now]
ESCALATE_TO: [which team should own this]
ADDITIONAL_STEPS:
- [step 1]
- [step 2]
- [step 3]

Do not add any explanation, preamble, or markdown outside this format."""

    user_prompt = f"""Analyse this IT incident and provide root cause analysis:

INCIDENT: {incident_description}"""

    print("\n⏳ Analysing incident with llama3.1...\n")
    
    response = ollama.chat(
        model="llama3.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response["message"]["content"]

def parse_and_display(raw_response, incident):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ticket_id = f"RCA{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    print("╔══════════════════════════════════════════════════════╗")
    print("║         RCA AGENT — ROOT CAUSE ANALYSIS              ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  Ticket ID  : {ticket_id}")
    print(f"  Timestamp  : {timestamp}")
    print("──────────────────────────────────────────────────────")
    print(f"  INCIDENT   : {incident}")
    print("──────────────────────────────────────────────────────")
    print("  ANALYSIS")
    print()
    
    # Parse each line from LLM response
    lines = raw_response.strip().split("\n")
    in_steps = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("SUMMARY:"):
            print(f"  Summary         : {line.replace('SUMMARY:', '').strip()}")
        elif line.startswith("ROOT_CAUSE:"):
            print(f"  Root Cause      : {line.replace('ROOT_CAUSE:', '').strip()}")
        elif line.startswith("CONFIDENCE:"):
            val = line.replace("CONFIDENCE:", "").strip()
            print(f"  Confidence      : {val}")
        elif line.startswith("PRIORITY:"):
            val = line.replace("PRIORITY:", "").strip()
            print(f"  Priority        : {val}")
        elif line.startswith("AFFECTED_AREA:"):
            print(f"  Affected Area   : {line.replace('AFFECTED_AREA:', '').strip()}")
        elif line.startswith("IMMEDIATE_ACTION:"):
            print(f"  Immediate Action: {line.replace('IMMEDIATE_ACTION:', '').strip()}")
        elif line.startswith("ESCALATE_TO:"):
            print(f"  Escalate To     : {line.replace('ESCALATE_TO:', '').strip()}")
        elif line.startswith("ADDITIONAL_STEPS:"):
            print(f"  Additional Steps:")
            in_steps = True
        elif in_steps and line.startswith("-"):
            print(f"    {line}")

    print()
    print("══════════════════════════════════════════════════════")
    
    return ticket_id

# ---- ENTRY POINT ----
if __name__ == "__main__":
    print("RCA Agent Ready. Powered by llama3.1 (local)")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("Describe the incident: ").strip()
        if user_input.lower() == "exit":
            print("Agent shutting down.")
            break
        elif user_input == "":
            continue
        
        raw = generate_rca(user_input)
        parse_and_display(raw, user_input)