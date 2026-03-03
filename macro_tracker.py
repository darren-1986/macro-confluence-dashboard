
assets = {
    "Gold": "GC=F",
    "USD Index": "DX-Y.NYB",
    "AUD/USD": "AUDUSD=X"
}

rows = ""

print("Generating Dashboard...")

for name, ticker in assets.items():
    try:
        # We use 2y to guarantee enough data for the SMA200 calculation
        df = yf.Ticker(ticker).history(period="2y")
        
        # FIX: Ensure columns are a simple list (fixes recent yfinance multi-index issues)
        if hasattr(df.columns, 'levels'):
            df.columns = df.columns.get_level_values(0)

        # Check if we actually have data
        if df.empty or len(df) < 200:
            rows += f"<tr><td>{name}</td><td style='background:#333; color:white;'>NO DATA</td></tr>"
            continue

        # Technical Analysis
        close = df["Close"].iloc[-1]
        sma50 = df["Close"].rolling(50).mean().iloc[-1]
        sma200 = df["Close"].rolling(200).mean().iloc[-1]

        if close > sma50 and sma50 > sma200:
            color, signal = "#2e7d32", "BUY"
        elif close < sma50 and sma50 < sma200:
            color, signal = "#c62828", "SELL"
        else:
            color, signal = "#424242", "NEUTRAL"

        rows += f"<tr><td>{name}</td><td style='background:{color}; color:white; font-weight:bold;'>{signal}</td></tr>"

    except Exception as e:
        print(f"Error for {name}: {e}")
        rows += f"<tr><td>{name}</td><td style='background:#7f0000; color:white;'>ERROR</td></tr>"

# 2. Build the final HTML using a safer .replace() method to avoid CSS brace conflicts
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Macro Dashboard</title>
    <style>
        body { font-family: sans-serif; background: #111; color: #eee; text-align: center; padding-top: 50px; }
        table { border-collapse: collapse; width: 350px; margin: 20px auto; }
        td, th { border: 1px solid #444; padding: 12px; }
        th { background: #222; color: #aaa; font-size: 11px; text-transform: uppercase; }
    </style>
</head>
<body>
    <h1>Macro Confluence</h1>
    <table>
        <tr><th>Asset</th><th>Signal</th></tr>
        {{ROWS}}
    </table>
    <p style="opacity:0.5; font-size:12px;">Last updated: {{TIME}}</p>
</body>
</html>
"""

final_html = html_template.replace("{{ROWS}}", rows).replace("{{TIME}}", last_updated)

# 3. Write to file
with open("index.html", "w") as f:
    f.write(final_html)

print(f"Done! Open 'index.html' in your browser.")
