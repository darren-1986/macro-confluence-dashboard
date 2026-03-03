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

    # 🔴 FORCE FLAT COLUMNS (CRITICAL)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

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
