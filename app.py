import streamlit as st
import pandas as pd
import yfinance as yf

st.title("S&P500 SMA200 Screener")

@st.cache_data
def get_sp500():
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    return table[0]["Symbol"].tolist()

tickers = get_sp500()

threshold = st.slider("Distance from SMA200 (%)",1,10,3)

results = []

for ticker in tickers[:150]:   # limitado para que cargue rápido en cloud
    try:
        data = yf.download(ticker, period="1y", progress=False)

        data["SMA200"] = data["Close"].rolling(200).mean()

        price = data["Close"].iloc[-1]
        sma200 = data["SMA200"].iloc[-1]

        dist = (price - sma200) / sma200 * 100

        if abs(dist) < threshold:
            results.append({
                "Ticker": ticker,
                "Price": round(price,2),
                "SMA200": round(sma200,2),
                "Distance %": round(dist,2)
            })
    except:
        pass

df = pd.DataFrame(results)

st.dataframe(df)
