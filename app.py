import streamlit as st
import numpy as np
import random
import webbrowser

st.set_page_config(page_title="Fiduciary AI Scanner", layout="wide")

st.title("🧠 Fiduciary Guardian AI — Live Micro-Cap Scanner")

# -----------------------------
# SIMULATED REAL-TIME UNIVERSE
# (replace later with real API like Finnhub/Polygon)
# -----------------------------
UNIVERSE = [
    "SNDL", "OCGN", "MULN", "BBIG", "AMC",
    "TELL", "NIO", "PLTR", "SOFI", "RIG"
]

# -----------------------------
# ENGINE
# -----------------------------
def analyze(symbol):
    price = round(random.uniform(0.2, 25), 2)

    volume = random.uniform(0, 1)
    sentiment = random.uniform(-1, 1)
    volatility = random.uniform(0, 1)

    min_invest = round(random.uniform(1, 100), 2)

    risk = min(100,
        abs(sentiment) * 40 +
        volatility * 60 +
        (1 - volume) * 20
    )

    confidence = (
        sentiment * 50 +
        volume * 60 -
        volatility * 30
    ) + 60

    confidence = max(0, min(100, confidence))

    if risk > 70:
        signal = "🚫 HIGH RISK / MANIPULATION ZONE"
    elif confidence > 75:
        signal = "🔥 STRONG SETUP"
    elif confidence > 60:
        signal = "⚠️ WEAK BUT WATCH"
    else:
        signal = "❌ NO EDGE"

    return {
        "symbol": symbol,
        "price": price,
        "confidence": round(confidence, 2),
        "risk": round(risk, 2),
        "min_invest": min_invest,
        "signal": signal
    }

# -----------------------------
# BROKER LINKS (LOW DOLLAR FRIENDLY)
# -----------------------------
BROKERS = {
    "Robinhood": "https://robinhood.com",
    "Webull": "https://www.webull.com",
    "Fidelity": "https://www.fidelity.com",
    "SoFi Invest": "https://www.sofi.com/invest",
}

# -----------------------------
# SCAN BUTTON
# -----------------------------
if st.button("Run Live Market Scan"):

    results = [analyze(s) for s in UNIVERSE]
    results.sort(key=lambda x: x["confidence"] - x["risk"], reverse=True)

    st.subheader("📡 Top Micro-Cap Opportunities")

    for r in results[:6]:

        st.write("---")

        col1, col2, col3 = st.columns(3)

        col1.metric("Symbol", r["symbol"])
        col2.metric("Confidence", r["confidence"])
        col3.metric("Risk", r["risk"])

        st.write("💰 Price:", f"${r['price']}")
        st.write("📉 Minimum Suggested Entry:", f"${r['min_invest']}")
        st.write("🧠 Signal:", r["signal"])

        # Stock chart link (simple public lookup)
        st.link_button(
            "View Chart",
            f"https://finance.yahoo.com/quote/{r['symbol']}"
        )

    st.subheader("💳 Low-Dollar Investment Platforms")

    for name, url in BROKERS.items():
        st.link_button(name, url)
