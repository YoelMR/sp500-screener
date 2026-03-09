import streamlit as st
import pandas as pd
import yfinance as yf

st.title("S&P500 SMA200 Screener")

tickers = [
"AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","JPM",
"V","XOM","UNH","LLY","PG","MA","HD","AVGO","COST",
"MRK","ABBV","PEP","KO","CRM","ADBE","NFLX","AMD",
"INTC","CSCO","WMT","BAC","TMO","ORCL"
]

threshold = st.slider("Distance from SMA200 (%)", 1.0, 50.0, 10.0)

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

        df["SMA200"] = df["Close"].rolling(200).mean()

        price = df["Close"].iloc[-1]
        sma200 = df["SMA200"].iloc[-1]

        if pd.isna(sma200):
            continue

        dist = (price - sma200) / sma200 * 100

        results.append({
            "Ticker": ticker,
            "Price": round(price,2),
            "SMA200": round(sma200,2),
            "Distance %": round(dist,2)
        })

    except:
        pass

df = pd.DataFrame(results)

st.write("Stocks scanned:", len(results))

st.dataframe(df.sort_values("Distance %"))
