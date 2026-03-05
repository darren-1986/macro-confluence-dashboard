import os
from datetime import datetime

# Step 2a: Ensure output folder exists
os.makedirs("dashboard_build", exist_ok=True)

# Step 2b: HTML content
html = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>Macro Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; background:#0f172a; color:#e5e7eb; padding:40px; }}
h1 {{ color:#38bdf8; }}
.card {{ background:#020617; padding:20px; border-radius:8px; margin-bottom:30px; }}
.timestamp {{ margin-top:40px; font-size:0.9rem; color:#94a3b8; }}
</style>
</head>
<body>
<h1>Macro Dashboard (AUD/USD & Gold Placeholder)</h1>

<div class="card">
<p>Gold Price: 1950.50 USD</p>
<p>AUD/USD: 0.6745</p>
<p>Trend: Neutral</p>
</div>

<div class="timestamp">
Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
</div>
</body>
</html>
"""

# Step 2c: Write the HTML file
file_path = "dashboard_build/index.html"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Dashboard generated successfully at {file_path}!")
