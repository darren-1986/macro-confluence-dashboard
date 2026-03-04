from datetime import datetime, timezone

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

html = f"""
<!DOCTYPE html>
<html lang="en">
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
        .timestamp {{
            margin-top: 20px;
            font-size: 0.9rem;
            color: #94a3b8;
        }}
        .card {{
            background: #020617;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>

<h1>Macro Confluence Dashboard</h1>

<div class="card">
    <p><strong>Status:</strong> Dashboard generated successfully.</p>
</div>

<div class="timestamp">
    Last updated: {now}
</div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html generated successfully")
