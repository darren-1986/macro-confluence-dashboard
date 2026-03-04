import csv
from collections import defaultdict
from datetime import datetime, timezone

# -----------------------------
# STATUS → COLOR MAP
# -----------------------------
def status_class(status: str) -> str:
    s = status.lower()
    if any(k in s for k in ["bull", "rising", "expansion"]):
        return "bull"
    if any(k in s for k in ["neutral", "stable"]):
        return "neutral"
    if any(k in s for k in ["bear", "falling", "inverted", "restrictive", "contraction"]):
        return "bear"
    return "neutral"

# -----------------------------
# LOAD CSV
# -----------------------------
data = defaultdict(list)

with open("macro_data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data[row["category"]].append({
            "indicator": row["indicator"],
            "status": row["status"],
            "class": status_class(row["status"])
        })

# -----------------------------
# TIMESTAMP
# -----------------------------
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# -----------------------------
# BUILD HTML
# -----------------------------
sections_html = ""

for category, items in data.items():
    rows = ""
    for item in items:
        rows += f"""
        <tr>
            <td>{item['indicator']}</td>
            <td class="{item['class']}">{item['status']}</td>
        </tr>
        """

    sections_html += f"""
    <div class="card">
        <h2>{category}</h2>
        <table>
            {rows}
        </table>
    </div>
    """

html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Macro Confluence Dashboard</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: #e5e7eb;
    padding: 40px;
}}
h1 {{ color: #38bdf8; }}
h2 {{ color: #7dd3fc; }}

.card {{
    background: #020617;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 30px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

td {{
    padding: 8px;
    border-bottom: 1px solid #1e293b;
}}

.bull {{
    color: #4ade80;
    font-weight: bold;
}}

.neutral {{
    color: #facc15;
}}

.bear {{
    color: #f87171;
    font-weight: bold;
}}

.timestamp {{
    margin-top: 40px;
    font-size: 0.9rem;
    color: #94a3b8;
}}
</style>
</head>
<body>

<h1>Macro Confluence Dashboard</h1>

{sections_html}

<div class="timestamp">
Last updated: {now}
</div>

<div class="card">
    <h2>Data Sources</h2>
    <ul>
        <li>Federal Reserve Economic Data (FRED)</li>
        <li>US Treasury</li>
        <li>Bureau of Labor Statistics (BLS)</li>
        <li>Bureau of Economic Analysis (BEA)</li>
        <li>Institute for Supply Management (ISM)</li>
        <li>Public central bank releases</li>
    </ul>
</div>

</body>
</html>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated with color coding")
