import os
from datetime import datetime
import requests

os.makedirs("dashboard_build", exist_ok=True)

# 1️⃣ Fetch AUD/USD from exchangerate.host
def fetch_audusd():
    try:
        r = requests.get("https://api.exchangerate.host/latest?base=AUD&symbols=USD")
        r.raise_for_status()
        rate = r.json()['rates']['USD']
        return [rate]*5, rate  # simple 5-day placeholder
    except Exception as e:
        print(f"❌ Failed to fetch AUD/USD: {e}")
        return [0.0]*5, 0.0

# 2️⃣ Fetch Gold price from metals-api.com
def fetch_gold():
    try:
        # Use your free API key from metals-api.com as an environment variable
        api_key = os.getenv("METALS_API_KEY")
        if not api_key:
            raise ValueError("METALS_API_KEY not set in GitHub secrets")
        r = requests.get(f"https://metals-api.com/api/latest?access_key={api_key}&base=USD&symbols=XAU")
        r.raise_for_status()
        price = r.json()['rates']['XAU']
        return [price]*5, price
    except Exception as e:
        print(f"❌ Failed to fetch Gold: {e}")
        return [0.0]*5, 0.0

# 3️⃣ Get data
aud_prices, audusd = fetch_audusd()
gold_prices, gold = fetch_gold()

# 4️⃣ Compute trends
def trend(prices):
    if len(prices) < 2: return "↔"
    if prices[-1] > prices[-2]: return "↑"
    elif prices[-1] < prices[-2]: return "↓"
    else: return "↔"

trend_audusd = trend(aud_prices)
trend_gold = trend(gold_prices)

# 5️⃣ Build HTML dashboard with mini charts
html = f"""
<!DOCTYPE html>
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
    data: {{
        labels: {list(range(len(gold_prices)))},
        datasets: [{{
            data: {gold_prices},
            borderColor: '#fbbf24',
            backgroundColor: 'rgba(251,191,36,0.2)',
            tension: 0.3,
            fill: true
        }}]
    }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
}});

const audCtx = document.getElementById('audChart').getContext('2d');
new Chart(audCtx, {{
    type: 'line',
    data: {{
        labels: {list(range(len(aud_prices)))},
        datasets: [{{
            data: {aud_prices},
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56,189,248,0.2)',
            tension: 0.3,
            fill: true
        }}]
    }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
}});
</script>
</body>
</html>
"""

with open("dashboard_build/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Dashboard generated at dashboard_build/index.html")
