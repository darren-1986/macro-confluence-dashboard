import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def status_class(value, bull_thresh, bear_thresh):
    if value is None:
        return "neutral"
    if value >= bull_thresh:
        return "bull"
    elif value <= bear_thresh:
        return "bear"
    return "neutral"

def fetch_yf_price(ticker):
    try:
        price = yf.Ticker(ticker).history(period="1d")["Close"][-1]
        return float(price)
    except:
        return None

def fetch_cpi():
    try:
        url = "https://tradingeconomics.com/united-states/inflation-cpi"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        # Grab first number in page as CPI (simplified)
        cpi_text = soup.find("div", {"class":"col-xs-6"}).text
        cpi_value = float(cpi_text.split()[0].replace(",", ""))
        return cpi_value
    except:
        return None

def fetch_treasury_10y():
    try:
        url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv"
        r = requests.get(url)
        lines = r.text.splitlines()
        latest = lines[-1].split(",")
        yield10 = float(latest[7])  # Column 8 = 10Y
        yield2  = float(latest[3])  # Column 4 = 2Y
        return yield10, yield2
    except:
        return None, None

# -----------------------------
# LIVE DATA
# -----------------------------
cpi = fetch_cpi()
yield10, yield2 = fetch_treasury_10y()
yield_curve = yield10 - yield2 if yield10 and yield2 else None

audusd = fetch_yf_price("AUDUSD=X")
gold = fetch_yf_price("GC=F")
vix = fetch_yf_price("^VIX")

# -----------------------------
# DASHBOARD DATA
# -----------------------------
data = {
    "Liquidity": [
        ("Fed Balance Sheet", "Neutral", "neutral"),
        ("Reverse Repo", "Falling", "bear"),
        ("Treasury General Account", "Stable", "neutral")
    ],
    "Rates": [
        ("US 10Y Yield", f"{yield10:.2f}" if yield10 else "N/A", status_class(yield10, 3.0, 1.5)),
        ("Yield Curve", f"{yield_curve:.2f}" if yield_curve else "N/A", status_class(yield_curve, 1.0, 0.0)),
    ],
    "Growth": [
        ("PMI", "N/A", "neutral"),  # optional scrape later
        ("Unemployment", "N/A", "neutral")
    ],
    "Inflation": [
        ("CPI YoY", f"{cpi:.1f}%" if cpi else "N/A", status_class(cpi, 3, 1.5))
    ],
    "Risk Sentiment": [
        ("VIX", f"{vix:.1f}" if vix else "N/A", status_class(vix, 15, 30))
    ]
}

# -----------------------------
# MACRO REGIME
# -----------------------------
rates_bias = max([row[2] for row in data["Rates"]], key=lambda x: ["bear","neutral","bull"].index(x))
inflation_bias = max([row[2] for row in data["Inflation"]], key=lambda x: ["bear","neutral","bull"].index(x))
risk_bias = max([row[2] for row in data["Risk Sentiment"]], key=lambda x: ["bear","neutral","bull"].index(x))

if risk_bias == "bear" or rates_bias == "bear":
    macro_regime = "RISK-OFF"
    regime_class = "bear"
elif risk_bias == "bull":
    macro_regime = "RISK-ON"
    regime_class = "bull"
else:
    macro_regime = "TRANSITION"
    regime_class = "neutral"

# -----------------------------
# AUTO-DERIVED ASSET BIAS
# -----------------------------
if macro_regime == "RISK-OFF":
    gold_bias, gold_class = "Bullish", "bull"
    aud_bias, aud_class = "Bearish", "bear"
elif macro_regime == "RISK-ON":
    gold_bias, gold_class = "Bearish", "bear"
    aud_bias, aud_class = "Bullish", "bull"
else:
    gold_bias, gold_class = "Neutral", "neutral"
    aud_bias, aud_class = "Neutral", "neutral"

# -----------------------------
# TIMESTAMP
# -----------------------------
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# -----------------------------
# BUILD HTML
# -----------------------------
sections_html = ""
for category, items in data.items():
    rows = ""
    for name, val, cls in items:
        rows += f"<tr><td>{name}</td><td class='{cls}'>{val}</td></tr>\n"
    sections_html += f"<div class='card'><h2>{category}</h2><table>{rows}</table></div>"

html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Macro Confluence Dashboard</title>
<style>
body {{ font-family: Arial; background:#0f172a; color:#e5e7eb; padding:40px; }}
h1 {{ color:#38bdf8; }} h2 {{ color:#7dd3fc; }}
.card {{ background:#020617; padding:20px; border-radius:8px; margin-bottom:30px; }}
table {{ width:100%; border-collapse:collapse; }}
td {{ padding:8px; border-bottom:1px solid #1e293b; }}
.bull {{ color:#4ade80; font-weight:bold; }}
.neutral {{ color:#facc15; }}
.bear {{ color:#f87171; font-weight:bold; }}
.timestamp {{ margin-top:40px; font-size:0.9rem; color:#94a3b8; }}
</style>
</head>
<body>
<h1>Macro Confluence Dashboard</h1>

<div class='card'><h2>Macro Regime</h2>
<p class='{regime_class}' style='font-size:1.6rem'>{macro_regime}</p></div>

{sections_html}

<div class='card'><h2>Assets</h2>
<table>
<tr><td>Gold</td><td class='{gold_class}'>{gold_bias}</td></tr>
<tr><td>AUD/USD</td><td class='{aud_class}'>{aud_bias}</td></tr>
</table></div>

<div class='timestamp'>Last updated: {now}</div>

<div class='card'><h2>Data Sources</h2>
<ul>
<li>Trading Economics (CPI)</li>
<li>US Treasury (10Y Yield)</li>
<li>Yahoo Finance (Gold, AUD/USD, VIX)</li>
<li>Public central bank releases</li>
</ul></div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Live Macro Dashboard generated successfully!")
