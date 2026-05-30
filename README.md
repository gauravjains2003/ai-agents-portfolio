# 🤖 AI Agents Portfolio

> Building AI agents from scratch — Rule-Based → GenAI → Agentic AI

## About
This portfolio documents my journey building production-grade AI agents,
progressing from rule-based logic to LLM-powered reasoning to full
agentic workflows with memory, tools, and planning.

Built entirely locally — no cloud APIs, no cost, runs on a personal
laptop using Ollama + llama3.1:8b.

## Projects

### ✅ L1 — Rule-Based Agents
| Project | Description | Status |
|---|---|---|
| [IT Triage Agent](./L1-RuleBasedAgent) | Classifies incidents, assigns priority, routes to teams | ✅ Complete |

### ✅ L2 — GenAI Agents
| Project | Description | Status |
|---|---|---|
| [RCA Generator](./L2-GenAIAgent) | Paste incident → LLM generates structured root cause analysis | ✅ Complete |

### ✅ L3 — Agentic AI
| Project | Description | Status |
|---|---|---|
| [Log Analyser](./L3-AgenticAI) | Autonomous agent reads logs, finds errors, checks KB, generates report | ✅ Complete |

## Architecture Progression
L1 — Rule Engine
if keyword → action (deterministic)
L2 — LLM Reasoning
incident → llama3.1 → structured JSON output
L3 — Autonomous Agent
goal → ReAct loop → tools → memory → report

## Key Concepts Covered

| Concept | L1 | L2 | L3 |
|---|---|---|---|
| Intent Classification | ✅ | ✅ | ✅ |
| Prompt Engineering | ❌ | ✅ | ✅ |
| Structured Output | ❌ | ✅ | ✅ |
| Tool Use | ❌ | ❌ | ✅ |
| Memory | ❌ | ❌ | ✅ |
| Autonomous Planning | ❌ | ❌ | ✅ |
| ReAct Pattern | ❌ | ❌ | ✅ |

## Tech Stack
- Python 3.13
- Ollama (llama3.1:8b) — fully local LLM
- Custom ReAct agent loop
- No cloud dependencies

## What I Learned
- Rule-based agents teach agent structure fundamentals
- Prompt engineering is the core skill for GenAI agents
- Structured JSON output makes LLM responses reliable
- Small local models need lightweight orchestration
- Agentic AI = Planning + Tools + Memory + Reflection

## Author
Gaurav Jain — IT Production Support → AI Engineering
[GitHub](https://github.com/gauravjains2003)