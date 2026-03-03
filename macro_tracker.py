import yfinance as yf
import pandas as pd

assets = {
    "Gold": "GC=F",
    "S&P 500": "^GSPC",
    "USD Index": "DX-Y.NYB",
    "Bitcoin": "BTC-USD",
    "EUR/USD": "EURUSD=X"
}

rows = []

for name, ticker in assets.items():
    df = yf.download(ticker, period="1y", interval="1d", progress=False)

    if df.empty or len(df) < 200:
        continue

    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()

    last = df.iloc[-1]
    close = last["Close"]
    sma50 = last["SMA50"]
    sma200 = last["SMA200"]

    if close > sma50 > sma200:
        signal = "BUY"
    elif close < sma50 < sma200:
        signal = "SELL"
    else:
        signal = "NEUTRAL"

    rows.append(f"<tr><td>{name}</td><td>{signal}</td></tr>")

html = f"""
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
</body>
</html>
"""

with open("dashboard.html", "w") as f:
    f.write(html)

print("Dashboard generated")
