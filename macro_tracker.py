import os
from datetime import datetime, timezone
import yfinance as yf
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

# Create build folder
os.makedirs("dashboard_build", exist_ok=True)

def safe_fetch(symbol):
    """Fetch last 30 days, return series or empty Series"""
    try:
        hist = yf.Ticker(symbol).history(period="30d")
        return hist['Close'] if 'Close' in hist else pd.Series()
    except:
        return pd.Series()

def status_class(value):
    try:
        num = float(str(value).replace("%",""))
        if num > 3: return "bear"
        elif num < 1: return "bull"
        else: return "neutral"
    except:
        s = str(value).lower()
        if any(k in s for k in ["bull","rising"]): return "bull"
        if any(k in s for k in ["bear","falling"]): return "bear"
        return "neutral"

def trend_arrow(series):
    if len(series) < 2: return "→"
    if series.iloc[-1] > series.iloc[0]: return "↑"
    if series.iloc[-1] < series.iloc[0]: return "↓"
    return "→"

def create_graph(data, title, color):
    plt.figure(figsize=(4,1))
    if not data.empty:
        plt.plot(data, color=color)
    plt.xticks([])
    plt.yticks([])
    plt.title(title, fontsize=10, color="#ffffff")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", transparent=True)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

# Symbols we care about
symbols = [
    ("GC=F","Gold","#facc15"),
    ("AUDUSD=X","AUD/USD","#38bdf8"),
    ("^TNX","US 10Y Yield","#f472b6"),
    ("^VIX","VIX","#f87171")
]

assets = {}
histories = {}
graphs = {}
trends = {}

for sym, name, color in symbols:
    series = safe_fetch(sym)
    histories[name] = series
    assets[name] = series.iloc[-1] if not series.empty else "N/A"
    graphs[name] = create_graph(series, name, color)
    trends[name] = trend_arrow(series)

# Correlation Gold <-> AUD/USD
try:
    combined = pd.concat([histories["Gold"], histories["AUD/USD"]], axis=1)
    combined.columns = ["Gold","AUDUSD"]
    correlation = combined["Gold"].corr(combined["AUDUSD"])
    correlation_text = f"{correlation:.2f}" if correlation is not None else "N/A"
    correlation_class = "bull" if correlation>0 else "bear" if correlation<0 else "neutral"
except:
    correlation_text = "N/A"
    correlation_class = "neutral"

# Macro regime
classes = {name: status_class(val) for name,val in assets.items()}
bear_count = list(classes.values()).count("bear")
bull_count = list(classes.values()).count("bull")

if bear_count >= 3: macro_regime, regime_class = "RISK-OFF","bear"
elif bull_count >= 3: macro_regime, regime_class = "RISK-ON","bull"
else: macro_regime, regime_class = "TRANSITION","neutral"

# Asset bias
gold_bias = "Bullish" if macro_regime=="RISK-OFF" else "Bearish" if macro_regime=="RISK-ON" else "Neutral"
aud_bias = "Bullish" if macro_regime=="RISK-ON" else "Bearish" if macro_regime=="RISK-OFF" else "Neutral"

# Build HTML
sections_html = ""
for name in ["Gold","AUD/USD","US 10Y Yield","VIX"]:
    val = assets.get(name,"N/A")
    cls = status_class(val)
    trend = trends.get(name,"→")
    graph = graphs.get(name,"")
    sections_html += f"""
    <div class='card'>
        <h2>{name}</h2>
        <table><tr><td>{val} {trend}</td><td class='{cls}'>{cls.title()}</td></tr></table>
        <img class='graph' src='data:image/png;base64,{graph}'>
    </div>
    """

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

html = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>Macro Dashboard</title>
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
.graph {{ display:block; margin-top:5px; }}
</style>
</head>
<body>

<h1>Macro Dashboard (AUD/USD & Gold Focus)</h1>

<div class='card'>
<h2>Macro Regime</h2>
<p class='{regime_class}' style='font-size:1.6rem'>{macro_regime}</p>
</div>

{sections_html}

<div class='card'>
<h2>Assets Correlation</h2>
<table>
<tr><td>Gold ↔ AUD/USD (30d)</td><td class='{correlation_class}'>{correlation_text}</td></tr>
</table>
</div>

<div class='timestamp'>Last updated: {now}</div>
</body>
</html>
"""

# Always write the file, even if some data failed
os.makedirs("dashboard_build", exist_ok=True)
with open("dashboard_build/index.html","w",encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated successfully!")
