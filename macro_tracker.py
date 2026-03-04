import os
from datetime import datetime, timezone
import pandas as pd
import yfinance as yf

# -----------------------------
# Ensure build folder exists
# -----------------------------
os.makedirs("dashboard_build", exist_ok=True)

# -----------------------------
# Helper: Status → Color Map
# -----------------------------
def status_class(value):
    try:
        num = float(str(value).replace("%",""))
        # thresholds can be adjusted
        if num > 3:
            return "bear"
        elif num < 1:
            return "bull"
        else:
            return "neutral"
    except:
        s = str(value).lower()
        if any(k in s for k in ["bull","rising","expansion","easing","cooling","improving"]):
            return "bull"
        if any(k in s for k in ["bear","falling","inverted","restrictive","contraction","sticky","elevated","high","stress"]):
            return "bear"
        return "neutral"

# -----------------------------
# LIVE ASSETS (Yahoo Finance)
# -----------------------------
assets = {}
for symbol,name in [("GC=F","Gold"),("AUDUSD=X","AUD/USD"),("^TNX","US 10Y Yield"),("^VIX","VIX")]:
    try:
        assets[name] = yf.Ticker(symbol).history(period="1d")['Close'].iloc[-1]
    except:
        assets[name] = "N/A"

# TNX comes in percent, divide by 100
if assets.get("US 10Y Yield") != "N/A":
    assets["US 10Y Yield"] = assets["US 10Y Yield"] / 100

# -----------------------------
# LIVE MACRO FROM FRED
# -----------------------------
fred_series = {
    "Inflation": {"CPI": "CPIAUCNS"},
    "Growth": {"Unemployment": "UNRATE"},
    "Liquidity": {
        "Fed Balance Sheet": "WALCL",
        "Reverse Repo": "RRPONTSYD",
        "Treasury General Account": "TGA"
    }
}

macro_data = {}
for category, indicators in fred_series.items():
    macro_data[category] = {}
    for name, series in indicators.items():
        try:
            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
            value = pd.read_csv(url).iloc[-1][series]
            macro_data[category][name] = round(value, 2)
        except:
            macro_data[category][name] = "N/A"

# Risk Sentiment (VIX from Yahoo)
macro_data["Risk Sentiment"] = {"VIX": assets.get("VIX","N/A")}

# Rates (US 10Y Yield from Yahoo)
macro_data["Rates"] = {"US 10Y Yield": assets.get("US 10Y Yield","N/A")}

# -----------------------------
# MACRO REGIME
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
# ASSET BIASES
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
# Build final HTML
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
<tr><td>Gold</td><td class='{gold_class}'>{gold_bias} ({assets.get("Gold","N/A"):.2f})</td></tr>
<tr><td>AUD/USD</td><td class='{aud_class}'>{aud_bias} ({assets.get("AUD/USD","N/A"):.4f})</td></tr>
</table>
</div>

<div class='timestamp'>Last updated: {now}</div>

<div class='card'>
<h2>Data Sources</h2>
<ul>
<li>Yahoo Finance (Gold, AUD/USD, US 10Y, VIX)</li>
<li>FRED (CPI, Unemployment, Fed Balance Sheet, Reverse Repo, TGA)</li>
<li>US Treasury</li>
<li>Bureau of Labor Statistics (BLS)</li>
</ul>
</div>

</body>
</html>
"""

with open("dashboard_build/index.html","w",encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated with live macro data in dashboard_build/index.html")
