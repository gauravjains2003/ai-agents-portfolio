# ============================================================
# IT Triage Agent - L1 Rule Based - Step 2
# New: Multi-category, Severity Escalation, Ticket Summary
# ============================================================

import datetime

# ---- PERCEPTION LAYER ----
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

# ---- ESCALATION RULES ----
# These override priority regardless of category
ESCALATION_TRIGGERS = {
    "user_count": {
        "keywords": ["all users", "everyone", "entire team", "whole floor", "500", "1000", "multiple users"],
        "bump_to": "P1",
        "reason": "Mass user impact detected"
    },
    "environment": {
        "keywords": ["production", "prod", "live", "client facing"],
        "bump_to": "P1",
        "reason": "Production environment affected"
    },
    "vip": {
        "keywords": ["ceo", "cfo", "cto", "director", "vip", "executive", "head of"],
        "bump_to": "P1",
        "reason": "VIP user impacted"
    },
    "compliance": {
        "keywords": ["audit", "compliance", "regulatory", "sox", "gdpr", "breach"],
        "bump_to": "P1",
        "reason": "Compliance risk identified"
    }
}

# ---- DECISION LAYER ----
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

def check_escalation(description):
    description_lower = description.lower()
    triggered = []

    for trigger_name, trigger in ESCALATION_TRIGGERS.items():
        matched = [kw for kw in trigger["keywords"] if kw in description_lower]
        if matched:
            triggered.append({
                "trigger": trigger_name,
                "bump_to": trigger["bump_to"],
                "reason": trigger["reason"],
                "matched": matched
            })

    return triggered

def determine_confidence(score):
    if score >= 3:
        return "HIGH"
    elif score >= 2:
        return "MEDIUM"
    else:
        return "LOW"

# ---- TICKET GENERATOR ----
def generate_ticket(description, categories, escalations):
    ticket_id = f"INC{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Primary category = highest score
    primary = max(categories, key=lambda x: categories[x]["score"])
    primary_rule = RULES[primary]
    priority = primary_rule["priority"]

    # Check if escalation overrides priority
    escalation_note = None
    if escalations:
        priority = "P1"  # escalations always win
        escalation_note = escalations[0]["reason"]

    ticket = f"""
╔══════════════════════════════════════════════════════╗
║           IT TRIAGE AGENT — AUTO TICKET              ║
╚══════════════════════════════════════════════════════╝
  Ticket ID   : {ticket_id}
  Timestamp   : {timestamp}
  Priority    : {priority}
──────────────────────────────────────────────────────
  INCIDENT DESCRIPTION
  {description}
──────────────────────────────────────────────────────
  CLASSIFICATION"""

    # Show all matched categories
    for cat, data in sorted(categories.items(), key=lambda x: -x[1]["score"]):
        confidence = determine_confidence(data["score"])
        ticket += f"""
  ▸ {cat.upper()} [{confidence}]
    Keywords  : {', '.join(data['matched'])}
    Route to  : {RULES[cat]['team']}
    Action    : {RULES[cat]['action']}"""

    # Show escalation if triggered
    if escalations:
        ticket += f"""
──────────────────────────────────────────────────────
  ⚠ ESCALATION TRIGGERED
  Reason      : {escalation_note}
  Matched on  : {', '.join(escalations[0]['matched'])}
  Priority bumped to P1"""

    ticket += """
══════════════════════════════════════════════════════"""
    return ticket

# ---- ACTION LAYER ----
def triage(description):
    categories = classify_incident(description)
    escalations = check_escalation(description)

    if not categories:
        print("""
══════════════════════════════════════════════════════
  RESULT    : UNCLASSIFIED
  Priority  : P3
  Route to  : L1 Helpdesk
  Action    : Manual review needed
══════════════════════════════════════════════════════""")
        return

    ticket = generate_ticket(description, categories, escalations)
    print(ticket)

# ---- ENTRY POINT ----
if __name__ == "__main__":
    print("IT Triage Agent v2 Ready. Type 'exit' to quit.\n")

    while True:
        user_input = input("Describe the incident: ")
        if user_input.lower() == "exit":
            print("Agent shutting down.")
            break
        triage(user_input)