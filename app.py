import streamlit as st
import pandas as pd
import yfinance as yf

st.title("S&P500 SMA200 Screener")

# Lista de ejemplo de acciones del S&P500
tickers = [
"AAPL","MSFT","NVDA","AMZN","META","GOOGL","GOOG",
"TSLA","BRK-B","UNH","LLY","JPM","XOM","V","PG",
"COST","MA","AVGO","HD","MRK","ABBV","PEP","KO",
"ADBE","CRM","NFLX","AMD","INTC","CSCO","WMT"
]

threshold = st.slider("Distance from SMA200 (%)",1,50,3)

results = []

for ticker in tickers:
    
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
