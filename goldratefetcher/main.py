"""
Gold Rate Agent — Mumbai (runner)

Entry point: runs the CrewAI crew defined in agent.py, prints the report,
and emails it via Gmail SMTP.

Run locally — sandbox blocks most financial data endpoints.
"""

import sys

from rich.panel import Panel
from rich import box

from agent import crew, MODEL, console, OPENROUTER_API_KEY
from mail_utility import send_report_email


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    if OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY_HERE":
        console.print(
            Panel(
                "[bold red]⚠  OpenRouter API key not set![/bold red]\n\n"
                "Either:\n"
                "  • [cyan]export OPENROUTER_API_KEY=sk-or-v1-xxxx[/cyan]  then re-run, or\n"
                "  • Set OPENROUTER_API_KEY in your [bold].env[/bold] file.",
                title="Configuration Required",
                border_style="red",
            )
        )
        sys.exit(1)

    console.print(Panel.fit(
        "[bold yellow]🏅  Mumbai Gold Rate Agent[/bold yellow]\n"
        f"[dim]Model : {MODEL}[/dim]\n"
        "[dim]Powered by CrewAI + OpenRouter[/dim]",
        box=box.DOUBLE_EDGE,
        border_style="yellow",
    ))
    console.print()

    result = crew.kickoff()

    console.print()
    console.print(Panel(
        str(result),
        title="[bold yellow]📋  Gold Rate Report — Mumbai[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    ))

    # Email the report
    send_report_email(str(result))


if __name__ == "__main__":
    main()
