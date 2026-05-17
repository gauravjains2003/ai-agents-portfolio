# 🤖 IT Triage Agent — Rule-Based AI Agent (L1)

> Part of my AI Agents Portfolio | Level 1: Rule-Based Agent

## What This Does
An intelligent IT incident triage agent that automatically classifies 
incidents, assigns priority, routes to the correct team, and generates 
structured tickets — all using rule-based decision logic.

## Features
- ✅ Multi-category incident classification
- ✅ Confidence scoring (HIGH / MEDIUM / LOW)
- ✅ Escalation detection (VIP, Production, Mass Impact, Compliance)
- ✅ Auto ticket generation with unique IDs
- ✅ Incident log in CSV format
- ✅ Live statistics dashboard

## Agent Architecture

Perception Layer  →  reads and tokenizes incident description
Decision Layer    →  scores against rule categories, checks escalations
Action Layer      →  generates ticket, saves file, updates log

## How to Run
```bash
python triage_agent.py
```

### Commands
| Command | Action |
|---|---|
| Type incident | Generates and saves ticket |
| `stats` | Shows incident statistics |
| `exit` | Shuts down agent |

## Sample Output

Ticket ID   : INC20260517144232
Priority    : P1
Category    : ACCESS, PERFORMANCE
Escalation  : VIP user impacted (CEO)
Route to    : IAM Team + Performance & Infra Team

## Limitations & Why L2 Exists
| Limitation | Example |
|---|---|
| Exact keyword match only | "cant get in" misses ACCESS category |
| No context understanding | "system on fire" misses OUTAGE |
| No learning capability | Same mistakes forever |

These limitations are solved in **L2** using a local LLM (Ollama + llama3.1).

## Tech Stack
- Python 3.13
- No external libraries required
- Runs fully offline

## Portfolio
This is Project 1 of my AI Agents Portfolio:
- **L1** → Rule-Based Agent ✅ (this project)
- **L2** → GenAI Agent (Ollama + llama3.1) 🔄
- **L3** → Agentic AI (Tools + Memory + Planning) 🔄