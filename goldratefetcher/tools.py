"""
CrewAI tools for the Mumbai Gold Rate Agent.

Scrapes goodreturns.in for Mumbai gold rates.

Exposes the @tool-decorated function:
  • get_gold_rate_history
"""

import requests
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from crewai.tools import tool
from rich.console import Console
from tabulate import tabulate

console = Console()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ─────────────────────────────────────────────────────────────
# SCRAPING HELPERS
# ─────────────────────────────────────────────────────────────

def _fetch_goodreturns() -> dict | None:
    """
    Attempt to scrape goodreturns.in for Mumbai gold rates.
    Returns dict with key: history (list of dicts with date/22k/24k keys).
    Returns None on failure.
    """
    try:
        url = "https://www.goodreturns.in/gold-rates/mumbai.html"
        session = requests.Session()
        session.headers.update(HEADERS)
        resp = session.get(url, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        data = {}

        # ── Historical rates ───────────────────────────────
        all_tables = soup.find_all("table")
        history = []
        for tbl in all_tables:
            rows = tbl.find_all("tr")
            for row in rows:
                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cols) >= 3:
                    # Check if first cell looks like a date
                    cell0 = cols[0]
                    months = ["Jan","Feb","Mar","Apr","May","Jun",
                              "Jul","Aug","Sep","Oct","Nov","Dec"]
                    if any(m in cell0 for m in months) or (
                        len(cell0) >= 8 and sum(c.isdigit() for c in cell0) >= 4
                    ):
                        # goodreturns.in column order is: Date | 24K | 22K
                        v24, v22 = cols[1], cols[2] if len(cols) > 2 else "-"

                        # Safety: 24K is always >= 22K. If the source ever
                        # reorders columns, swap back based on numeric value.
                        def _num(s):
                            digits = "".join(c for c in s if c.isdigit())
                            return int(digits) if digits else None

                        n24, n22 = _num(v24), _num(v22)
                        if n24 is not None and n22 is not None and n22 > n24:
                            v24, v22 = v22, v24

                        history.append({
                            "date": cell0,
                            "24k": v24,
                            "22k": v22,
                        })
                        if len(history) >= 10:
                            break
            if len(history) >= 10:
                break

        data["history"] = history
        return data if data else None

    except Exception as e:
        console.print(f"[yellow]goodreturns.in scrape failed: {e}[/yellow]")
        return None


# ─────────────────────────────────────────────────────────────
# CREWAI TOOLS
# ─────────────────────────────────────────────────────────────

@tool("Get Last 10 Days Gold Rate History Mumbai")
def get_gold_rate_history() -> str:
    """
    Fetches the last 10 days of gold rates in Mumbai (22K and 24K per 10g)
    from goodreturns.in. If too few rows are available, returns a static
    illustrative estimate. Returns a formatted ASCII table.
    """
    data = _fetch_goodreturns()

    history = data.get("history", []) if data else []

    if len(history) < 3:
        source = "estimated (source unavailable)"
        # Fallback: show a static illustrative table
        base_22k = 64500
        base_24k = 70300
        history = []
        for i in range(10):
            day = datetime.now() - timedelta(days=i)
            # Simulate ±0.5% daily drift
            drift = 1 + (((i * 17) % 5) - 2) / 1000
            p22 = int(base_22k * drift)
            p24 = int(base_24k * drift)
            history.append({
                "date": day.strftime("%d %b %Y"),
                "22k": f"₹{p22:,}",
                "24k": f"₹{p24:,}",
            })
    else:
        source = "goodreturns.in"

    rows = [(h["date"], h["22k"], h["24k"]) for h in history[:10]]
    table_str = tabulate(
        rows,
        headers=["Date", "22K / 10g", "24K / 10g"],
        tablefmt="rounded_outline",
        colalign=("left", "right", "right"),
    )
    return f"📊 Last 10 Days Gold Rates — Mumbai  [source: {source}]\n\n{table_str}"
