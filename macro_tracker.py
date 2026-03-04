import yfinance as yf
import pandas as pd
from datetime import datetime, timezone

assets = {
    "Gold": "GC=F",
    "USD Index": "DX-Y.NYB",
    "AUD/USD": "AUDUSD=X"
}

rows = []

for name, ticker in assets.items():
    try:
        df = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if df.empty or len(df) < 200:
            rows.append(f"<tr><td>{name}</td><td>NO DATA</td></tr>")
            continue

        close = df["Close"].iloc[-1]
        sma50 = df["Close"].rolling(50).mean().iloc[-1]
        sma200 = df["Close"].rolling(200).mean().iloc[-1]

        if close > sma50 and sma50 > sma200:
            signal = "BUY"
        elif close < sma50 and sma50 < sma200:
            signal = "SELL"
        else:
            signal = "NEUTRAL"

        rows.append(f"<tr><td>{name}</td><td>{signal}</td></tr>")

    except Exception as e:
        rows.append(f"<tr><td>{name}</td><td>ERROR</td></tr>")

# 👇 THIS LINE FORCES A CHANGE EVERY RUN
updated_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

html = f"""
<html>
<head>
<title>Macro Confluence Dashboard</title>
<style>
body {{ font-family: Arial; background:#111; color:#eee }}
table {{ border-collapse: collapse; width:50% }}
td, th {{ border:1px solid #555; padding:8px }}
th {{ background:#222 }}
footer {{ margin-top:20px; font-size:12px; color:#aaa }}
</style>
</head>
<body>
<h1>Macro Confluence Dashboard</h1>

<table>
<tr><th>Asset</th><th>Signal</th></tr>
{''.join(rows)}
</table>

<footer>
Last updated: {updated_time}
</footer>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard updated at", updated_time)
