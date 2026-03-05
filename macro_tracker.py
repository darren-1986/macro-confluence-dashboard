import os
from datetime import datetime, timezone

# Ensure output folder exists
os.makedirs("dashboard_build", exist_ok=True)

# Placeholder data
assets = {
    "Gold": 1950.50,
    "AUD/USD": 0.6745
}
trends = {
    "Gold": "↑",
    "AUD/USD": "→"
}
status_classes = {
    "Gold": "neutral",
    "AUD/USD": "bull"
}

# Macro regime
bull_count = list(status_classes.values()).count("bull")
bear_count = list(status_classes.values()).count("bear")
if bear_count >= 2:
    macro_regime, regime_class = "RISK-OFF", "bear"
elif bull_count >= 2:
    macro_regime, regime_class = "RISK-ON", "bull"
else:
    macro_regime, regime_class = "TRANSITION", "neutral"

# HTML content
sections_html = ""
for name in ["Gold","AUD/USD"]:
    val = assets[name]
    cls = status_classes[name]
    trend = trends[name]
    sections_html += f"""
    <div class='card'>
        <h2>{name}</h2>
        <table><tr><td>{val} {trend}</td><td class='{cls}'>{cls.title()}</td></tr></table>
        <div style="width:100%; height:50px; background:#1e293b; border-radius:4px; margin-top:5px;"></div>
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

with open("dashboard_build/index.html","w",encoding="utf-8") as f:
    f.write(html)

print("✅ Dashboard generated successfully with placeholders!")
