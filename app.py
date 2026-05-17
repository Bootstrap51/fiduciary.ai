import streamlit as st
import yfinance as yf
import random

# =========================================
# PAGE
# =========================================
st.set_page_config(
    page_title="Guardian AI",
    layout="wide"
)

st.title("🧠 Guardian AI — Penny Stock Discovery Engine")

st.markdown("""
Find active low-cost speculative stocks using:
- live pricing
- momentum
- trading activity

Designed for beginner micro-investors.
""")

st.write("---")

# =========================================
# SETTINGS
# =========================================
st.header("⚙️ Discovery Settings")

price_range = st.selectbox(
    "Price Range",
    [
        "$0.01 - $1",
        "$1 - $3",
        "$3 - $5"
    ]
)

if price_range == "$0.01 - $1":
    min_price = 0.01
    max_price = 1.00

elif price_range == "$1 - $3":
    min_price = 1.00
    max_price = 3.00

else:
    min_price = 3.00
    max_price = 5.00

investment = st.selectbox(
    "Micro Investment Amount ($)",
    [1, 2, 5],
    index=2
)

st.write("---")

# =========================================
# LARGE SYMBOL POOL
# =========================================
SYMBOLS = [

    # SUB $1
    "SNDL","MULN","TELL","ZOM","HUSA",
    "TOPS","SOS","XELA","CEI","BIOR",
    "IDEX","CTRM","COSM","GNUS","VERB",

    # $1-$3
    "WKHS","CLOV","OCGN","BNGO","WISH",
    "AVTX","HEPS","RIDE","GSAT","ATER",

    # $3-$5
    "OPEN","SOUN","JOBY","PLUG","NVAX",
    "BB","TLRY","FUBO","PENN","RIOT",

    # ACTIVE SMALL CAPS
    "IONQ","ACHR","ASTS","RKLB","DNA",
    "LCID","NIO","SOFI","PLTR","HOOD"
]

# =========================================
# FETCH
# =========================================
def fetch(symbol):

    try:

        t = yf.Ticker(symbol)

        h = t.history(period="5d")

        if h.empty:
            return None

        price = h["Close"].iloc[-1]

        if price < min_price or price > max_price:
            return None

        volume = h["Volume"].iloc[-1]
        avg_volume = h["Volume"].mean()

        momentum = (
            h["Close"].iloc[-1]
            -
            h["Close"].iloc[0]
        )

        rel_volume = (
            volume / avg_volume
            if avg_volume else 1
        )

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "volume": volume,
            "momentum": momentum,
            "rel_volume": rel_volume
        }

    except:
        return None

# =========================================
# SCORE
# =========================================
def analyze(d):

    if not d:
        return None

    score = 0

    # MOMENTUM
    if d["momentum"] > 0:
        score += 1

    # RELATIVE VOLUME
    if d["rel_volume"] > 1.2:
        score += 1

    # PRICE ACTIVITY
    if d["price"] < 1:
        score += 1

    shares = int(investment / d["price"])

    # LABELS
    if score >= 3:
        label = "🔥 Strong Activity"

    elif score >= 2:
        label = "⚠️ Active Setup"

    else:
        label = "👀 Weak Activity"

    # RISK
    if d["price"] < 0.50:
        risk = "🔴 Extreme Risk"

    elif d["price"] < 2:
        risk = "🟠 High Risk"

    else:
        risk = "🟡 Speculative"

    opinions = [
        "Momentum may be building",
        "Speculative activity detected",
        "Trading activity elevated",
        "Watch short-term movement",
        "Possible retail interest"
    ]

    return {
        "symbol": d["symbol"],
        "price": d["price"],
        "shares": shares,
        "score": score,
        "label": label,
        "risk": risk,
        "opinion": random.choice(opinions)
    }

# =========================================
# SCAN
# =========================================
st.header("📡 Discovery Engine")

if st.button("Scan Penny Stocks"):

    results = []

    progress = st.progress(0)

    for i, sym in enumerate(SYMBOLS):

        d = fetch(sym)

        r = analyze(d)

        if r:
            results.append(r)

        progress.progress(
            (i + 1) / len(SYMBOLS)
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    if not results:

        st.warning(
            "No matching opportunities found."
        )

    else:

        st.subheader("Top Ranked Opportunities")

        for r in results[:10]:

            st.write("---")

            st.subheader(
                f"{r['symbol']} — {r['label']}"
            )

            st.markdown(f"""
### 💵 Price
${r['price']}

### 💸 Your ${investment}
Approx shares:
{r['shares']}

### ⚠️ Risk
{r['risk']}

### 📊 Activity Score
{r['score']} / 3

### 🤖 Guardian View
{r['opinion']}
""")

            st.link_button(
                "View Chart",
                f"https://finance.yahoo.com/quote/{r['symbol']}"
            )

# =========================================
# MANUAL CHECK
# =========================================
st.write("---")

st.header("✈️ Manual Stock Check")

manual = st.text_input("Enter Symbol")

if st.button("Analyze Symbol") and manual:

    d = fetch(manual.upper())

    r = analyze(d)

    if r:

        st.subheader(
            f"{r['symbol']} — {r['label']}"
        )

        st.write(f"Price: ${r['price']}")
        st.write(f"Risk: {r['risk']}")
        st.write(f"Shares for ${investment}: {r['shares']}")

        st.link_button(
            "View Chart",
            f"https://finance.yahoo.com/quote/{manual.upper()}"
        )

    else:

        st.warning(
            "No usable data for this symbol."
        )

# =========================================
# PLATFORMS
# =========================================
st.write("---")

st.header("💳 Beginner Platforms")

st.markdown("""
- https://robinhood.com  
- https://www.webull.com  
- https://www.fidelity.com  
- https://www.sofi.com/invest  
""")
