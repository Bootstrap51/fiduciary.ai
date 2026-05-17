import streamlit as st
import yfinance as yf
import random

# =========================================
# PAGE SETUP
# =========================================
st.set_page_config(
    page_title="Guardian AI",
    layout="wide"
)

st.title("🧠 Guardian AI — Penny Stock Discovery")

# =========================================
# INTRO
# =========================================
st.markdown("""
## 📌 What Guardian AI Does

Guardian AI helps beginner and micro-investors discover:

- Cheap penny stocks
- Active low-cost opportunities
- Beginner-friendly speculative plays
- Simple momentum-based setups

---

## ⚠️ Important

Penny stocks are highly speculative.

This tool does NOT guarantee profits.

Guardian AI is designed to:
- simplify research
- reduce confusion
- help beginners learn
""")

st.write("---")

# =========================================
# PRICE RANGE FILTER
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

# RANGE LOGIC
if price_range == "$0.01 - $1.00":
    min_price = 0.01
    max_price = 1.00

elif price_range == "$1.00 - $3.00":
    min_price = 1.00
    max_price = 3.00

else:
    min_price = 3.00
    max_price = 5.00

# =========================================
# INVESTMENT AMOUNT
# =========================================
investment_amount = st.selectbox(
    "How Much Are You Experimenting With?",
    [1, 2, 5],
    index=2
)

st.write("---")

# =========================================
# PENNY STOCK UNIVERSE
# =========================================
PENNY_STOCKS = [
    "SNDL",
    "MULN",
    "OCGN",
    "TELL",
    "WKHS",
    "CLOV",
    "ATER",
    "CEI",
    "IDEX",
    "XELA",
    "GNUS",
    "CTRM",
    "HUSA",
    "TOPS",
    "ZOM",
    "SOS",
    "BIOR",
    "COSM",
    "NAK",
    "JOBY",
    "RIDE",
    "GSAT",
    "BNGO",
    "VERB",
    "WISH",
    "HEPS",
    "AVTX"
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

        current_price = round(
            hist["Close"].iloc[-1],
            2
        )

        # FILTER PRICE RANGE
        if current_price < min_price:
            return None

        if current_price > max_price:
            return None

        volume_today = hist["Volume"].iloc[-1]

        avg_volume = hist["Volume"].mean()

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
# ANALYZE STOCK
# =========================================
def analyze_stock(data):

    if not data:
        return None

    # SHARES
    shares = int(
        investment_amount / data["price"]
    )

    # ACTIVITY
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

    # SETUP LABEL
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

    # MOMENTUM WINDOW
    if score == 2:
        window = "1–5 days"

    elif score == 1:
        window = "1–3 days"

    else:
        window = "Weak momentum"

    # OPINION
    if score == 2:
        opinion = random.choice([
            "Momentum appears active",
            "Retail activity increasing",
            "Volume and price movement look strong"
        ])

    elif score == 1:
        opinion = random.choice([
            "Moderate speculative activity",
            "Worth watching carefully",
            "Some momentum detected"
        ])

    else:
        opinion = random.choice([
            "Limited current activity",
            "Weak setup right now",
            "Low momentum currently"
        ])

    return {
        "symbol": data["symbol"],
        "price": data["price"],
        "shares": shares,
        "setup": setup,
        "risk": risk,
        "window": window,
        "opinion": opinion,
        "volume_spike": volume_spike,
        "momentum_up": momentum_up,
        "score": score
    }

# =========================================
# DISCOVERY MODE
# =========================================
st.header("📡 Guardian Discovery")

if st.button("Find Penny Stock Opportunities"):

    opportunities = []

    progress = st.progress(0)

    for i, symbol in enumerate(PENNY_STOCKS):

        stock_data = get_stock_data(symbol)

        result = analyze_stock(stock_data)

        if result:
            opportunities.append(result)

        progress.progress(
            (i + 1) / len(PENNY_STOCKS)
        )

    # SORT BEST FIRST
    opportunities.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    if not opportunities:
        st.warning(
            "No active penny stock opportunities found."
        )

    # DISPLAY RESULTS
    for stock in opportunities[:10]:

        st.write("---")

        st.subheader(
            f"{stock['symbol']} — {stock['setup']}"
        )

        st.markdown(f"""
### 💵 Stock Price
${stock['price']} per share

### 💸 Your ${investment_amount}
Approximate shares:
{stock['shares']}

### 📈 Why Guardian Flagged It
""")

        if stock["volume_spike"]:
            st.write(
                "✔ Trading volume is increasing"
            )

        if stock["momentum_up"]:
            st.write(
                "✔ Price momentum is moving upward"
            )

        if (
            not stock["volume_spike"]
            and
            not stock["momentum_up"]
        ):
            st.write(
                "• Limited activity currently"
            )

        st.markdown(f"""
### ⚠️ Risk
{stock['risk']}

### ⏳ Momentum Window
{stock['window']}

### 🤖 Guardian Opinion
{stock['opinion']}
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
### 💵 Stock Price
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

            st.link_button(
                "View Stock Chart",
                f"https://finance.yahoo.com/quote/{custom_symbol.upper()}"
            )

        else:

            st.warning(
                "Stock unavailable or outside selected price range."
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
