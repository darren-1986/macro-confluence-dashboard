import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

# -----------------------------
# STATUS → COLOR MAP
# -----------------------------
def status_class(status: str) -> str:
    s = status.lower()
    bullish_keywords = ["bull", "rising", "expansion", "easing", "cooling", "improving"]
    bearish_keywords = ["bear", "falling", "inverted", "restrictive", "contraction",
                        "sticky", "elevated", "above target", "widening", "tightening",
                        "high", "stress"]
    if any(k in s for k in bullish_keywords):
        return "bull"
    if any(k in s for k in bearish_keywords):
        return "bear"
    return "neutral"

# -----------------------------
# LIVE DATA
# -----------------------------
def get_yf_status(ticker_symbol):
    try:
        data = yf.Ticker(ticker_symbol).history(period="2d")['Close']
        change = (data[-1] - data[-2]) / data[-2] * 100
        status = "Rising" if change > 0 else "Falling" if change < 0 else "Stable"
        return status, status_class(status)
    except:
        return "Neutral", "neutral"

gold_status, gold_class = get_yf_status("GC=F")       # Gold
aud_status, aud_class = get_yf_status("AUDUSD=X")     # AUD/USD
vix_status, risk_class = get_yf_status("^VIX")        # Risk Sentiment

# Inflation (US CPI YoY)
try:
    page = requests.get("https://tradingeconomics.com/united-states/inflation-cpi")
    soup = BeautifulSoup(page.content, "html.parser")
    cpi = float(soup.select_one(".table-responsive td[data-key='Value']").text.strip())
    inflation_status = "Above target" if cpi > 3 else "Below target" if cpi < 2 else "Stable"
except:
    inflation_status = "Neutral"
inflation_class = status_class(inflation_status)

# Growth (PMI + Unemployment)
def get_te_value(url):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        value = float(soup.select_one(".table-responsive td[data-key='Value']").text.strip())
        return value
    except:
        return None

pmi_value = get_te_value("https://tradingeconomics.com/united-states/pmi")
pmi_status = "Expansion" if pmi_value and pmi_value > 50 else "Contraction" if pmi_value and pmi_value < 50 else "Neutral"

u_value = get_te_value("https://tradingeconomics.com/united-states/unemployment-rate")
u_status = "Rising" if u_value and u_value > 4.0 else "Falling" if u_value and u_value < 4.0 else "Stable"

growth_status_list = [pmi_status, u_status]
if "Contraction" in growth_status_list or "Falling" in growth_status_list:
    growth_status = "Contraction"
elif "Expansion" in growth_status_list or "Rising" in growth_status_list:
    growth_status = "Expansion"
else:
    growth_status = "Neutral"
growth_class = status_class(growth_status)

# -----------------------------
# MACRO REGIME
# -----------------------------
bear_count = sum([c == "bear" for c in [gold_class, aud_class, inflation_class, risk_class, growth_class]])
bull_count = sum([c == "bull" for c in [gold_class, aud_class, inflation_class, risk_class, growth_class]])

if bear_count >= 3:
    macro_regime = "RISK-OFF"
    regime_class = "bear"
elif bull_count >= 3:
    macro_regime = "RISK-ON"
    regime_class = "bull"
else:
    macro_regime = "TRANSITION"
    regime_class = "neutral"

# -----------------------------
# TIMESTAMP
# -----------------------------
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# -----------------------------
# BUILD HTML
# -----------------------------
html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Macro Confluence Dashboard</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: #e5e7eb;
    padding: 40px;
}}
h1 {{ color: #38bdf8; }}
h2 {{ color: #7dd3fc; }}

.card {{
    background: #020617;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 30px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

td {{
    padding: 8px;
    border-bottom: 1px solid #1e293b;
}}

.bull {{ color: #4ade80; font-weight: bold; }}
.neutral {{ color: #facc15; }}
.bear {{ color: #f87171; font-weight: bold; }}

.timestamp {{ margin-top: 40px; font-size: 0.9rem; color: #94a3b8; }}
</style>
</head>
<body>

<h1>Macro Confluence Dashboard</h1>

<div class="card">
    <h2>Macro Regime</h2>
    <p class="{regime_class}" style="font-size: 1.6rem;">{macro_regime}</p>
</div>

<div class="card">
    <h2>Assets</h2>
    <table>
        <tr><td>Gold</td><td class="{gold_class}">{gold_status}</td></tr>
        <tr><td>AUD/USD</td><td class="{aud_class}">{aud_status}</td></tr>
    </table>
</div>

<div class="card">
    <h2>Inflation & Risk Sentiment</h2>
    <table>
        <tr><td>Inflation</td><td class="{inflation_class}">{inflation_status}</td></tr>
        <tr><td>VIX / Risk</td><td class="{risk_class}">{risk_status}</td></tr>
    </table>
</div>

<div class="card">
    <h2>Growth</h2>
    <table>
        <tr><td>PMI</td><td class="{growth_class}">{pmi_status}</td></tr>
        <tr><td>Unemployment</td><td class="{growth_class}">{u_status}</td></tr>
        <tr><td>Overall Growth</td><td class="{growth_class}">{growth_status}</td></tr>
    </table>
</div>

<div class="timestamp">Last updated: {now}</div>

<div class="card">
    <h2>Data Sources</h2>
    <ul>
        <li>Yahoo Finance (Gold, AUD/USD, VIX)</li>
        <li>Trading Economics (US CPI, PMI, Unemployment)</li>
        <li>Public central bank releases</li>
    </ul>
</div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated with live Growth, PMI & Unemployment")
