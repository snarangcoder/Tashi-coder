
import streamlit as st
import pandas as pd
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

API_KEY = st.secrets["API_KEY"]
API_SECRET = st.secrets["API_SECRET"]
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL)

MAX_TICKERS = 50
MIN_VOLUME = 100000
MIN_PRICE = 1.0

def get_ticker_data(symbol):
    try:
        bars = api.get_bars(symbol, tradeapi.TimeFrame.Minute, limit=20).df
        if bars.empty:
            return None

        sma20 = bars['close'].mean()
        latest_price = bars['close'].iloc[-1]
        vwap = (bars['high'].iloc[-1] + bars['low'].iloc[-1] + bars['close'].iloc[-1]) / 3
        volume = bars['volume'].sum()

        return {
            'symbol': symbol,
            'price': latest_price,
            'sma20': sma20,
            'vwap': vwap,
            'volume': volume,
            'pattern': detect_simple_pattern(bars)
        }
    except:
        return None

def detect_simple_pattern(df):
    closes = df['close'].tolist()
    if len(closes) < 5:
        return ""
    if closes[-1] < closes[-2] and closes[-2] > closes[-3]:
        return "Possible Double Top"
    if closes[-1] > closes[-2] and closes[-2] < closes[-3]:
        return "Possible Inverse Head & Shoulders"
    return ""

st.set_page_config(page_title="AI Trading Assistant", layout="centered")
st.title("🚀 AI Trading Assistant")
st.markdown("This assistant scans top tickers using your 20-SMA + VWAP strategy, and identifies possible chart patterns.")

st.subheader("Momentum Picks")
tickers = ['AAPL', 'NVDA', 'GOOG', 'TSLA', 'AMZN', 'BABA', 'ORCL', 'VTI', 'AVGO', 'VYM', 'VT', 'SHY', 'SCHD']
results = []

for symbol in tickers:
    data = get_ticker_data(symbol)
    if data and data['price'] > data['sma20'] and data['price'] > data['vwap'] and data['volume'] > MIN_VOLUME:
        results.append(data)

top_results = sorted(results, key=lambda x: x['volume'], reverse=True)[:3]

if top_results:
    df = pd.DataFrame(top_results)
    st.dataframe(df[['symbol', 'price', 'sma20', 'vwap', 'volume', 'pattern']])
else:
    st.info("No qualifying momentum tickers found today.")

st.subheader("Core Watchlist")
core_data = []
for symbol in tickers:
    data = get_ticker_data(symbol)
    if data:
        core_data.append(data)

core_df = pd.DataFrame(core_data)
st.dataframe(core_df[['symbol', 'price', 'sma20', 'vwap', 'volume', 'pattern']])
