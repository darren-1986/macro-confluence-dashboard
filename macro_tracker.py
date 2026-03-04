import csv
from collections import defaultdict
from datetime import datetime, timezone

# -----------------------------
# STATUS → COLOR MAP
# -----------------------------
def status_class(status: str) -> str:
    s = status.lower()

    bullish_keywords = [
        "bull", "rising", "expansion", "easing", "cooling", "improving"
    ]

    bearish_keywords = [
        "bear", "falling", "inverted", "restrictive", "contraction",
        "sticky", "elevated", "above target", "widening", "tightening",
        "high", "stress"
    ]

    if any(k in s for k in bullish_keywords):
        return "bull"
    if any(k in s for k in bearish_keywords):
        return "bear"

    return "neutral"

def category_bias(items):
    """
    Returns 'bear', 'bull', or 'neutral' for a category
    based on majority of item classes.
    """
    counts = {"bear": 0, "bull": 0, "neutral": 0}
    for item in items:
        counts[item["class"]] += 1

    if counts["bear"] >= 2:
        return "bear"
    if counts["bull"] >= 2:
        return "bull"
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
# MACRO REGIME
# -----------------------------
rates_bias = category_bias(data.get("Rates", []))
inflation_bias = category_bias(data.get("Inflation", []))
risk_bias = category_bias(data.get("Risk Sentiment", []))

# -----------------------------
# DETERMINE MACRO REGIME
# -----------------------------
if risk_bias == "bull" and rates_bias != "bear":
    macro_regime = "RISK-ON"
    regime_class = "bull"
elif risk_bias == "bear" or rates_bias == "bear":
    macro_regime = "RISK-OFF"
    regime_class = "bear"
else:
    macro_regime = "TRANSITION"
    regime_class = "neutral"

bearish_count = [rates_bias, inflation_bias, risk_bias].count("bear")

if bearish_count >= 2:
    macro_regime = "RISK-OFF"
    regime_class = "bear"
elif bearish_count == 1:
    macro_regime = "TRANSITION"
    regime_class = "neutral"
else:
    macro_regime = "RISK-ON"
    regime_class = "bull"

# -----------------------------
# AUTO-DERIVED ASSET BIAS
# -----------------------------

# GOLD
if macro_regime == "RISK-OFF" and (inflation_bias == "bear" or rates_bias == "bear"):
    gold_bias = "Bullish"
    gold_class = "bull"
elif macro_regime == "RISK-ON":
    gold_bias = "Bearish"
    gold_class = "bear"
else:
    gold_bias = "Neutral"
    gold_class = "neutral"

# AUD/USD
growth_bias = category_bias(data.get("Growth", []))

if macro_regime == "RISK-OFF" and risk_bias == "bear" and growth_bias == "bear":
    aud_bias = "Bearish"
    aud_class = "bear"
elif macro_regime == "RISK-ON" and growth_bias == "bull":
    aud_bias = "Bullish"
    aud_class = "bull"
else:
    aud_bias = "Neutral"
    aud_class = "neutral"

# -----------------------------
# AUTO-DERIVED ASSETS
# -----------------------------

# GOLD
if macro_regime == "RISK-OFF" and rates_bias == "bear":
    gold_bias = "Bullish"
    gold_class = "bull"
elif macro_regime == "RISK-ON":
    gold_bias = "Bearish"
    gold_class = "bear"
else:
    gold_bias = "Neutral"
    gold_class = "neutral"

# AUD/USD
if macro_regime == "RISK-OFF" and growth_bias == "bear":
    aud_bias = "Bearish"
    aud_class = "bear"
elif macro_regime == "RISK-ON" and growth_bias == "bull":
    aud_bias = "Bullish"
    aud_class = "bull"
else:
    aud_bias = "Neutral"
    aud_class = "neutral"

# -----------------------------
# TIMESTAMP
# -----------------------------
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# -----------------------------
# CATEGORY BIAS
# -----------------------------
rates_bias = category_bias(data.get("Rates", []))
inflation_bias = category_bias(data.get("Inflation", []))
risk_bias = category_bias(data.get("Risk Sentiment", []))
growth_bias = category_bias(data.get("Growth", []))

# -----------------------------
# MACRO REGIME
# -----------------------------
if risk_bias == "bear" or rates_bias == "bear":
    macro_regime = "RISK-OFF"
    regime_class = "bear"
elif risk_bias == "bull" and growth_bias == "bull":
    macro_regime = "RISK-ON"
    regime_class = "bull"
else:
    macro_regime = "TRANSITION"
    regime_class = "neutral"

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

<div class="card">
    <h2>Macro Regime</h2>
    <p class="{regime_class}" style="font-size: 1.6rem;">
        {macro_regime}
    </p>
</div>

{sections_html}

<div class="card">
    <h2>Assets (Auto-Derived)</h2>
    <table>
        <tr>
            <td>Gold</td>
            <td class="{gold_class}">{gold_bias}</td>
        </tr>
        <tr>
            <td>AUD/USD</td>
            <td class="{aud_class}">{aud_bias}</td>
        </tr>
    </table>
</div>

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
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated with color coding")
