import os
from datetime import datetime, timezone

# Example data, replace with live scraping later
sections_html = """
<div class="card">
    <h2>Liquidity</h2>
    <table>
        <tr><td>Fed Balance Sheet</td><td class="neutral">Neutral</td></tr>
        <tr><td>Reverse Repo</td><td class="bear">Falling</td></tr>
    </table>
</div>
"""

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Macro Confluence Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; background: #0f172a; color: #e5e7eb; padding: 40px; }}
h1 {{ color: #38bdf8; }}
h2 {{ color: #7dd3fc; }}
.card {{ background: #020617; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
table {{ width: 100%; border-collapse: collapse; }}
td {{ padding: 8px; border-bottom: 1px solid #1e293b; }}
.bull {{ color: #4ade80; font-weight: bold; }}
.neutral {{ color: #facc15; }}
.bear {{ color: #f87171; font-weight: bold; }}
.timestamp {{ margin-top: 40px; font-size: 0.9rem; color: #94a3b8; }}
</style>
</head>
<body>
<h1>Macro Confluence Dashboard</h1>

{sections_html}

<div class="timestamp">
Last updated: {now}
</div>

</body>
</html>
"""

# Create dedicated build folder
os.makedirs("dashboard_build", exist_ok=True)

with open("dashboard_build/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated successfully in dashboard_build/")
