import yfinance as yf
import pandas as pd

from datetime import datetime
last_updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

assets = {
    "Gold": "GC=F",
    "USD Index": "DX-Y.NYB",
    "AUD/USD": "AUDUSD=X"
}

rows = []

for name, ticker in assets.items():
    try:
        df = yf.Ticker(ticker).history(period="1y")

        if df.empty or len(df) < 200:
            rows.append(f"<tr><td>{name}</td><td>NO DATA</td></tr>")
            continue

        close_series = df["Close"]

        close = close_series.iloc[-1]
        sma50 = close_series.rolling(50).mean().iloc[-1]
        sma200 = close_series.rolling(200).mean().iloc[-1]

        if close > sma50 and sma50 > sma200:
            signal = "BUY"
        elif close < sma50 and sma50 < sma200:
            signal = "SELL"
        else:
            signal = "NEUTRAL"

        rows.append(f"<tr><td>{name}</td><td>{signal}</td></tr>")

    except Exception as e:
        rows.append(f"<tr><td>{name}</td><td>ERROR</td></tr>")

html = f"""

<!DOCTYPE html>
<html>
<head>
<title>Macro Confluence Dashboard</title>
<style>
body {{ font-family: Arial; background:#111; color:#eee }}
table {{ border-collapse: collapse; width:50% }}
td, th {{ border:1px solid #555; padding:8px }}
th {{ background:#222 }}
</style>
</head>
<body>
<h1>Macro Confluence Dashboard</h1>
<table>
<tr><th>Asset</th><th>Signal</th></tr>
{''.join(rows)}
</table>
<p style="opacity:0.6;font-size:12px;margin-top:20px;">
Last updated: {last_updated}
</p>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html)

print("Dashboard generated")
