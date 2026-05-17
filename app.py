import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import random

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Guardian AI",
    layout="wide"
)

st.title("🧠 Guardian AI — Real Penny Stock Discovery")

# =========================================
# INTRO
# =========================================
st.markdown("""
## 📌 What Guardian AI Does

Guardian AI scans live markets looking for:

- Cheap penny stocks
- Active low-cost opportunities
- Increased trading activity
- Beginner-friendly speculative setups

---

## ⚠️ Important

Penny stocks are extremely risky and volatile.

This tool is designed to:
- simplify discovery
- reduce information overload
- help beginners experiment carefully
""")

st.write("---")

# =========================================
# FILTERS
# =========================================
st.header("⚙️ Discovery Settings")

price_range = st.selectbox(
    "Choose Penny Stock Price Range",
    [
        "$0.01 - $1.00",
        "$1.00 - $3.00",
        "$3.00 - $5.00"
    ]
)

if price_range == "$0.01 - $1.00":
    min_price = 0.01
    max_price = 1.00

elif price_range == "$1.00 - $3.00":
    min_price = 1.00
    max_price = 3.00

else:
    min_price = 3.00
    max_price = 5.00

investment_amount = st.selectbox(
    "How Much Are You Experimenting With?",
    [1, 2, 5],
    index=2
)

st.write("---")

# =========================================
# GET LIVE MARKET MOVERS
# =========================================
def get_market_movers():

    url = "https://finance.yahoo.com/markets/stocks/gainers/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        tables = pd.read_html(
            requests.get(
                url,
                headers=headers,
                timeout=10
            ).text
        )

        if len(tables) == 0:
            return []

        df = tables[0]

        symbols = []

        for symbol in df["Symbol"]:

            if isinstance(symbol, str):

                # remove weird symbols
                if "." not in symbol:
                    symbols.append(symbol)

        return symbols[:50]

    except:
        return []

# =========================================
# GET STOCK DATA
# =========================================
def get_stock_data(symbol):

    try:

        stock = yf.Ticker(symbol)

        hist = stock.history(period="5d")

        if hist.empty:
            return None

        current_price = round(
            hist["Close"].iloc[-1],
            2
        )

        # PRICE FILTER
        if current_price < min_price:
            return None

        if current_price > max_price:
            return None

        volume_today = hist["Volume"].iloc[-1]

        avg_volume = hist["Volume"].mean()

        # remove dead stocks
        if volume_today < 50000:
            return None

        momentum = (
            hist["Close"].iloc[-1]
            -
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
# ANALYSIS ENGINE
# =========================================
def analyze_stock(data):

    if not data:
        return None

    shares = int(
        investment_amount / data["price"]
    )

    volume_spike = (
        data["volume_today"]
        >
        data["avg_volume"]
    )

    momentum_up = (
        data["momentum"] > 0
    )

    # SCORE
    score = 0

    if volume_spike:
        score += 1

    if momentum_up:
        score += 1

    # LABELS
    if score == 2:
        setup = "🔥 Active Momentum"

    elif score == 1:
        setup = "⚠️ Moderate Activity"

    else:
        setup = "❌ Weak Activity"

    # RISK
    if data["price"] < 0.50:
        risk = "🔴 Very High Risk"

    elif data["price"] < 2:
        risk = "🟠 High Risk"

    else:
        risk = "🟡 Speculative"

    # WINDOW
    if score == 2:
        window = "1–5 days"

    elif score == 1:
        window = "1–3 days"

    else:
        window = "Weak momentum"

    # HUMAN LANGUAGE
    reasons = []

    if volume_spike:
        reasons.append(
            "Trading activity increased today"
        )

    if momentum_up:
        reasons.append(
            "Price momentum is moving upward"
        )

    if not reasons:
        reasons.append(
            "Limited activity currently"
        )

    # OPINION
    if score == 2:

        opinion = random.choice([
            "Interesting speculative momentum setup",
            "Momentum appears stronger than normal",
            "Retail trading activity is elevated"
        ])

    elif score == 1:

        opinion = random.choice([
            "Worth watching carefully",
            "Moderate speculative activity detected",
            "Some momentum appears active"
        ])

    else:

        opinion = random.choice([
            "Weak setup currently",
            "Low momentum detected",
            "Not much activity right now"
        ])

    return {
        "symbol": data["symbol"],
        "price": data["price"],
        "shares": shares,
        "setup": setup,
        "risk": risk,
        "window": window,
        "opinion": opinion,
        "reasons": reasons,
        "score": score
    }

# =========================================
# DISCOVERY MODE
# =========================================
st.header("📡 Live Market Discovery")

if st.button("Scan Live Penny Stocks"):

    with st.spinner("Scanning live markets..."):

        symbols = get_market_movers()

        if not symbols:

            st.error(
                "Unable to retrieve live market movers."
            )

        else:

            opportunities = []

            progress = st.progress(0)

            for i, symbol in enumerate(symbols):

                stock_data = get_stock_data(symbol)

                result = analyze_stock(stock_data)

                if result:
                    opportunities.append(result)

                progress.progress(
                    (i + 1) / len(symbols)
                )

            opportunities.sort(
                key=lambda x: x["score"],
                reverse=True
            )

            if not opportunities:

                st.warning(
                    "No active penny stock opportunities found in this price range."
                )

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

### ⚠️ Risk
{stock['risk']}

### ⏳ Momentum Window
{stock['window']}

### 🤖 Guardian Opinion
{stock['opinion']}
""")

                st.markdown(
                    "### 📈 Why Guardian Flagged It"
                )

                for reason in stock["reasons"]:
                    st.write(f"✔ {reason}")

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
{result['opinion']}
""")

            st.markdown(
                "### 📈 Why Guardian Flagged It"
            )

            for reason in result["reasons"]:
                st.write(f"✔ {reason}")

            st.link_button(
                "View Stock Chart",
                f"https://finance.yahoo.com/quote/{custom_symbol.upper()}"
            )

        else:

            st.warning(
                "Stock unavailable, inactive, or outside selected price range."
            )

# =========================================
# BROKER LINKS
# =========================================
st.write("---")

st.header("💳 Beginner-Friendly Investment Platforms")

st.markdown("""
- https://robinhood.com  
- https://www.webull.com  
- https://www.sofi.com/invest  
- https://www.fidelity.com  
""")
