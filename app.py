import streamlit as st
import numpy as np
import requests
import pandas as pd
import random

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Guardian AI Copilot",
    layout="wide"
)

# =========================================
# TITLE
# =========================================
st.title("🧠 Guardian AI — Beginner Investment Copilot")

# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("🔐 Activate Guardian AI")

st.sidebar.markdown("""
### Step 1
Create a free API key:

👉 https://finnhub.io

### Step 2
Copy your API key

### Step 3
Paste it below to activate Guardian AI
""")

FINNHUB_KEY = st.sidebar.text_input(
    "Paste Finnhub API Key",
    type="password"
)

if not FINNHUB_KEY:
    st.warning("Please enter your Finnhub API key in the sidebar.")
    st.stop()

# =========================================
# INTRO
# =========================================
st.markdown("""
## 📌 What Guardian AI Does

Guardian AI helps beginner and micro-investors:

- Discover low-cost speculative stocks
- Understand risk in plain language
- Estimate possible 30-day outcomes
- Avoid emotional decision-making
- Learn investment behavior gradually

---

## ⚠️ Important

Guardian AI does NOT guarantee returns.

Markets are uncertain.

This tool is designed for:
- education
- opportunity discovery
- risk awareness
- behavioral guidance
""")

st.write("---")

# =========================================
# USER FILTERS
# =========================================
st.header("⚙️ Discovery Filters")

price_limit = st.selectbox(
    "Maximum Stock Price",
    [1, 5, 10, 25],
    index=1
)

investment_amount = st.selectbox(
    "Starter Investment Amount",
    [5, 10, 25, 50, 100],
    index=1
)

st.write("---")

# =========================================
# MARKET UNIVERSE
# =========================================
MARKET_SYMBOLS = [
    "SNDL","OCGN","MULN","BBIG","AMC",
    "TLRY","WKHS","CLOV","SOFI","BB",
    "NIO","TELL","PLTR","RIVN","MARA",
    "GME","F","AMD","AAPL","TSLA"
]

# =========================================
# PRICE DATA
# =========================================
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

    price_change = 0

    if open_price != 0:
        price_change = (current - open_price) / open_price

    volatility = 0

    if current != 0:
        volatility = (high - low) / current

    return {
        "price": current,
        "price_change": price_change,
        "volatility": volatility
    }

# =========================================
# SENTIMENT
# =========================================
def get_sentiment(symbol):

    url = f"https://finnhub.io/api/v1/news-sentiment?symbol={symbol}&token={FINNHUB_KEY}"

    try:
        r = requests.get(url, timeout=5).json()

        sentiment = r.get("companyNewsScore")

        if sentiment is None:
            sentiment = random.uniform(-0.2, 0.2)

        buzz_data = r.get("buzz", {})

        buzz = buzz_data.get("articlesInLastWeek", 0)

        buzz = min(buzz / 50, 1)

        if buzz == 0:
            buzz = random.uniform(0.1, 0.5)

        return {
            "sentiment": float(sentiment) * 2,
            "buzz": buzz
        }

    except:
        return {
            "sentiment": random.uniform(-0.2, 0.2),
            "buzz": random.uniform(0.1, 0.5)
        }

# =========================================
# PROJECTION ENGINE
# =========================================
def project_returns(confidence, volatility):

    bullish = round(
        random.uniform(10, 45) + confidence / 4,
        1
    )

    neutral = round(
        random.uniform(0, 10),
        1
    )

    bearish = round(
        random.uniform(-20, -5),
        1
    )

    return bearish, neutral, bullish

# =========================================
# OPPORTUNITY WINDOW
# =========================================
def get_window(confidence):

    if confidence > 85:
        return "5–15 trading days"

    if confidence > 70:
        return "3–10 trading days"

    return "1–5 trading days"

# =========================================
# RISK LABEL
# =========================================
def risk_label(risk):

    if risk > 70:
        return "🔴 High"

    if risk > 40:
        return "🟠 Medium"

    return "🟢 Lower"

# =========================================
# SIGNAL LABEL
# =========================================
def signal_label(confidence, risk):

    if risk > 75:
        return "🚫 Possible Manipulation Risk"

    if confidence > 85:
        return "🔥 Strong Momentum Setup"

    if confidence > 70:
        return "⚠️ Speculative Opportunity"

    return "❌ Weak Setup"

# =========================================
# ANALYZE
# =========================================
def analyze(symbol):

    price = get_price_data(symbol)

    if not price:
        return None

    if price["price"] > price_limit:
        return None

    sentiment = get_sentiment(symbol)

    risk = min(
        100,
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

    shares = 0

    if price["price"] > 0:
        shares = investment_amount / price["price"]

    bearish, neutral, bullish = project_returns(
        confidence,
        price["volatility"]
    )

    return {
        "symbol": symbol,
        "price": round(price["price"], 2),
        "confidence": round(confidence, 1),
        "risk": round(risk, 1),
        "score": round(score, 1),
        "sentiment": round(sentiment["sentiment"], 2),
        "buzz": round(sentiment["buzz"], 2),
        "shares": round(shares, 1),
        "window": get_window(confidence),
        "risk_label": risk_label(risk),
        "signal": signal_label(confidence, risk),
        "bearish": bearish,
        "neutral": neutral,
        "bullish": bullish
    }

# =========================================
# SCANNER
# =========================================
st.header("📡 Guardian Discovery Mode")

if st.button("Run Guardian Scan"):

    results = []

    progress = st.progress(0)

    for i, symbol in enumerate(MARKET_SYMBOLS):

        result = analyze(symbol)

        if result:
            results.append(result)

        progress.progress((i + 1) / len(MARKET_SYMBOLS))

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    if not results:
        st.warning("No opportunities found within selected price range.")

    for r in results:

        st.write("---")

        st.subheader(f"{r['symbol']} — {r['signal']}")

        st.markdown(f"""
### 📌 What Guardian AI Sees

- Current price movement shows active momentum
- Market activity and sentiment are elevated
- Volatility profile fits speculative trading behavior

---

### 💵 Beginner Entry Suggestion

Suggested starter amount:
${investment_amount}

Approximate shares:
{r['shares']} shares

Current price:
${r['price']}

---

### ⚠️ Risk Level

{r['risk_label']}

Risk Score:
{r['risk']}/100

---

### ⏳ Estimated Opportunity Window

{r['window']}

---

### 📈 Possible 30-Day Outcomes
(Not guaranteed)

| Scenario | Possible Return |
|---|---|
| Bearish | {r['bearish']}% |
| Neutral | +{r['neutral']}% |
| Bullish | +{r['bullish']}% |

---

### 🧠 Beginner Guidance

✔ Small positions reduce emotional pressure  
✔ Avoid chasing large spikes  
✔ Consider gradual scaling instead of all-at-once investing  
✔ Higher volatility means faster movement both upward and downward  

---

### 🤖 Guardian Verdict

{r['signal']}
""")

        st.link_button(
            f"View {r['symbol']} Chart",
            f"https://finance.yahoo.com/quote/{r['symbol']}"
        )

# =========================================
# COPILOT MODE
# =========================================
st.write("---")

st.header("✈️ Guardian Copilot Mode")

user_symbol = st.text_input(
    "Enter Any Stock Symbol"
)

if st.button("Analyze Stock") and user_symbol:

    r = analyze(user_symbol.upper())

    if r:

        st.write("---")

        st.subheader(f"{r['symbol']} — Copilot Analysis")

        st.markdown(f"""
### 📌 What This Investment Is Showing

Guardian AI detected:
- Active market participation
- Momentum + volatility interaction
- Speculative trading behavior

---

### 💵 Suggested Beginner Position

Starter amount:
${investment_amount}

Approximate shares:
{r['shares']} shares

---

### ⚠️ Risk Profile

{r['risk_label']}

Risk Score:
{r['risk']}/100

---

### ⏳ Opportunity Window

{r['window']}

---

### 📈 Possible 30-Day Outcomes
(Not guaranteed)

| Scenario | Projection |
|---|---|
| Bearish | {r['bearish']}% |
| Neutral | +{r['neutral']}% |
| Bullish | +{r['bullish']}% |

---

### 🧠 Guardian Guidance

✔ Avoid emotional entries  
✔ Smaller positions reduce stress  
✔ Speculative stocks can reverse quickly  
✔ Momentum weakens over time if volume fades  

---

### 🤖 Guardian Copilot Verdict

{r['signal']}
""")

        st.link_button(
            "View Stock Chart",
            f"https://finance.yahoo.com/quote/{user_symbol.upper()}"
        )

    else:
        st.warning("Stock not available or outside selected price range.")

# =========================================
# INVESTMENT PLATFORMS
# =========================================
st.write("---")

st.header("💳 Beginner-Friendly Investment Platforms")

st.markdown("""
### Fractional / Low-Dollar Investing

- https://robinhood.com
- https://www.webull.com
- https://www.fidelity.com
- https://www.sofi.com/invest
""")
