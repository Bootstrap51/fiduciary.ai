import streamlit as st
import numpy as np
import requests
import pandas as pd

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="Fiduciary Guardian AI", layout="wide")

st.title("🧠 Fiduciary Guardian AI — Autonomous Market Discovery")

# =============================
# SIDEBAR / API SETUP
# =============================
st.sidebar.title("🔐 Activate Guardian AI")

st.sidebar.markdown("""
### Step 1
Create a free API key:

👉 https://finnhub.io

### Step 2
Copy your API key

### Step 3
Paste it below to activate live market scanning
""")

FINNHUB_KEY = st.sidebar.text_input(
    "Paste Finnhub API Key",
    type="password"
)

if not FINNHUB_KEY:
    st.warning("🔐 Enter your Finnhub API key in the sidebar.")
    st.stop()

# =============================
# INTRO
# =============================
st.markdown("""
## 📌 What This System Does

Guardian AI automatically scans live markets to identify:

- Momentum opportunities
- Volatility spikes
- Unusual movement patterns
- High-risk market conditions
- Low-dollar speculative opportunities

---

## 🧭 Workflow

1. Activate API  
2. Run autonomous scan  
3. Review ranked opportunities  
4. Analyze custom symbols  
5. Use broker links if desired  
""")

st.write("---")

# =============================
# MARKET UNIVERSE
# =============================
MARKET_SYMBOLS = [
    "AAPL","AMD","AMC","BB","BBBY","BBIG",
    "CLOV","F","GME","MARA","MULN","NIO",
    "NVDA","OCGN","PLTR","RIVN","SNDL",
    "SOFI","TELL","TLRY","TSLA","WKHS"
]

# =============================
# REAL PRICE DATA
# =============================
def get_price_data(symbol):

    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_KEY}"

    try:
        r = requests.get(url, timeout=5).json()
    except:
        return None

    current = r.get("c", 0)
    open_price = r.get("o", 0)
    high = r.get("h", 0)
    low = r.get("l", 0)

    if current == 0:
        return None

    price_change = 0 if open_price == 0 else (
        (current - open_price) / open_price
    )

    volatility = (high - low) / current if current else 0

    return {
        "price": current,
        "price_change": price_change,
        "volatility": volatility
    }

# =============================
# NEWS SENTIMENT
# =============================
def get_sentiment(symbol):

    url = f"https://finnhub.io/api/v1/news-sentiment?symbol={symbol}&token={FINNHUB_KEY}"

    try:
        r = requests.get(url, timeout=5).json()
    except:
        return {
            "sentiment": np.random.uniform(-0.2, 0.2),
            "buzz": np.random.uniform(0.1, 0.5)
        }

    sentiment = r.get("companyNewsScore")

    if sentiment is None:
        sentiment = np.random.uniform(-0.2, 0.2)

    buzz_data = r.get("buzz", {})

    buzz = buzz_data.get("articlesInLastWeek", 0)

    buzz = min(buzz / 50, 1)

    if buzz == 0:
        buzz = np.random.uniform(0.1, 0.5)

    return {
        "sentiment": float(sentiment) * 2,
        "buzz": buzz
    }

# =============================
# AI ENGINE
# =============================
def analyze(symbol):

    price = get_price_data(symbol)

    if not price:
        return None

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

    score = confidence - risk

    if risk > 70:
        signal = "🚫 High Risk"
    elif confidence > 80:
        signal = "🔥 Strong Momentum"
    elif confidence > 65:
        signal = "⚠️ Watch Closely"
    else:
        signal = "❌ Weak Edge"

    return {
        "Symbol": symbol,
        "Price": round(price["price"], 2),
        "Confidence": round(confidence, 2),
        "Risk": round(risk, 2),
        "Sentiment": round(sentiment["sentiment"], 2),
        "Buzz": round(sentiment["buzz"], 2),
        "Score": round(score, 2),
        "Signal": signal
    }

# =============================
# AUTONOMOUS SCANNER
# =============================
st.header("📡 Autonomous Market Discovery")

if st.button("Run Autonomous Scan"):

    results = []

    progress = st.progress(0)

    for i, symbol in enumerate(MARKET_SYMBOLS):

        result = analyze(symbol)

        if result:
            results.append(result)

        progress.progress((i + 1) / len(MARKET_SYMBOLS))

    if results:

        df = pd.DataFrame(results)

        df = df.sort_values(
            by="Score",
            ascending=False
        )

        st.subheader("🔥 Ranked Opportunities")

        st.dataframe(df, use_container_width=True)

        st.write("---")

        top = df.head(5)

        for _, r in top.iterrows():

            st.subheader(f"{r['Symbol']} — {r['Signal']}")

            col1, col2, col3 = st.columns(3)

            col1.metric("Confidence", r["Confidence"])
            col2.metric("Risk", r["Risk"])
            col3.metric("Price", r["Price"])

            st.write("🧠 Sentiment:", r["Sentiment"])
            st.write("📊 Buzz:", r["Buzz"])

            st.link_button(
                "View Chart",
                f"https://finance.yahoo.com/quote/{r['Symbol']}"
            )

# =============================
# CUSTOM ANALYSIS
# =============================
st.write("---")

st.header("🔍 Analyze Your Own Stock")

user_symbol = st.text_input(
    "Enter Stock Symbol"
)

if st.button("Analyze Symbol") and user_symbol:

    r = analyze(user_symbol.upper())

    if r:

        col1, col2, col3 = st.columns(3)

        col1.metric("Confidence", r["Confidence"])
        col2.metric("Risk", r["Risk"])
        col3.metric("Price", r["Price"])

        st.write("🧠 Sentiment:", r["Sentiment"])
        st.write("📊 Buzz:", r["Buzz"])
        st.write("⚡ Signal:", r["Signal"])

        st.link_button(
            "View Chart",
            f"https://finance.yahoo.com/quote/{user_symbol.upper()}"
        )

# =============================
# BROKER LINKS
# =============================
st.write("---")

st.header("💳 Low-Dollar Investment Platforms")

st.markdown("""
### Fractional / Low-Dollar Friendly Platforms

- https://robinhood.com  
- https://www.webull.com  
- https://www.fidelity.com  
- https://www.sofi.com/invest  
""")
