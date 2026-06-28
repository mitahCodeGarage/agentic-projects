"""
Mail utility — sends the gold rate report via Gmail SMTP.

Credentials and recipient are read from the environment (loaded from .env):
  • GMAIL_ADDRESS       your Gmail address (the sender)
  • GMAIL_APP_PASSWORD  a Gmail App Password (NOT your normal password;
                        create one at https://myaccount.google.com/apppasswords)
  • GMAIL_TO            recipient (optional — defaults to mitahworkplace@gmail.com)
"""

import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from rich.console import Console

console = Console()


def send_report_email(report: str) -> None:
    """
    Email the report via Gmail SMTP (smtp.gmail.com:587, STARTTLS).

    Credentials are read from the environment — never hard-coded:
      • GMAIL_ADDRESS       your Gmail address (the sender)
      • GMAIL_APP_PASSWORD  a Gmail App Password (NOT your normal password)
    """
    sender = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    # Recipient for the report. Override with the GMAIL_TO env var.
    email_to = os.getenv("GMAIL_TO", "mitahworkplace@gmail.com")

    if not sender or not app_password:
        console.print(
            "[yellow]⚠  Skipping email: set GMAIL_ADDRESS and GMAIL_APP_PASSWORD "
            "env vars to enable sending.[/yellow]"
        )
        return

    today = datetime.now().strftime("%d %b %Y")
    msg = EmailMessage()
    msg["Subject"] = f"Mumbai Gold Rate Report — {today}"
    msg["From"] = sender
    msg["To"] = email_to
    msg.set_content(report)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(sender, app_password)
            smtp.send_message(msg)
        console.print(f"[green]✓  Report emailed to {email_to}[/green]")
    except Exception as e:
        console.print(f"[red]✗  Failed to send email: {e}[/red]")
