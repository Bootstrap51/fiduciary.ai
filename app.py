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

st.title("🧠 Guardian AI — Ranked Penny Stock Discovery")

st.markdown("""
Guardian AI scans low-cost speculative stocks and ranks them by:

- momentum
- activity
- relative trading volume

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
# SYMBOL POOL
# =========================================
SYMBOLS = [

    "SNDL","MULN","TELL","ZOM","HUSA",
    "TOPS","SOS","XELA","CEI","BIOR",
    "IDEX","CTRM","COSM","GNUS","VERB",

    "WKHS","CLOV","OCGN","BNGO","WISH",
    "AVTX","HEPS","RIDE","GSAT","ATER",

    "OPEN","SOUN","JOBY","PLUG","NVAX",
    "BB","TLRY","FUBO","PENN","RIOT",

    "IONQ","ACHR","ASTS","RKLB","DNA",
    "LCID","NIO","SOFI","PLTR","HOOD"
]

# =========================================
# FETCH STOCK DATA
# =========================================
def fetch(symbol):

    try:

        t = yf.Ticker(symbol)

        h = t.history(period="5d")

        if h.empty:
            return None

        price = float(h["Close"].iloc[-1])

        if price < min_price or price > max_price:
            return None

        volume = float(h["Volume"].iloc[-1])

        avg_volume = float(h["Volume"].mean())

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
# SCORE ENGINE
# =========================================
def analyze(d):

    if not d:
        return None

    score = 0

    # PRICE ACTIVITY
    if d["price"] < 1:
        score += 1

    # MOMENTUM
    if d["momentum"] > 0:
        score += 1

    # RELATIVE VOLUME
    if d["rel_volume"] > 1:
        score += 1

    shares = int(investment / d["price"])

    # LABELS
    if score == 3:
        label = "🔥 Strong Momentum"

    elif score == 2:
        label = "⚠️ Active"

    else:
        label = "👀 Watch"

    # RISK
    if d["price"] < 0.50:
        risk = "🔴 Extreme"

    elif d["price"] < 2:
        risk = "🟠 High"

    else:
        risk = "🟡 Speculative"

    opinions = [
        "Retail activity appears elevated",
        "Momentum may be building",
        "Watching for continuation",
        "Speculative activity present",
        "Possible short-term movement"
    ]

    return {
        "symbol": d["symbol"],
        "price": d["price"],
        "shares": shares,
        "score": score,
        "risk": risk,
        "label": label,
        "opinion": random.choice(opinions)
    }

# =========================================
# SCAN
# =========================================
st.header("📡 Ranked Discovery Engine")

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

    # SORT BEST FIRST
    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    if not results:

        st.warning(
            "No matching stocks found."
        )

    else:

        st.subheader(
            "Top Penny Stock Opportunities"
        )

        for r in results[:10]:

            st.write("---")

            st.subheader(
                f"{r['symbol']} — {r['label']}"
            )

            st.markdown(f"""
### 💵 Price
${r['price']}

### 💸 Your ${investment}
Approximate shares:
{r['shares']}

### 📊 Activity Score
{r['score']} / 3

### ⚠️ Risk
{r['risk']}

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

manual = st.text_input(
    "Enter Symbol"
)

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
            "No usable data for this stock."
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
