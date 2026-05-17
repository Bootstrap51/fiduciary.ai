import streamlit as st
import requests
import yfinance as yf
import random

# =========================================
# PAGE
# =========================================
st.set_page_config(page_title="Guardian AI", layout="wide")

st.title("🧠 Guardian AI — Live Micro Market Scanner")

st.markdown("""
## 📌 What This Does

Guardian AI scans live market movers and ranks:

- cheap stocks
- active movement
- beginner-friendly speculative setups

It does NOT try to eliminate everything.
It ranks what exists.
""")

st.write("---")

# =========================================
# SETTINGS
# =========================================
st.header("⚙️ Settings")

price_range = st.selectbox(
    "Price Range",
    ["$0.01 - $1", "$1 - $3", "$3 - $5"]
)

if price_range == "$0.01 - $1":
    min_price, max_price = 0.01, 1.00
elif price_range == "$1 - $3":
    min_price, max_price = 1.00, 3.00
else:
    min_price, max_price = 3.00, 5.00

investment = st.selectbox("Micro Budget ($)", [1, 2, 5], index=2)

st.write("---")

# =========================================
# MARKET MOVERS (LIVE)
# =========================================
def get_market_movers():

    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"

    params = {"scrIds": "day_gainers", "count": 100}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()

        quotes = data["finance"]["result"][0]["quotes"]

        return [q["symbol"] for q in quotes if q.get("symbol")]

    except:
        return []

# =========================================
# STOCK DATA
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

        momentum = h["Close"].iloc[-1] - h["Close"].iloc[0]

        # softer liquidity filter (do NOT kill results)
        if volume < 20000:
            return None

        rel_volume = volume / avg_volume if avg_volume else 1

        return {
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "avg_volume": avg_volume,
            "momentum": momentum,
            "rel_volume": rel_volume
        }

    except:
        return None

# =========================================
# SCORING ENGINE (SOFT + RANKING)
# =========================================
def score(d):

    score = 0

    # volume strength (soft)
    if d["rel_volume"] > 3:
        score += 2
    elif d["rel_volume"] > 1.5:
        score += 1
    else:
        score += 0.5

    # momentum
    if d["momentum"] > 0:
        score += 1
    elif d["momentum"] > -d["price"] * 0.01:
        score += 0.3

    return score

# =========================================
# ANALYSIS
# =========================================
def analyze(d):

    if not d:
        return None

    s = score(d)

    shares = int(investment / d["price"])

    # LABELS (NO DEAD-END FILTERING)
    if s >= 2.5:
        label = "🔥 Strong Momentum"
        window = "1–4 days"
    elif s >= 1.5:
        label = "⚠️ Active Setup"
        window = "1–3 days"
    else:
        label = "👀 Weak but Moving"
        window = "Uncertain"

    if d["price"] < 0.50:
        risk = "🔴 Very High Risk"
    elif d["price"] < 2:
        risk = "🟠 High Risk"
    else:
        risk = "🟡 Speculative"

    opinion_pool = [
        "Short-term movement possible",
        "Low conviction but active trading",
        "Momentum is unstable but present",
        "Watch for volume continuation",
        "No strong trend yet"
    ]

    return {
        "symbol": d["symbol"],
        "price": round(d["price"], 2),
        "shares": shares,
        "score": round(s, 2),
        "label": label,
        "risk": risk,
        "window": window,
        "opinion": random.choice(opinion_pool),
        "rel_volume": round(d["rel_volume"], 2)
    }

# =========================================
# SCAN
# =========================================
st.header("📡 Live Discovery Engine")

if st.button("Scan Market"):

    symbols = get_market_movers()

    if not symbols:
        st.error("Market data unavailable.")
        st.stop()

    results = []

    progress = st.progress(0)

    for i, sym in enumerate(symbols):

        d = fetch(sym)
        r = analyze(d)

        if r:
            results.append(r)

        progress.progress((i + 1) / len(symbols))

    # ALWAYS SORT AND SHOW TOP RESULTS
    results.sort(key=lambda x: x["score"], reverse=True)

    if not results:
        st.warning("No usable data found — try again.")

    st.subheader("Top Opportunities (Ranked)")

    for r in results[:10]:

        st.write("---")

        st.subheader(f"{r['symbol']} — {r['label']}")

        st.markdown(f"""
### 💵 Price
${r['price']}

### 💸 Your ${investment}
Approx shares: {r['shares']}

### 📊 Score
{r['score']} / 4

### ⚠️ Risk
{r['risk']}

### ⏳ Window
{r['window']}

### 🤖 Guardian Insight
{r['opinion']}
""")

        st.link_button(
            "View Chart",
            f"https://finance.yahoo.com/quote/{r['symbol']}"
        )

# =========================================
# MANUAL MODE
# =========================================
st.write("---")

st.header("✈️ Manual Check")

sym = st.text_input("Enter Symbol")

if st.button("Analyze") and sym:

    t = yf.Ticker(sym.upper())
    h = t.history(period="5d")

    if h.empty:
        st.warning("No data.")
        st.stop()

    price = h["Close"].iloc[-1]

    st.subheader(sym.upper())
    st.write(f"Price: ${round(price,2)}")
    st.write(f"Shares: {int(investment/price)}")

    st.link_button(
        "View Chart",
        f"https://finance.yahoo.com/quote/{sym.upper()}"
    )

# =========================================
# FOOTER
# =========================================
st.write("---")

st.header("💳 Platforms")

st.markdown("""
- https://robinhood.com  
- https://www.webull.com  
- https://www.fidelity.com  
- https://www.sofi.com/invest  
""")
