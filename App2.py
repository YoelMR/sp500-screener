import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

st.title("📊 S&P500 Opportunity Screener")

stocks = {
"AAPL":"Apple",
"MSFT":"Microsoft",
"NVDA":"NVIDIA",
"AMZN":"Amazon",
"META":"Meta",
"GOOGL":"Alphabet",
"TSLA":"Tesla",
"JPM":"JPMorgan",
"V":"Visa",
"XOM":"Exxon",
"UNH":"UnitedHealth",
"LLY":"Eli Lilly",
"PG":"Procter & Gamble",
"MA":"Mastercard",
"HD":"Home Depot",
"AVGO":"Broadcom",
"COST":"Costco",
"MRK":"Merck",
"ABBV":"AbbVie",
"PEP":"PepsiCo",
"KO":"Coca-Cola",
"CRM":"Salesforce",
"ADBE":"Adobe",
"NFLX":"Netflix",
"AMD":"AMD",
"INTC":"Intel",
"CSCO":"Cisco",
"WMT":"Walmart",
"BAC":"Bank of America",
"ORCL":"Oracle"
}

tickers = list(stocks.keys())

threshold = st.slider("Distance from SMA200 (%)",1.0,50.0,10.0)

data = yf.download(
    tickers,
    period="1y",
    group_by="ticker",
    progress=False
)

results = []

for ticker in tickers:

    try:

        df = data[ticker]

        close = df["Close"]

        price = close.iloc[-1]

        sma200 = close.rolling(200).mean().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]

        if pd.isna(sma200):
            continue

        dist = abs((price - sma200)/sma200*100)

        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain/avg_loss
        rsi = 100 - (100/(1+rs))

        rsi_val = rsi.iloc[-1]

        golden_cross = sma50 > sma200

        momentum = (close.iloc[-1] / close.iloc[-20] - 1) * 100

        score = (
            (50 - dist) +
            (100 - rsi_val) +
            (10 if golden_cross else 0) +
            momentum
        )

        if dist <= threshold:

            results.append({
                "Ticker":ticker,
                "Company":stocks[ticker],
                "Price":round(price,2),
                "Distance %":round(dist,2),
                "RSI":round(rsi_val,1),
                "Momentum 20d":round(momentum,2),
                "Golden Cross":golden_cross,
                "Score":round(score,2)
            })

    except:
        pass

df = pd.DataFrame(results)

df = df.sort_values("Score",ascending=False)

st.subheader("🔥 Top Opportunities")

st.dataframe(df.head(10))

st.subheader("All Candidates")

st.dataframe(df)

ticker_selected = st.selectbox("Select stock", df["Ticker"])

chart = yf.download(ticker_selected, period="1y", progress=False)

if not chart.empty and "Close" in chart.columns:

    chart["SMA200"] = chart["Close"].rolling(200).mean()
    chart["SMA50"] = chart["Close"].rolling(50).mean()

    chart_plot = chart[["Close","SMA50","SMA200"]].dropna()

    st.line_chart(chart_plot)

else:

    st.warning("No price data available for this ticker")
