python
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone

# 1. Update the timestamp using modern standards
last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

assets = {
    "Gold": "GC=F",
    "USD Index": "DX-Y.NYB",
    "AUD/USD": "AUDUSD=X"
}

# 2. Define your status colors
colors = {
    "BUY": "#2e7d32",      # Green
    "SELL": "#c62828",     # Red
    "NEUTRAL": "#424242",  # Grey
    "ERROR": "#b71c1c"
}

rows = []

for name, ticker in assets.items():
    try:
        df = yf.Ticker(ticker).history(period="1y")
        if df.empty or len(df) < 200:
            rows.append(f"<tr><td>{name}</td><td style='background:#333;'>NO DATA</td></tr>")
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

        bg = colors.get(signal, "#333")
        rows.append(f"<tr><td>{name}</td><td style='background:{bg}; font-weight:bold;'>{signal}</td></tr>")

    except Exception:
        rows.append(f"<tr><td>{name}</td><td style='background:{colors['ERROR']};'>ERROR</td></tr>")

# 3. Create HTML - Note the DOUBLE BRACES {{ }} in the <style> section!
html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Macro Dashboard</title>
<style>
    body {{ font-family: Arial; background:#111; color:#eee; text-align:center; }}
    table {{ border-collapse: collapse; width:50%; margin:auto; }}
    td, th {{ border:1px solid #555; padding:12px; }}
    th {{ background:#222; }}
</style>
</head>
<body>
    <h1>Macro Confluence Dashboard</h1>
    <table>
        <tr><th>Asset</th><th>Signal</th></tr>
        {''.join(rows)}
    </table>
    <p style="opacity:0.6; font-size:12px; margin-top:20px;">
        Last updated: {last_updated}
    </p>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html)

print(f"Success! Dashboard generated at {last_updated}")
