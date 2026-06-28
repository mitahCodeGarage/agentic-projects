"""
Gold Rate Agent — Mumbai (CrewAI setup)

Defines the CrewAI agent, task, and crew. The scraping tools they use live in
tools.py; the runnable entry point lives in main.py.

Run locally — sandbox blocks most financial data endpoints.

Exposes: crew, MODEL, console, OPENROUTER_API_KEY
"""

import os
from dotenv import load_dotenv

# Load variables from a local .env file (if present) into the environment
load_dotenv()

from crewai import Agent, Task, Crew, Process
from rich.console import Console

from tools import get_gold_rate_history

# ─────────────────────────────────────────────────────────────
# CONFIG  — set your key via env var or paste directly below
# ─────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY_HERE")

# Pick any model available on OpenRouter
MODEL = "openrouter/openai/gpt-4o-mini"
# Alternatives:
#   "openrouter/anthropic/claude-3-haiku"
#   "openrouter/openai/gpt-4o-mini"
#   "openrouter/mistralai/mistral-7b-instruct"
#   "openrouter/google/gemini-2.0-flash-001"

os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

console = Console()


# ─────────────────────────────────────────────────────────────
# AGENT + TASK + CREW
# ─────────────────────────────────────────────────────────────

gold_analyst = Agent(
    role="Gold Market Analyst",
    goal=(
        "Provide accurate, well-formatted gold rate reports for Mumbai. "
        "The 10-day history already includes today's rate, so call only the "
        "history tool and read today's rate from its first (most recent) row."
    ),
    backstory=(
        "You are a seasoned commodities analyst covering the Indian gold market. "
        "You specialise in presenting gold prices clearly for retail buyers, jewellers, "
        "and investors, with an eye for trends and practical implications."
    ),
    tools=[get_gold_rate_history],
    llm=MODEL,
    verbose=True,
    max_iter=6,
)

gold_task = Task(
    description=(
        "Step 1: Call the tool 'Get Last 10 Days Gold Rate History Mumbai' to get the table. "
        "Its first (most recent) row IS today's rate — do NOT call any separate current-rate tool.\n"
        "Step 2: Write a structured report containing:\n"
        "  A) A clear section for today's 22K and 24K rates, taken from the first row of the table.\n"
        "  B) The full 10-day historical table exactly as returned by the tool.\n"
        "  C) A 2–3 sentence market trend analysis based on the data.\n"
        "Do NOT fabricate rates."
    ),
    expected_output=(
        "A gold rate report with: current rates section, 10-day historical table, "
        "and brief trend commentary."
    ),
    agent=gold_analyst,
)

crew = Crew(
    agents=[gold_analyst],
    tasks=[gold_task],
    process=Process.sequential,
    verbose=True,
)
