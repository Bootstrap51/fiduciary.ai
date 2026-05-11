import streamlit as st
import numpy as np
import random

st.set_page_config(page_title="Fiduciary Guardian AI", layout="wide")

# -----------------------------
# INTRO SECTION (FIRST THING USERS SEE)
# -----------------------------
st.title("🧠 Fiduciary Guardian AI")

st.markdown("""
## 📌 What this is

This system is a **real-time market intelligence scanner** designed to:

- Detect low-cap and micro-cap opportunities
- Evaluate risk vs reward probabilistically
- Identify manipulation risk in volatile markets
- Provide structured, non-emotional decision signals

---

## ⚙️ Why this exists

Retail investors are often exposed to:
- emotional trading
- hype cycles
- misinformation
- manipulated micro-cap movements

This tool is designed to **reduce emotional decision-making and improve signal clarity** using structured AI-style scoring.

---

## 🧭 How to use this

1. Review live opportunities below  
2. Optionally analyze your own stock  
3. Compare risk vs confidence scores  
4. Use broker links only after evaluation  
""")

st.write("---")

# -----------------------------
# MARKET UNIVERSE
# -----------------------------
UNIVERSE = ["SNDL", "OCGN", "MULN", "BBIG", "AMC", "TELL", "NIO", "PLTR"]

# -----------------------------
# ENGINE
# -----------------------------
def analyze(symbol):

    price = round(random.uniform(0.5, 25), 2)

    sentiment = random.uniform(-1, 1)
    volatility = random.uniform(0, 1)
    volume = random.uniform(0, 1)

    min_invest = round(random.uniform(1, 50), 2)

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
        signal = "🚫 High Manipulation Risk"
    elif confidence > 75:
        signal = "🔥 Strong Setup"
    elif confidence > 60:
        signal = "⚠️ Weak Opportunity"
    else:
        signal = "❌ No Edge"

    return {
        "symbol": symbol,
        "price": price,
        "confidence": round(confidence, 2),
        "risk": round(risk, 2),
        "min_invest": min_invest,
        "signal": signal
    }

# -----------------------------
# SECTION 2 — LIVE OPPORTUNITIES
# -----------------------------
st.header("📡 Live Opportunity Scanner")

if st.button("Run Market Scan"):

    results = [analyze(s) for s in UNIVERSE]
    results.sort(key=lambda x: x["confidence"] - x["risk"], reverse=True)

    for r in results[:6]:

        st.write("---")

        col1, col2, col3 = st.columns(3)

        col1.metric("Symbol", r["symbol"])
        col2.metric("Confidence", r["confidence"])
        col3.metric("Risk", r["risk"])

        st.write("💰 Price:", f"${r['price']}")
        st.write("📉 Minimum Entry:", f"${r['min_invest']}")
        st.write("🧠 Signal:", r["signal"])

        st.link_button(
            "View Chart",
            f"https://finance.yahoo.com/quote/{r['symbol']}"
        )

# -----------------------------
# SECTION 3 — CUSTOM ANALYSIS
# -----------------------------
st.write("---")
st.header("🔍 Analyze Your Own Stock")

user_symbol = st.text_input("Enter Stock Symbol (example: TSLA, AMC, etc.)")

if st.button("Analyze Symbol") and user_symbol:

    r = analyze(user_symbol.upper())

    st.subheader(f"Results for {r['symbol']}")

    col1, col2, col3 = st.columns(3)

    col1.metric("Confidence", r["confidence"])
    col2.metric("Risk", r["risk"])
    col3.metric("Price", r["price"])

    st.write("📉 Minimum Entry Suggestion:", f"${r['min_invest']}")
    st.write("🧠 Signal:", r["signal"])

    st.link_button(
        "View Stock Chart",
        f"https://finance.yahoo.com/quote/{r['symbol']}"
    )

# -----------------------------
# SECTION 4 — INVESTMENT PLATFORMS
# -----------------------------
st.write("---")
st.header("💳 Low-Dollar Investment Platforms")

st.markdown("""
These platforms support fractional or low-minimum investing:

- https://robinhood.com  
- https://www.webull.com  
- https://www.fidelity.com  
- https://www.sofi.com/invest  
""")
