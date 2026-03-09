import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("S&P 500 SMA200 Screener")

threshold = st.slider("Distance from SMA200 (%)", 1.0, 50.0, 5.0)

@st.cache_data
def get_sp500_tickers():

    url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"

    df = pd.read_csv(url)

    tickers = df["Symbol"].tolist()

    tickers = [t.replace(".", "-") for t in tickers]

    return tickers


@st.cache_data
def download_data(tickers):

    all_data = {}

    batch_size = 50

    for i in range(0, len(tickers), batch_size):

        batch = tickers[i:i+batch_size]

        try:

            data = yf.download(
                batch,
                period="1y",
                group_by="ticker",
                progress=False,
                threads=True
            )

            for ticker in batch:

                if ticker in data:

                    all_data[ticker] = data[ticker]

        except:
            pass

    return all_data


tickers = get_sp500_tickers()

data = download_data(tickers)

results = []

for ticker, df in data.items():

    try:

        close = df["Close"]

        if len(close) < 200:
            continue

        price = close.iloc[-1]

        sma200 = close.rolling(200).mean().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]

        dist = abs((price - sma200) / sma200 * 100)

        if dist <= threshold:

            results.append({
                "Ticker": ticker,
                "Price": round(price,2),
                "SMA50": round(sma50,2),
                "SMA200": round(sma200,2),
                "Distance %": round(dist,2)
            })

    except:
        pass


df = pd.DataFrame(results)

df = df.sort_values("Distance %")

st.write("Stocks matching filter:", len(df))

st.dataframe(df, use_container_width=True)

if not df.empty:

    ticker_selected = st.selectbox("Select stock", df["Ticker"])

    chart = yf.download(
        ticker_selected,
        period="1y",
        progress=False,
        auto_adjust=True
    )

    if not chart.empty:

        chart["SMA200"] = chart["Close"].rolling(200).mean()
        chart["SMA50"] = chart["Close"].rolling(50).mean()

        plot = chart[["Close","SMA50","SMA200"]].dropna()

        ymin = plot.min().min() * 0.98
        ymax = plot.max().max() * 1.02

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=plot.index,
            y=plot["Close"],
            name="Price"
        ))

        fig.add_trace(go.Scatter(
            x=plot.index,
            y=plot["SMA50"],
            name="SMA50"
        ))

        fig.add_trace(go.Scatter(
            x=plot.index,
            y=plot["SMA200"],
            name="SMA200"
        ))

        fig.update_layout(
            height=500,
            yaxis=dict(range=[ymin, ymax]),
            margin=dict(l=20,r=20,t=40,b=20)
        )

        st.plotly_chart(fig, use_container_width=True)
