# ============================================================
# IT Triage Agent - L1 Rule Based - Step 3
# New: File output, Incident Log CSV, Statistics Summary
# ============================================================

import datetime
import os
import csv

# ---- FOLDER SETUP ----
TICKETS_DIR = "tickets"
LOG_FILE = "incident_log.csv"

def setup():
    if not os.path.exists(TICKETS_DIR):
        os.makedirs(TICKETS_DIR)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["TicketID", "Timestamp", "Priority", "Categories", "Escalated", "Description"])

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
def generate_ticket(ticket_id, timestamp, description, categories, escalations):
    primary = max(categories, key=lambda x: categories[x]["score"])
    primary_rule = RULES[primary]
    priority = primary_rule["priority"]
    escalation_note = None

    if escalations:
        priority = "P1"
        escalation_note = escalations[0]["reason"]

    lines = []
    lines.append("╔══════════════════════════════════════════════════════╗")
    lines.append("║           IT TRIAGE AGENT — AUTO TICKET              ║")
    lines.append("╚══════════════════════════════════════════════════════╝")
    lines.append(f"  Ticket ID   : {ticket_id}")
    lines.append(f"  Timestamp   : {timestamp}")
    lines.append(f"  Priority    : {priority}")
    lines.append("──────────────────────────────────────────────────────")
    lines.append("  INCIDENT DESCRIPTION")
    lines.append(f"  {description}")
    lines.append("──────────────────────────────────────────────────────")
    lines.append("  CLASSIFICATION")

    for cat, data in sorted(categories.items(), key=lambda x: -x[1]["score"]):
        confidence = determine_confidence(data["score"])
        lines.append(f"  ▸ {cat.upper()} [{confidence}]")
        lines.append(f"    Keywords  : {', '.join(data['matched'])}")
        lines.append(f"    Route to  : {RULES[cat]['team']}")
        lines.append(f"    Action    : {RULES[cat]['action']}")

    if escalations:
        lines.append("──────────────────────────────────────────────────────")
        lines.append("  ⚠ ESCALATION TRIGGERED")
        lines.append(f"  Reason      : {escalation_note}")
        lines.append(f"  Matched on  : {', '.join(escalations[0]['matched'])}")
        lines.append("  Priority bumped to P1")

    lines.append("══════════════════════════════════════════════════════")
    return "\n".join(lines), priority

# ---- FILE OPERATIONS ----
def save_ticket(ticket_id, ticket_text):
    filepath = os.path.join(TICKETS_DIR, f"{ticket_id}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(ticket_text)
    return filepath

def log_incident(ticket_id, timestamp, priority, categories, escalations, description):
    escalated = "YES" if escalations else "NO"
    category_names = ", ".join(categories.keys())
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([ticket_id, timestamp, priority, category_names, escalated, description])

# ---- STATISTICS ----
def show_statistics():
    if not os.path.exists(LOG_FILE):
        print("No incidents logged yet.")
        return

    priorities = {"P1": 0, "P2": 0, "P3": 0}
    escalated_count = 0
    category_count = {}
    total = 0

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            p = row["Priority"]
            if p in priorities:
                priorities[p] += 1
            if row["Escalated"] == "YES":
                escalated_count += 1
            for cat in row["Categories"].split(", "):
                cat = cat.strip()
                category_count[cat] = category_count.get(cat, 0) + 1

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║              INCIDENT STATISTICS                     ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  Total Incidents : {total}")
    print(f"  P1 Critical     : {priorities['P1']}")
    print(f"  P2 High         : {priorities['P2']}")
    print(f"  P3 Medium       : {priorities['P3']}")
    print(f"  Escalated       : {escalated_count}")
    print("──────────────────────────────────────────────────────")
    print("  TOP CATEGORIES")
    for cat, count in sorted(category_count.items(), key=lambda x: -x[1]):
        print(f"  ▸ {cat.upper():<15} : {count} incidents")
    print("══════════════════════════════════════════════════════\n")

# ---- ACTION LAYER ----
def triage(description):
    categories = classify_incident(description)
    escalations = check_escalation(description)

    if not categories:
        ticket_id = f"INC{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("\n══════════════════════════════════════════════════════")
        print(f"  Ticket ID : {ticket_id}")
        print("  RESULT    : UNCLASSIFIED")
        print("  Priority  : P3")
        print("  Route to  : L1 Helpdesk")
        print("  Action    : Manual review needed")
        print("══════════════════════════════════════════════════════\n")
        log_incident(ticket_id, timestamp, "P3", {"unclassified": {"score": 0}}, [], description)
        return

    ticket_id = f"INC{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ticket_text, priority = generate_ticket(ticket_id, timestamp, description, categories, escalations)

    print("\n" + ticket_text)

    filepath = save_ticket(ticket_id, ticket_text)
    log_incident(ticket_id, timestamp, priority, categories, escalations, description)

    print(f"  ✓ Ticket saved to : {filepath}")
    print(f"  ✓ Logged to       : {LOG_FILE}\n")

# ---- ENTRY POINT ----
if __name__ == "__main__":
    setup()
    print("IT Triage Agent v3 Ready.")
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
            triage(user_input)