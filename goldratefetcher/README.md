# 🏅 Mumbai Gold Rate Agent

A small [CrewAI](https://docs.crewai.com/) agent that fetches the last 10 days of
gold rates (22K & 24K) for **Mumbai**, writes a short market report, prints it to
the terminal, and emails it via Gmail.

Today's rate is taken from the most recent row of the 10-day history — there is no
separate "current rate" call.

## How it works

1. **`tools.py`** scrapes [goodreturns.in](https://www.goodreturns.in/gold-rates/mumbai.html)
   for the last 10 days of Mumbai gold rates. If too few rows come back, it returns a
   static illustrative estimate so the agent still produces output.
2. **`agent.py`** defines a CrewAI "Gold Market Analyst" agent + task + crew that calls
   the history tool and composes the report (today's rates, the 10-day table, and a brief
   trend comment).
3. **`main.py`** runs the crew, prints the report, and hands it to the mailer.
4. **`mail_utility.py`** emails the report through Gmail SMTP.

## Project layout

| File | Responsibility |
|------|----------------|
| `main.py` | Entry point — runs the crew, prints and emails the report |
| `agent.py` | CrewAI agent / task / crew definition + model config |
| `tools.py` | Gold-rate scraping tool (`get_gold_rate_history`) |
| `mail_utility.py` | Sends the report via Gmail SMTP |
| `.env` | Secrets and config (not committed) |
| `requirements.txt` | Python dependencies |

## Setup

Requires **Python 3.12**.

```bash
# Create and activate a virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Copy your settings into a `.env` file in the project root:

```dotenv
# OpenRouter API key — https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-...

# Gmail SMTP — for emailing the report
# Use a Gmail App Password, NOT your normal password.
# Create one at https://myaccount.google.com/apppasswords (requires 2FA).
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Recipient (optional — defaults to mitahworkplace@gmail.com)
GMAIL_TO=recipient@example.com
```

`.env` is git-ignored — keep your keys out of version control.

### About the Gmail App Password

Gmail rejects your normal account password over SMTP. You need a 16-character
**App Password**, which only appears once **2-Step Verification** is enabled on the
account:

1. Enable 2FA: <https://myaccount.google.com/signinoptions/twosv>
2. Create an App Password: <https://myaccount.google.com/apppasswords>

If the credentials aren't set, the report still prints — only the email step is skipped.

## Usage

```bash
python main.py
```

You'll see the formatted report in the terminal, followed by a confirmation that it was
emailed (or a notice that emailing was skipped).

## Notes

- Data is scraped from a public website; if the page layout changes, the scraper may need
  updating. The history parser includes a guard that keeps 24K ≥ 22K even if the source
  reorders its columns.
- The model is set in `agent.py` (`MODEL`), defaulting to `openrouter/openai/gpt-4o-mini`.
  Alternatives are listed in the comments there.
- Run locally — sandboxed environments often block the financial data endpoint.
