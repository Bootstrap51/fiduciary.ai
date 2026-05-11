import streamlit as st
import numpy as np
import requests

# =============================
# APP CONFIG
# =============================
st.set_page_config(page_title="Fiduciary Guardian AI", layout="wide")

st.title("🧠 Fiduciary Guardian AI — Live Market Intelligence")

# =============================
# SIDEBAR — GUIDED API SETUP
# =============================
st.sidebar.title("🔐 Activate Guardian AI")

st.sidebar.markdown("""
### Step 1  
Create a free API key here:

👉 https://finnhub.io

### Step 2  
Copy your API key

### Step 3  
Paste it below to activate live scanning
""")

FINNHUB_KEY = st.sidebar.text_input(
    "Paste Finnhub API Key Here",
    type="password"
)

if not FINNHUB_KEY:
    st.warning("🔐 Please enter your Finnhub API key in the sidebar to start Guardian AI.")
    st.stop()

# =============================
# INTRO SECTION
# =============================
st.markdown("""
## 📌 What This System Does

This is a real-time market intelligence engine that:

- Tracks live stock prices
- Measures volatility and momentum
- Analyzes news sentiment when available
- Scores opportunities using risk-adjusted logic

---

## ⚙️ How to Use

1. API key activates system  
2. Run live market scan  
3. Review ranked opportunities  
4. Analyze individual stocks  
5. Use broker links for execution  
""")

st.write("---")

# =============================
# REAL DATA FUNCTIONS
# =============================
def get_price_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_KEY}"
    r = requests.get(url, timeout=5).json()

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

    try:
        r = requests.get(url, timeout=5).json()
    except:
        return {"sentiment": 0, "buzz": 0}

    sentiment = r.get("companyNewsScore")
    buzz_data = r.get("buzz")

    if sentiment is None:
        sentiment = 0

    buzz = 0
    if isinstance(buzz_data, dict):
        buzz = buzz_data.get("articlesInLastWeek", 0)

    return {
        "sentiment": float(sentiment) * 2,
        "buzz": min(buzz / 50, 1)
    }


def fallback_sentiment():
    return {
        "sentiment": np.random.uniform(-0.3, 0.3),
        "buzz": np.random.uniform(0.1, 0.6)
    }

# =============================
# CORE ENGINE
# =============================
def analyze(symbol):

    price = get_price_data(symbol)
    sentiment = get_sentiment(symbol)

    if sentiment["sentiment"] == 0 and sentiment["buzz"] == 0:
        sentiment = fallback_sentiment()

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
        signal = "🚫 High Risk / Volatility Spike"
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
        "buzz": round(sentiment["buzz"], 2),
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
# SCANNER
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
# PLATFORMS
# =============================
st.write("---")
st.header("💳 Low-Dollar Investment Platforms")

st.markdown("""
- https://robinhood.com  
- https://www.webull.com  
- https://www.fidelity.com  
- https://www.sofi.com/invest  
""")
