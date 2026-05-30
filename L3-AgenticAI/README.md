# 🤖 Log Analyser — Agentic AI (L3)

> Part of my AI Agents Portfolio | Level 3: Agentic AI

## What This Does
An autonomous IT log analysis agent that investigates incidents 
independently — reading log files, finding errors, building timelines, 
checking a knowledge base, and generating incident reports without 
human guidance at each step.

## What Makes This "Agentic"
| Capability | Implementation |
|---|---|
| Planning | Agent decides its own investigation steps |
| Tool Use | 5 tools: read, search, timeline, KB lookup, report |
| Memory | Full conversation history passed between steps |
| Reflection | Agent checks results and decides next action |
| Autonomy | Identified OutOfMemory error without being told to |

## Agent Architecture — Custom ReAct Loop
GOAL given by user
↓
THOUGHT  → Agent reasons about next step
ACTION   → Agent picks and calls a tool
OBSERVATION → Tool result returned
↓
Loop repeats until agent decides DONE
↓
REPORT generated and saved

## Available Tools
| Tool | Purpose |
|---|---|
| read_log_file | Reads any log file from disk |
| search_errors | Finds error patterns in log content |
| get_error_timeline | Builds chronological error timeline |
| check_knowledge_base | Looks up known fixes for error codes |
| generate_report | Produces formatted incident report |

## How to Run

### Prerequisites
- Python 3.9+
- Ollama installed and running
- llama3.1 model pulled

```bash
ollama serve
python log_analyser.py
```

## Sample Agent Run
Step 1 → read_log_file        (agent's own decision)
Step 2 → search_errors        (found 8 errors)
Step 3 → get_error_timeline   (8 timestamped events)
Step 4 → check_knowledge_base (ORA-12541)
Step 5 → check_knowledge_base (OutOfMemory — noticed autonomously)
Step 6 → generate_report      (full incident report)
Step 7 → DONE

## Key Concepts Demonstrated
| Concept | What it means |
|---|---|
| ReAct Pattern | Reasoning + Acting loop |
| Tool Registry | Agent selects from available tools |
| Conversation Memory | Full history passed to LLM each step |
| Autonomous Planning | Agent sets its own agenda |
| Custom Agent Loop | Built without heavy frameworks |

## Why Custom Loop Over LangChain
LangChain's ReAct executor sends prompts too large for llama3.1:8b,
causing the model to freeze. A custom loop sends small focused JSON
requests — more reliable and educational.

## Tech Stack
- Python 3.13
- Ollama (llama3.1:8b) — local LLM
- No heavy frameworks — custom ReAct implementation

## Portfolio
- **L1** → Rule-Based Agent ✅
- **L2** → GenAI Agent ✅
- **L3** → Agentic AI ✅ (this project)