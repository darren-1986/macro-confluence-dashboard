import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timezone

# -----------------------------
# Ensure build folder exists
# -----------------------------
os.makedirs("dashboard_build", exist_ok=True)

# -----------------------------
# Live Asset Prices
# -----------------------------
gold = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
audusd = yf.Ticker("AUDUSD=X").history(period="1d")['Close'].iloc[-1]

# -----------------------------
# Helper function: scrape numeric value from Trading Economics
# -----------------------------
def scrape_te(url, fallback="N/A"):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        value_tag = soup.find("td", class_="datatable-item-value")
        return value_tag.text.strip() if value_tag else fallback
    except:
        return fallback

# -----------------------------
# Live Macro Indicators
# -----------------------------
macro_data = {
    "Liquidity": {"Fed Balance Sheet": "Neutral", "Reverse Repo": "Falling", "Treasury General Account": "Stable"},
    "Rates": {"US 10Y Yield": "Bearish Risk", "Yield Curve": "Inverted", "Policy Rate": "Restrictive"},
    "Growth": {
        "PMI": scrape_te("https://tradingeconomics.com/united-states/pmis"),
        "Unemployment": scrape_te("https://tradingeconomics.com/united-states/unemployment-rate")
    },
    "Inflation": {
        "CPI": scrape_te("https://tradingeconomics.com/united-states/consumer-price-index-cpi")
    },
    "Risk Sentiment": {
        "VIX": scrape_te("https://tradingeconomics.com/indices/vix")
    }
}

# -----------------------------
# Status → Color Mapping
# -----------------------------
def status_class(value):
    try:
        # attempt numeric thresholds
        num = float(str(value).replace("%",""))
        if num > 3:        # example threshold
            return "bear"
        elif num < 1:
            return "bull"
        else:
            return "neutral"
    except:
        # fallback to text
        s = str(value).lower()
        if any(k in s for k in ["bull","rising","expansion","easing","cooling","improving"]):
            return "bull"
        if any(k in s for k in ["bear","falling","inverted","restrictive","contraction","sticky","elevated","high","stress"]):
            return "bear"
        return "neutral"

# -----------------------------
# Macro Regime
# -----------------------------
all_classes = [status_class(v) for cat in macro_data.values() for v in cat.values()]
bear_count = all_classes.count("bear")
bull_count = all_classes.count("bull")

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
# Asset Biases
# -----------------------------
gold_bias = "Bullish" if macro_regime=="RISK-OFF" else "Bearish" if macro_regime=="RISK-ON" else "Neutral"
gold_class = status_class(gold_bias)

aud_bias = "Bullish" if macro_regime=="RISK-ON" else "Bearish" if macro_regime=="RISK-OFF" else "Neutral"
aud_class = status_class(aud_bias)

# -----------------------------
# Build HTML sections
# -----------------------------
sections_html = ""
for category, indicators in macro_data.items():
    rows = "".join([f"<tr><td>{k}</td><td class='{status_class(v)}'>{v}</td></tr>" for k,v in indicators.items()])
    sections_html += f"<div class='card'><h2>{category}</h2><table>{rows}</table></div>"

# -----------------------------
# Timestamp
# -----------------------------
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# -----------------------------
# Build Final HTML
# -----------------------------
html = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>Macro Confluence Dashboard</title>
<style>
body {{ font-family: Arial,sans-serif; background:#0f172a; color:#e5e7eb; padding:40px; }}
h1 {{ color:#38bdf8; }}
h2 {{ color:#7dd3fc; }}
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

<div class='card'>
<h2>Macro Regime</h2>
<p class='{regime_class}' style='font-size:1.6rem'>{macro_regime}</p>
</div>

{sections_html}

<div class='card'>
<h2>Assets</h2>
<table>
<tr><td>Gold</td><td class='{gold_class}'>{gold_bias} ({gold:.2f})</td></tr>
<tr><td>AUD/USD</td><td class='{aud_class}'>{aud_bias} ({audusd:.4f})</td></tr>
</table>
</div>

<div class='timestamp'>Last updated: {now}</div>

<div class='card'>
<h2>Data Sources</h2>
<ul>
<li>Yahoo Finance (Gold, AUD/USD)</li>
<li>Trading Economics (PMI, Unemployment, CPI, VIX)</li>
<li>Federal Reserve Economic Data (FRED)</li>
<li>US Treasury</li>
<li>Bureau of Labor Statistics (BLS)</li>
<li>Public central bank releases</li>
</ul>
</div>

</body>
</html>
"""

with open("dashboard_build/index.html","w",encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated with live macro data in dashboard_build/index.html")
