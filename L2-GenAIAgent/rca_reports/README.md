# 🤖 RCA Generator — GenAI Agent (L2)

> Part of my AI Agents Portfolio | Level 2: GenAI Agent

## What This Does
An AI-powered Root Cause Analysis agent that takes an IT incident 
description and returns a fully structured RCA — powered by llama3.1 
running locally via Ollama. No internet. No API costs.

## Features
- ✅ LLM-powered semantic understanding (no keyword rules)
- ✅ Structured JSON output via prompt engineering
- ✅ Auto-generated RCA reports saved as JSON files
- ✅ Running incident log in CSV format
- ✅ Live statistics dashboard
- ✅ Fully offline — runs on local hardware

## Agent Architecture
User Input
↓
System Prompt (Prompt Engineering)
↓
llama3.1 via Ollama (Local LLM)
↓
JSON Response Parser
↓
Structured Display + File Save + CSV Log

## How to Run

### Prerequisites
- Python 3.9+
- Ollama installed → https://ollama.com
- llama3.1 model pulled

```bash
ollama pull llama3.1
ollama serve
```

### Run the Agent
```bash
python rca_agent.py
```

### Commands
| Command | Action |
|---|---|
| Type incident | Generates structured RCA |
| `stats` | Shows analysis statistics |
| `exit` | Shuts down agent |

## Sample Output
Ticket ID       : RCA20260528161448
Priority        : P1
Confidence      : HIGH
Root Cause      : Database connection issue due to network failure
Affected Area   : Login Module
Immediate Action: Restart Database Connection Pool
Escalate To     : DBA Team and Network Team

## Key Concepts Demonstrated
| Concept | Implementation |
|---|---|
| Prompt Engineering | Structured system prompt with exact JSON schema |
| Structured Output | LLM constrained to return valid JSON |
| Local Inference | Ollama + llama3.1, fully offline |
| Zero-shot Reasoning | No examples needed, LLM uses domain knowledge |
| Safe Parsing | JSON parser with markdown fence cleanup |

## L1 vs L2 Comparison
| Scenario | L1 Rule Agent | L2 RCA Agent |
|---|---|---|
| "ORA-12541 error" | UNCLASSIFIED ❌ | Root cause identified ✅ |
| "Deployment degraded perf" | PERFORMANCE only ❌ | Rollback recommended ✅ |
| Prevention advice | Never ❌ | Always ✅ |

## Tech Stack
- Python 3.13
- Ollama (llama3.1:8b) — local LLM
- No external Python libraries beyond ollama

## Portfolio
- **L1** → Rule-Based Agent ✅
- **L2** → GenAI Agent ✅ (this project)
- **L3** → Agentic AI 🔄