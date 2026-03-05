import os
from datetime import datetime, timezone
import yfinance as yf
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

# Make sure the output folder exists
os.makedirs("dashboard_build", exist_ok=True)

# Helper: safe fetch from yfinance
def safe_fetch(symbol, name):
    try:
        hist = yf.Ticker(symbol).history(period="30d")
        if 'Close' in hist and not hist['Close'].empty:
            return hist['Close'], None
        else:
            return pd.Series(), f"No data for {name}"
    except Exception as e:
        return pd.Series(), str(e)

# Status class based on value
def status_class(value):
    try:
        v = float(value)
        if v > 3: return "bear"
        elif v < 1: return "bull"
        else: return "neutral"
    except:
        s = str(value).lower()
        if "bull" in s: return "bull"
        if "bear" in s: return "bear"
        return "neutral"

# Trend arrow
def trend_arrow(series):
    if len(series) < 2: return "→"
    if series.iloc[-1] > series.iloc[0]: return "↑"
    if series.iloc[-1] < series.iloc[0]: return "↓"
    return "→"

# Create base64 graph for embedding
def create_graph(series, title, color):
    plt.figure(figsize=(4,1))
    if not series.empty:
        plt.plot(series, color=color)
    plt.xticks([]); plt.yticks([])
    plt.title(title, fontsize=10, color="#ffffff")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", transparent=True)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

# Symbols we track
symbols = [
    ("GC=F","Gold","#facc15"),
    ("AUDUSD=X","AUD/USD","#38bdf8"),
]

assets = {}
histories = {}
graphs = {}
trends = {}
errors = []

# Fetch data safely
for sym, name, color in symbols:
    series, err = safe_fetch(sym, name)
    if err: errors.append(err)
    histories[name] = series
    assets[name] = series.iloc[-1] if not series.empty else 0  # placeholder 0
    graphs[name] = create_graph(series, name, color)
    trends[name] = trend_arrow(series)

# Macro regime
classes = {n: status_class(v) for n,v in assets.items()}
bear_count = list(classes.values()).count("bear")
bull_count = list(classes.values()).count("bull")
if bear_count >= 2: macro_regime, regime_class = "RISK-OFF","bear"
elif bull_count >= 2: macro_regime, regime_class = "RISK-ON","bull"
else: macro_regime, regime_class = "TRANSITION","neutral"

# HTML sections
sections_html = ""
for name in ["Gold","AUD/USD"]:
    val = assets.get(name,0)
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

# Timestamp
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# Build full HTML
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

<div class='timestamp'>Last updated: {now}</div>

</body>
</html>
"""

# Write HTML no matter what
os.makedirs("dashboard_build", exist_ok=True)
with open("dashboard_build/index.html","w",encoding="utf-8") as f:
    f.write(html)

# Print errors for GitHub Actions logs
if errors:
    print("⚠️ Some data fetch errors occurred:")
    for e in errors:
        print(e)
print("✅ Dashboard generated successfully!")
