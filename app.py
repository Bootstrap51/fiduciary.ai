import streamlit as st
import numpy as np
import requests

# =============================
# APP CONFIG
# =============================
st.set_page_config(page_title="Fiduciary Guardian AI", layout="wide")

st.title("🧠 Fiduciary Guardian AI — Live Market Intelligence")

# =============================
# API INPUT (USER PROVIDED)
# =============================
st.sidebar.title("🔐 Setup")

FINNHUB_KEY = st.sidebar.text_input(
    "Enter Finnhub API Key",
    type="password"
)

if not FINNHUB_KEY:
    st.warning("Enter your Finnhub API key in the sidebar to activate live market data.")
    st.stop()

# =============================
# INTRO SECTION
# =============================
st.markdown("""
## 📌 System Overview

This tool analyzes live financial markets using:

- Real-time stock pricing
- News sentiment scoring
- Volatility + momentum modeling
- Risk-adjusted opportunity ranking

---

## 🧭 How to use

1. Run live scanner  
2. Review ranked opportunities  
3. Analyze any stock manually  
4. Use broker links if desired  
""")

st.write("---")

# =============================
# REAL DATA FUNCTIONS
# =============================
def get_price_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_KEY}"
    r = requests.get(url).json()

    current = r.get("c", 0)
    open_price = r.get("o", 0)
    high = r.get("h", 0)
    low = r.get("l", 0)

    price_change = 0 if open_price == 0 else (current - open_price) / open_price
    volatility = 0 if current == 0 else (high - low) / current

    return {
        "price": current,
        "price_change": price_change,
        "volatility": volatility
    }


def get_sentiment(symbol):
    url = f"https://finnhub.io/api/v1/news-sentiment?symbol={symbol}&token={FINNHUB_KEY}"
    r = requests.get(url).json()

    sentiment = r.get("companyNewsScore", 0)
    buzz = r.get("buzz", {}).get("articlesInLastWeek", 0)

    return {
        "sentiment": sentiment * 2,
        "buzz": min(buzz / 50, 1)
    }

# =============================
# CORE ENGINE
# =============================
def analyze(symbol):

    price = get_price_data(symbol)
    sentiment = get_sentiment(symbol)

    risk = min(100,
        abs(sentiment["sentiment"]) * 40 +
        price["volatility"] * 180 +
        (1 - sentiment["buzz"]) * 30
    )

    confidence = (
        price["price_change"] * 120 +
        sentiment["sentiment"] * 60 +
        sentiment["buzz"] * 50
    ) + 60

    confidence = max(0, min(100, confidence))

    if risk > 70:
        signal = "🚫 High Risk / Possible Manipulation"
    elif confidence > 75:
        signal = "🔥 Strong Opportunity"
    elif confidence > 60:
        signal = "⚠️ Watch Closely"
    else:
        signal = "❌ No Clear Edge"

    return {
        "symbol": symbol,
        "price": price["price"],
        "confidence": round(confidence, 2),
        "risk": round(risk, 2),
        "sentiment": round(sentiment["sentiment"], 2),
        "buzz": sentiment["buzz"],
        "signal": signal
    }

# =============================
# WATCHLIST
# =============================
WATCHLIST = [
    "SNDL", "OCGN", "MULN", "BBIG",
    "AMC", "TELL", "NIO", "PLTR"
]

# =============================
# LIVE SCANNER
# =============================
st.header("📡 Live Market Scanner")

if st.button("Run Scan"):

    results = [analyze(s) for s in WATCHLIST]
    results.sort(key=lambda x: x["confidence"] - x["risk"], reverse=True)

    for r in results:

        st.write("---")

        col1, col2, col3 = st.columns(3)

        col1.metric("Symbol", r["symbol"])
        col2.metric("Confidence", r["confidence"])
        col3.metric("Risk", r["risk"])

        st.write("💰 Price:", f"${r['price']}")
        st.write("🧠 Sentiment:", r["sentiment"])
        st.write("📊 Buzz:", r["buzz"])
        st.write("⚡ Signal:", r["signal"])

        st.link_button(
            "View Chart",
            f"https://finance.yahoo.com/quote/{r['symbol']}"
        )

# =============================
# CUSTOM ANALYSIS
# =============================
st.write("---")
st.header("🔍 Analyze Any Stock")

user_symbol = st.text_input("Enter Symbol (e.g. TSLA, AMC)")

if st.button("Analyze") and user_symbol:

    r = analyze(user_symbol.upper())

    st.subheader(f"{r['symbol']} Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric("Confidence", r["confidence"])
    col2.metric("Risk", r["risk"])
    col3.metric("Price", r["price"])

    st.write("🧠 Sentiment:", r["sentiment"])
    st.write("📊 Buzz:", r["buzz"])
    st.write("⚡ Signal:", r["signal"])

    st.link_button(
        "View Chart",
        f"https://finance.yahoo.com/quote/{r['symbol']}"
    )

# =============================
# BROKER LINKS
# =============================
st.write("---")
st.header("💳 Low-Dollar Investment Platforms")

st.markdown("""
- https://robinhood.com  
- https://www.webull.com  
- https://www.fidelity.com  
- https://www.sofi.com/invest  
""")
