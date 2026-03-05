import os
from datetime import datetime
import yfinance as yf

# 1️⃣ Ensure output folder exists
os.makedirs("dashboard_build", exist_ok=True)

# 2️⃣ Get data for AUD/USD and Gold
audusd = yf.Ticker("AUDUSD=X").history(period="1d")['Close'][-1]
gold = yf.Ticker("GC=F").history(period="1d")['Close'][-1]

# 3️⃣ Placeholder trends
trend_audusd = "↔"
trend_gold = "↔"

# 4️⃣ Build HTML
html = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>Macro Dashboard</title>
<style>
body {{ font-family: Arial,sans-serif; background:#0f172a; color:#e5e7eb; padding:40px; }}
h1 {{ color:#38bdf8; }}
.card {{ background:#020617; padding:20px; border-radius:8px; margin-bottom:30px; }}
.timestamp {{ margin-top:40px; font-size:0.9rem; color:#94a3b8; }}
</style>
</head>
<body>
<h1>Macro Dashboard (AUD/USD & Gold)</h1>
<div class="card">
<p>Gold Price: {gold:.2f} USD {trend_gold}</p>
<p>AUD/USD: {audusd:.4f} {trend_audusd}</p>
</div>
<div class="timestamp">
Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
</div>
</body>
</html>
"""

# 5️⃣ Write HTML to file
with open("dashboard_build/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Dashboard generated at dashboard_build/index.html")
