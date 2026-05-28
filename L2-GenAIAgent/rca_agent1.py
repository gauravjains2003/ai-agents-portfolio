# ============================================================
# L2 GenAI Agent — First LLM Call
# Concept: Talking to a local LLM via Ollama
# ============================================================

import ollama

# This is the entire "brain" replacement for L1's RULES dictionary
response = ollama.chat(
    model="llama3.1",
    messages=[
        {
            "role": "system",
            "content": "You are an expert IT support engineer. Analyse incidents and provide clear root cause analysis."
        },
        {
            "role": "user",
            "content": "Users cannot login to the application since 9am this morning."
        }
    ]
)

# The LLM response is here
print(response["message"]["content"])