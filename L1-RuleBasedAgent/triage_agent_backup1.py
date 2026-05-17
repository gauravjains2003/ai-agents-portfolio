# ============================================================
# IT Triage Agent - L1 Rule Based
# Concept: Perception -> Decision -> Action
# ============================================================

# ---- PERCEPTION LAYER ----
# This is what the agent "knows about the world"
# In L2/L3 this will be replaced by LLM understanding
# For now - we define rules manually

RULES = {
    "access": {
        "keywords": ["login", "password", "access", "locked", "sso", "authentication", "unauthorized"],
        "team": "IAM Team",
        "priority": "P2",
        "action": "Check AD sync, SSO config, and user account status"
    },
    "performance": {
        "keywords": ["slow", "latency", "timeout", "hanging", "unresponsive", "lag"],
        "team": "Performance & Infra Team",
        "priority": "P2",
        "action": "Check CPU, memory, DB query times and network latency"
    },
    "outage": {
        "keywords": ["down", "outage", "unavailable", "not working", "crash", "failed"],
        "team": "L2 Production Support",
        "priority": "P1",
        "action": "Trigger incident bridge, notify stakeholders immediately"
    },
    "data": {
        "keywords": ["data", "missing", "wrong", "incorrect", "mismatch", "feed", "sync"],
        "team": "Data & Integration Team",
        "priority": "P3",
        "action": "Check feed logs, reconciliation reports and source system"
    },
    "batch": {
        "keywords": ["batch", "job", "scheduled", "cron", "stuck", "not run"],
        "team": "Batch Operations Team",
        "priority": "P2",
        "action": "Check job scheduler, logs and dependencies"
    }
}

# ---- DECISION LAYER ----
# Agent reads input, matches against rules, calculates confidence
def classify_incident(description):
    description_lower = description.lower()
    
    scores = {}

    for category, rule in RULES.items():
        matched_keywords = [kw for kw in rule["keywords"] if kw in description_lower]
        score = len(matched_keywords)
        if score > 0:
            scores[category] = {
                "score": score,
                "matched": matched_keywords
            }

    return scores

# ---- ACTION LAYER ----
# Agent decides what to do and produces structured output
def triage(description):
    print("\n" + "="*55)
    print("IT TRIAGE AGENT - INCIDENT ANALYSIS")
    print("="*55)
    print(f"Incident: {description}")
    print("-"*55)

    scores = classify_incident(description)

    if not scores:
        print("Category  : UNKNOWN")
        print("Priority  : P3")
        print("Route to  : L1 Helpdesk")
        print("Action    : Manual review needed - no rules matched")
        print("Confidence: LOW")
        return

    # Pick the highest scoring category
    best_match = max(scores, key=lambda x: scores[x]["score"])
    result = RULES[best_match]
    confidence = "HIGH" if scores[best_match]["score"] >= 2 else "MEDIUM"

    print(f"Category  : {best_match.upper()}")
    print(f"Priority  : {result['priority']}")
    print(f"Route to  : {result['team']}")
    print(f"Action    : {result['action']}")
    print(f"Matched   : {scores[best_match]['matched']}")
    print(f"Confidence: {confidence}")
    print("="*55)

# ---- ENTRY POINT ----
if __name__ == "__main__":
    print("\n\nIT Triage Agent Ready. Type 'exit' to quit.\n")

    while True:
        user_input = input("\n\nDescribe the incident: ")
        if user_input.lower() == "exit":
            print("Agent shutting down.")
            break
        triage(user_input)