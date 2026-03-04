import os
from datetime import datetime, timezone
import yfinance as yf
from fredapi import Fred

# -----------------------------
# CONFIG
# -----------------------------
os.makedirs("dashboard_build", exist_ok=True)
FRED_API_KEY = os.environ.get("FRED_API_KEY")  # Must be set in GitHub Actions

# -----------------------------
# STATUS → COLOR
# -----------------------------
def status_class(value):
    try:
        num = float(str(value).replace("%",""))
        if num > 3: return "bear"
        elif num < 1: return "bull"
        else: return "neutral"
    except:
        s = str(value).lower()
        if any(k in s for k in ["bull","rising","expansion","easing","cooling","improving"]): return "bull"
        if any(k in s for k in ["bear","falling","inverted","restrictive","contraction","sticky","elevated","high","stress"]): return "bear"
        return "neutral"

# -----------------------------
# ASSETS (Yahoo Finance)
# -----------------------------
assets = {}
for symbol,name in [("GC=F","Gold"),("AUDUSD=X","AUD/USD"),("^TNX","US 10Y Yield"),("^VIX","VIX")]:
    try:
        assets[name] = yf.Ticker(symbol).history(period="1d")['Close'].iloc[-1]
        if name=="US 10Y Yield":
            assets[name] /= 100
    except:
        assets[name] = "N/A"

# -----------------------------
# MACRO DATA (FRED)
# -----------------------------
macro_data = {}
if FRED_API_KEY:
    fred = Fred(api_key=FRED_API_KEY)
    try:
        macro_data["Inflation"] = {"CPI": round(fred.get_series("CPIAUCNS")[-1],2)}
        macro_data["Growth"] = {"Unemployment": round(fred.get_series("UNRATE")[-1],2)}
        macro_data["Liquidity"] = {
            "Fed Balance Sheet": round(fred.get_series("WALCL")[-1],2),
            "Reverse Repo": round(fred.get_series("RRPONTSYD")[-1],2),
            "Treasury General Account": round(fred.get_series("TGA")[-1],2)
        }
    except Exception as e:
        print("FRED fetch failed:", e)
        macro_data = {}
else:
    print("No FRED API key, skipping macro indicators")
    macro_data["Inflation"] = {"CPI":"N/A"}
    macro_data["Growth"] = {"Unemployment":"N/A"}
    macro_data["Liquidity"] = {"Fed Balance Sheet":"N/A","Reverse Repo":"N/A","Treasury General Account":"N/A"}

# Risk Sentiment and Rates from assets
macro_data["Risk Sentiment"] = {"VIX": assets.get("VIX","N/A")}
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
# BUILD HTML
# -----------------------------
sections_html = ""
for category, indicators in macro_data.items():
    rows = "".join([f"<tr><td>{k}</td><td class='{status_class(v)}'>{v}</td></tr>" for k,v in indicators.items()])
    sections_html += f"<div class='card'><h2>{category}</h2><table>{rows}</table></div>"

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

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
<li>Yahoo Finance (Gold, AUD/USD, US 10Y Yield, VIX)</li>
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
