python
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone

# Get the current timestamp (Python 3.12+ compliant)
last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

assets = {
    "Gold": "GC=F",
    "USD Index": "DX-Y.NYB",
    "AUD/USD": "AUDUSD=X"
}

# Define colors for each signal
colors = {
    "BUY": "#2e7d32",      # Dark Green
    "SELL": "#c62828",     # Dark Red
    "NEUTRAL": "#424242",  # Dark Grey
    "ERROR": "#b71c1c",
    "NO DATA": "#37474f"
}

rows = []

for name, ticker in assets.items():
    try:
        df = yf.Ticker(ticker).history(period="1y")

        if df.empty or len(df) < 200:
            status = "NO DATA"
            color = colors[status]
            rows.append(f"<tr><td>{name}</td><td style='background:{color}; font-weight:bold;'>{status}</td></tr>")
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

        # Apply color based on the signal
        bg_color = colors.get(signal, "#333")
        rows.append(f"<tr><td>{name}</td><td style='background:{bg_color}; font-weight:bold;'>{signal}</td></tr>")

    except Exception as e:
        error_color = colors["ERROR"]
        rows.append(f"<tr><td>{name}</td><td style='background:{error_color};'>ERROR</td></tr>")

html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Macro Confluence Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; background:#111; color:#eee; display: flex; flex-direction: column; align-items: center; padding-top: 50px; }}
table {{ border-collapse: collapse; width:400px; text-align: center; }}
td, th {{ border:1px solid #444; padding:12px; }}
th {{ background:#222; color: #aaa; text-transform: uppercase; font-size: 12px; }}
h1 {{ margin-bottom: 20px; }}
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

print(f"Dashboard generated at {last_updated}")
