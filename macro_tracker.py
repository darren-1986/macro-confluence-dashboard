import csv
from collections import defaultdict
from datetime import datetime, timezone

# -----------------------------
# LOAD CSV DATA
# -----------------------------
data = defaultdict(list)

with open("macro_data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data[row["category"]].append({
            "indicator": row["indicator"],
            "status": row["status"]
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
            <td>{item['status']}</td>
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
h2 {{ color: #7dd3fc; margin-bottom: 10px; }}

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

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated from CSV")
