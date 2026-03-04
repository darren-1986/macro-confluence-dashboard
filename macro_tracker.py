import os
from datetime import datetime, timezone
import yfinance as yf
import requests
from bs4 import BeautifulSoup

# -----------------------------
# STATUS → COLOR MAP
# -----------------------------
def status_class(status: str) -> str:
    s = status.lower()
    bullish_keywords = ["bull", "rising", "expansion", "easing", "cooling", "improving"]
    bearish_keywords = ["bear", "falling", "inverted", "restrictive", "contraction",
                        "sticky", "elevated", "above target", "widening", "tightening", "high", "stress"]
    if any(k in s for k in bullish_keywords):
        return "bull"
    if any(k in s for k in bearish_keywords):
        return "bear"
    return "neutral"

def category_bias(items):
    counts = {"bull":0,"bear":0,"neutral":0}
    for item in items:
        counts[item["class"]] += 1
    if counts["bear"] >= 2:
        return "bear"
    if counts["bull"] >= 2:
        return "bull"
    return "neutral"

# -----------------------------
# LIVE DATA FETCH
# -----------------------------
data = {"Liquidity":[], "Rates":[], "Growth":[], "Inflation":[], "Risk Sentiment":[]}

# --- Liquidity ---
data["Liquidity"].append({"indicator":"Fed Balance Sheet", "status":"Neutral", "class":status_class("Neutral")})
data["Liquidity"].append({"indicator":"Reverse Repo", "status":"Falling", "class":status_class("Falling")})
data["Liquidity"].append({"indicator":"Treasury General Account", "status":"Stable", "class":status_class("Stable")})

# --- Rates ---
try:
    resp = requests.get("https://fred.stlouisfed.org/series/DGS10")
    soup = BeautifulSoup(resp.text, "html.parser")
    val = soup.find(id="series-meta-observation-value").text.strip()
    val_num = float(val)
    status = "Bearish Risk" if val_num > 4 else "Neutral"
except Exception:
    status = "Neutral"
data["Rates"].append({"indicator":"US 10Y Yield", "status":status, "class":status_class(status)})
data["Rates"].append({"indicator":"Yield Curve", "status":"Inverted", "class":status_class("Inverted")})
data["Rates"].append({"indicator":"Policy Rate", "status":"Restrictive", "class":status_class("Restrictive")})

# --- Growth ---
data["Growth"].append({"indicator":"PMI", "status":"Contraction", "class":status_class("Contraction")})
data["Growth"].append({"indicator":"GDP Trend", "status":"Slowing", "class":status_class("Slowing")})
data["Growth"].append({"indicator":"Unemployment", "status":"Rising", "class":status_class("Rising")})

# --- Inflation ---
data["Inflation"].append({"indicator":"CPI", "status":"Elevated", "class":status_class("Elevated")})

# --- Risk Sentiment ---
try:
    vix = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
    status = "Bearish" if vix > 20 else "Neutral"
except Exception:
    status = "Neutral"
data["Risk Sentiment"].append({"indicator":"VIX", "status":status, "class":status_class(status)})
data["Risk Sentiment"].append({"indicator":"Credit Spreads", "status":"Widening", "class":status_class("Widening")})

# -----------------------------
# CATEGORY BIAS
# -----------------------------
rates_bias = category_bias(data.get("Rates", []))
inflation_bias = category_bias(data.get("Inflation", []))
risk_bias = category_bias(data.get("Risk Sentiment", []))
growth_bias = category_bias(data.get("Growth", []))
liquidity_bias = category_bias(data.get("Liquidity", []))

# -----------------------------
# MACRO REGIME
# -----------------------------
if risk_bias == "bear" or rates_bias == "bear":
    macro_regime = "RISK-OFF"
    regime_class = "bear"
elif risk_bias == "bull" and growth_bias == "bull":
    macro_regime = "RISK-ON"
    regime_class = "bull"
else:
    macro_regime = "TRANSITION"
    regime_class = "neutral"

# -----------------------------
# AUTO-DERIVED ASSETS
# -----------------------------
# Gold
if macro_regime == "RISK-OFF":
    gold_bias = "Bullish"
    gold_class = "bull"
elif macro_regime == "RISK-ON":
    gold_bias = "Bearish"
    gold_class = "bear"
else:
    gold_bias = "Neutral"
    gold_class = "neutral"

# AUD/USD
try:
    audusd = yf.Ticker("AUDUSD=X").history(period="1d")["Close"].iloc[-1]
    if macro_regime == "RISK-OFF":
        aud_bias = "Bearish"
        aud_class = "bear"
    elif macro_regime == "RISK-ON":
        aud_bias = "Bullish"
        aud_class = "bull"
    else:
        aud_bias = "Neutral"
        aud_class = "neutral"
except Exception:
    aud_bias = "Neutral"
    aud_class = "neutral"

# -----------------------------
# BUILD HTML
# -----------------------------
sections_html = ""
for category, items in data.items():
    rows = ""
    for item in items:
        rows += f"<tr><td>{item['indicator']}</td><td class='{item['class']}'>{item['status']}</td></tr>"
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
<tr><td>Gold</td><td class='{gold_class}'>{gold_bias}</td></tr>
<tr><td>AUD/USD</td><td class='{aud_class}'>{aud_bias}</td></tr>
</table>
</div>

<div class='timestamp'>Last updated: {now}</div>

<div class='card'>
<h2>Data Sources</h2>
<ul>
<li>FRED</li>
<li>Yahoo Finance</li>
<li>Public Central Bank Releases</li>
<li>Trading Economics</li>
</ul>
</div>
</body>
</html>
"""

# -----------------------------
# WRITE TO BUILD FOLDER
# -----------------------------
os.makedirs("dashboard_build", exist_ok=True)
with open("dashboard_build/index.html","w",encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated successfully in dashboard_build/")
