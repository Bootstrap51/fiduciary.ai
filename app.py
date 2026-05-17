import streamlit as st
import requests
import pandas as pd
import yfinance as yf
import random

# =========================================
# PAGE
# =========================================
st.set_page_config(
    page_title="Guardian AI",
    layout="wide"
)

st.title("🧠 Guardian AI — Micro Investor Discovery")

# =========================================
# INTRO
# =========================================
st.markdown("""
## 📌 What Guardian AI Does

Guardian AI helps beginner investors discover:

- Low-cost stocks
- Active penny stock momentum
- Cheap speculative opportunities
- Beginner-friendly small-position ideas

---

## ⚠️ Important

This tool does NOT guarantee returns.

Penny stocks are highly speculative and risky.

Guardian AI is designed to:
- simplify research
- reduce confusion
- help beginners understand opportunities
""")

st.write("---")

# =========================================
# FILTERS
# =========================================
st.header("⚙️ Discovery Settings")

max_price = st.selectbox(
    "Maximum Stock Price",
    [1, 2, 5],
    index=0
)

investment_amount = st.selectbox(
    "How Much Are You Experimenting With?",
    [1, 2, 5],
    index=2
)

st.write("---")

# =========================================
# STOCK LIST
# =========================================
PENNY_STOCKS = [
    "SNDL",
    "MULN",
    "OCGN",
    "TELL",
    "WKHS",
    "CLOV",
    "BBIG",
    "ATER",
    "CEI",
    "NAKD",
    "IDEX",
    "XELA",
    "GNUS",
    "CTRM",
    "HUSA",
    "TOPS",
    "ZOM",
    "SOS",
    "BIOR",
    "COSM"
]

# =========================================
# GET STOCK DATA
# =========================================
def get_stock_data(symbol):

    try:

        stock = yf.Ticker(symbol)

        hist = stock.history(period="5d")

        if hist.empty:
            return None

        current_price = round(hist["Close"].iloc[-1], 2)

        volume_today = hist["Volume"].iloc[-1]

        avg_volume = hist["Volume"].mean()

        momentum = (
            hist["Close"].iloc[-1] -
            hist["Close"].iloc[0]
        )

        return {
            "symbol": symbol,
            "price": current_price,
            "volume_today": volume_today,
            "avg_volume": avg_volume,
            "momentum": momentum
        }

    except:
        return None

# =========================================
# SIMPLE ANALYSIS
# =========================================
def analyze_stock(data):

    if not data:
        return None

    if data["price"] > max_price:
        return None

    shares = int(investment_amount / data["price"])

    volume_spike = data["volume_today"] > data["avg_volume"]

    momentum_up = data["momentum"] > 0

    # SIMPLE SCORE
    score = 0

    if volume_spike:
        score += 1

    if momentum_up:
        score += 1

    # SIMPLE LABELS
    if score == 2:
        setup = "🔥 Active Momentum"

    elif score == 1:
        setup = "⚠️ Moderate Activity"

    else:
        setup = "❌ Weak Activity"

    # RISK
    if data["price"] < 0.50:
        risk = "🔴 Very High"

    elif data["price"] < 2:
        risk = "🟠 High"

    else:
        risk = "🟡 Speculative"

    # MOMENTUM WINDOW
    if score == 2:
        window = "1–5 days"

    elif score == 1:
        window = "1–3 days"

    else:
        window = "Weak momentum"

    # SIMPLE OUTLOOK
    if score == 2:
        outlook = random.choice([
            "Possible strong move",
            "Momentum building",
            "Retail attention increasing"
        ])

    elif score == 1:
        outlook = random.choice([
            "Watch carefully",
            "Moderate speculative activity",
            "Some momentum present"
        ])

    else:
        outlook = random.choice([
            "Low momentum",
            "Weak setup currently",
            "Limited activity"
        ])

    return {
        "symbol": data["symbol"],
        "price": data["price"],
        "shares": shares,
        "setup": setup,
        "risk": risk,
        "window": window,
        "outlook": outlook,
        "volume_spike": volume_spike,
        "momentum_up": momentum_up,
    }

# =========================================
# SCAN BUTTON
# =========================================
st.header("📡 Guardian Discovery")

if st.button("Find Opportunities"):

    opportunities = []

    progress = st.progress(0)

    for i, symbol in enumerate(PENNY_STOCKS):

        stock_data = get_stock_data(symbol)

        result = analyze_stock(stock_data)

        if result:
            opportunities.append(result)

        progress.progress((i + 1) / len(PENNY_STOCKS))

    # SORT
    opportunities.sort(
        key=lambda x: (
            x["volume_spike"],
            x["momentum_up"]
        ),
        reverse=True
    )

    if not opportunities:
        st.warning("No active opportunities found.")

    # DISPLAY
    for stock in opportunities[:10]:

        st.write("---")

        st.subheader(
            f"{stock['symbol']} — {stock['setup']}"
        )

        st.markdown(f"""
### 💵 Price
${stock['price']} per share

### 💸 Your ${investment_amount}
Approximate shares:
{stock['shares']}

### 📈 Why Guardian Flagged It
""")

        if stock["volume_spike"]:
            st.write("✔ Trading volume is increasing")

        if stock["momentum_up"]:
            st.write("✔ Price momentum is moving upward")

        if not stock["volume_spike"] and not stock["momentum_up"]:
            st.write("• Limited activity currently")

        st.markdown(f"""
### ⚠️ Risk
{stock['risk']}

### ⏳ Momentum Window
{stock['window']}

### 🤖 Guardian Opinion
{stock['outlook']}
""")

        st.link_button(
            f"View {stock['symbol']} Chart",
            f"https://finance.yahoo.com/quote/{stock['symbol']}"
        )

# =========================================
# CUSTOM STOCK CHECK
# =========================================
st.write("---")

st.header("✈️ Check Your Own Stock")

custom_symbol = st.text_input(
    "Enter Stock Symbol"
)

if st.button("Analyze Stock"):

    if custom_symbol:

        stock_data = get_stock_data(
            custom_symbol.upper()
        )

        result = analyze_stock(stock_data)

        if result:

            st.write("---")

            st.subheader(
                f"{result['symbol']} — {result['setup']}"
            )

            st.markdown(f"""
### 💵 Price
${result['price']} per share

### 💸 Your ${investment_amount}
Approximate shares:
{result['shares']}

### ⚠️ Risk
{result['risk']}

### ⏳ Momentum Window
{result['window']}

### 🤖 Guardian Opinion
{result['outlook']}
""")

            st.link_button(
                "View Chart",
                f"https://finance.yahoo.com/quote/{result['symbol']}"
            )

        else:
            st.warning(
                "Stock unavailable or above selected price limit."
            )

# =========================================
# BROKER LINKS
# =========================================
st.write("---")

st.header("💳 Beginner Investment Platforms")

st.markdown("""
- https://robinhood.com  
- https://www.webull.com  
- https://www.sofi.com/invest  
- https://www.fidelity.com  
""")
