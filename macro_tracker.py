import yfinance as yf
from datetime import datetime, timezone

# 1. Define timestamp
last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

assets = {"Gold": "GC=F", "USD Index": "DX-Y.NYB", "AUD/USD": "AUDUSD=X"}
rows = ""

for name, ticker in assets.items():
    try:
        df = yf.Ticker(ticker).history(period="1y")
        
        # Check if we actually got data
        if not df.empty and len(df) >= 200:
            close = df["Close"].iloc[-1]
            sma50 = df["Close"].rolling(50).mean().iloc[-1]
            sma200 = df["Close"].rolling(200).mean().iloc[-1]

            if close > sma50 and sma50 > sma200:
                color, signal = "#2e7d32", "BUY"
            elif close < sma50 and sma50 < sma200:
                color, signal = "#c62828", "SELL"
            else:
                color, signal = "#424242", "NEUTRAL"
        else:
            color, signal = "#333", "NO DATA"

        # Build row string manually to avoid f-string issues
        rows += f"<tr><td>{name}</td><td style='background:{color}; color:white;'>{signal}</td></tr>"
    
    except Exception as e:
        rows += f"<tr><td>{name}</td><td>ERROR: {str(e)}</td></tr>"

# 2. Build HTML using a simple replace method instead of nested f-strings
html_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #111; color: #eee; font-family: sans-serif; text-align: center; }
        table { margin: auto; border-collapse: collapse; width: 300px; }
        td, th { border: 1px solid #444; padding: 10px; }
    </style>
</head>
<body>
    <h1>Macro Dashboard</h1>
    <table>
        <tr><th>Asset</th><th>Signal</th></tr>
        [ROWS]
    </table>
    <p>Last updated: [TIME]</p>
</body>
</html>
"""

final_html = html_template.replace("[ROWS]", rows).replace("[TIME]", last_updated)

with open("index.html", "w") as f:
    f.write(final_html)

print("Check index.html now.")
