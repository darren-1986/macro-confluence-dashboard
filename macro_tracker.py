import os
from datetime import datetime
import csv
import requests

os.makedirs("dashboard_build", exist_ok=True)

# --- 1️⃣ AUD/USD fetch ---
def fetch_audusd():
    try:
        r = requests.get("https://api.exchangerate.host/latest?base=AUD&symbols=USD")
        r.raise_for_status()
        data = r.json()
        if 'rates' not in data or 'USD' not in data['rates']:
            print(f"⚠ Unexpected API response: {data}")
            return [0.0]*5, 0.0
        rate = data['rates']['USD']
        return [rate]*5, rate
    except Exception as e:
        print(f"❌ Failed to fetch AUD/USD: {e}")
        return [0.0]*5, 0.0

# --- 2️⃣ Gold fetch from CSV fallback ---
def fetch_gold():
    prices = []
    try:
        with open("data/gold.csv", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                prices.append(float(row[1]))
        if not prices:
            return [0.0]*5, 0.0
        return prices[-5:], prices[-1]  # last 5 prices
    except Exception as e:
        print(f"❌ Failed to fetch Gold from CSV: {e}")
        return [0.0]*5, 0.0

aud_prices, audusd = fetch_audusd()
gold_prices, gold = fetch_gold()

# --- Trend calculation ---
def trend(prices):
    if len(prices) < 2: return "↔"
    if prices[-1] > prices[-2]: return "↑"
    elif prices[-1] < prices[-2]: return "↓"
    else: return "↔"

trend_audusd = trend(aud_prices)
trend_gold = trend(gold_prices)

# --- HTML Dashboard ---
html_file = "dashboard_build/index.html"
with open(html_file, "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>Macro Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {{ font-family: Arial,sans-serif; background:#0f172a; color:#e5e7eb; padding:40px; }}
h1 {{ color:#38bdf8; }}
.card {{ background:#020617; padding:20px; border-radius:8px; margin-bottom:30px; }}
.price {{ font-size:1.5rem; }}
.trend-up {{ color:#22c55e; }}
.trend-down {{ color:#ef4444; }}
.trend-flat {{ color:#facc15; }}
.canvas-container {{ width:300px; height:100px; }}
.timestamp {{ margin-top:40px; font-size:0.9rem; color:#94a3b8; }}
</style>
</head>
<body>
<h1>Macro Dashboard (AUD/USD & Gold)</h1>

<div class="card">
<p class="price">Gold: {gold:.2f} USD <span class="{'trend-up' if trend_gold=='↑' else 'trend-down' if trend_gold=='↓' else 'trend-flat'}">{trend_gold}</span></p>
<canvas id="goldChart" class="canvas-container"></canvas>
</div>

<div class="card">
<p class="price">AUD/USD: {audusd:.4f} <span class="{'trend-up' if trend_audusd=='↑' else 'trend-down' if trend_audusd=='↓' else 'trend-flat'}">{trend_audusd}</span></p>
<canvas id="audChart" class="canvas-container"></canvas>
</div>

<div class="timestamp">
Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
</div>

<script>
const goldCtx = document.getElementById('goldChart').getContext('2d');
new Chart(goldCtx, {{
    type: 'line',
    data: {{ labels: {list(range(len(gold_prices)))}, datasets: [{{ data: {gold_prices}, borderColor: '#fbbf24', backgroundColor: 'rgba(251,191,36,0.2)', tension: 0.3, fill: true }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
}});

const audCtx = document.getElementById('audChart').getContext('2d');
new Chart(audCtx, {{
    type: 'line',
    data: {{ labels: {list(range(len(aud_prices)))}, datasets: [{{ data: {aud_prices}, borderColor: '#38bdf8', backgroundColor: 'rgba(56,189,248,0.2)', tension: 0.3, fill: true }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
}});
</script>
</body>
</html>""")

print(f"✅ Dashboard generated at {html_file}")
