import streamlit as st
import requests
import yfinance as yf
import random

# =========================================
# PAGE
# =========================================
st.set_page_config(page_title="Guardian AI", layout="wide")

st.title("🧠 Guardian AI — Clean Signal Micro Scanner")

st.markdown("""
## 📌 Purpose

This scanner filters real market movers into:

- clean momentum setups
- low-dollar speculative opportunities
- beginner-readable signals

It removes noise and low-quality spikes.
""")

st.write("---")

# =========================================
# FILTERS
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
# MARKET MOVERS
# =========================================
def get_market_movers():

    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"

    params = {"scrIds": "day_gainers", "count": 100}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()

        quotes = data["finance"]["result"][0]["quotes"]

        return [
            q["symbol"]
            for q in quotes
            if q.get("symbol")
        ]

    except:
        return []

# =========================================
# STOCK DATA
# =========================================
def fetch(symbol):

    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="5d")

        if hist.empty:
            return None

        price = hist["Close"].iloc[-1]

        if price < min_price or price > max_price:
            return None

        volume = hist["Volume"].iloc[-1]
        avg_volume = hist["Volume"].mean()

        # HARD FILTER: remove illiquid noise
        if volume < 100000:
            return None

        momentum = hist["Close"].iloc[-1] - hist["Close"].iloc[0]

        return {
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "avg_volume": avg_volume,
            "momentum": momentum,
            "rel_volume": volume / avg_volume if avg_volume else 0
        }

    except:
        return None

# =========================================
# SIGNAL ENGINE (IMPROVED)
# =========================================
def score_stock(d):

    vol_strength = d["rel_volume"]
    momentum = d["momentum"]

    score = 0

    # volume strength weighting
    if vol_strength > 2:
        score += 2
    elif vol_strength > 1:
        score += 1

    # momentum weighting
    if momentum > 0:
        score += 1
    if momentum > d["price"] * 0.02:
        score += 1

    return score

# =========================================
# ANALYSIS
# =========================================
def analyze(d):

    if not d:
        return None

    score = score_stock(d)

    shares = int(investment / d["price"])

    if score >= 3:
        label = "🔥 Strong Clean Momentum"
        window = "1–4 days"
    elif score == 2:
        label = "⚠️ Developing Setup"
        window = "1–3 days"
    else:
        label = "❌ Weak / Noisy"
        window = "Unclear"

    if d["price"] < 0.50:
        risk = "🔴 Extreme Risk"
    elif d["price"] < 2:
        risk = "🟠 High Risk"
    else:
        risk = "🟡 Speculative"

    return {
        "symbol": d["symbol"],
        "price": round(d["price"], 2),
        "shares": shares,
        "label": label,
        "risk": risk,
        "window": window,
        "rel_volume": round(d["rel_volume"], 2),
        "momentum": round(d["momentum"], 2),
        "score": score
    }

# =========================================
# RUN SCAN
# =========================================
st.header("📡 Live Clean Scan")

if st.button("Scan Market"):

    symbols = get_market_movers()

    if not symbols:
        st.error("Market data unavailable")
        st.stop()

    results = []

    progress = st.progress(0)

    for i, s in enumerate(symbols):

        d = fetch(s)
        r = analyze(d)

        if r:
            results.append(r)

        progress.progress((i + 1) / len(symbols))

    results.sort(key=lambda x: x["score"], reverse=True)

    if not results:
        st.warning("No clean signals found.")

    for r in results[:8]:

        st.write("---")

        st.subheader(f"{r['symbol']} — {r['label']}")

        st.markdown(f"""
### 💵 Price
${r['price']}

### 💸 Your ${investment}
Approx shares: {r['shares']}

### 📊 Signal Strength
Score: {r['score']}/4  
Relative Volume: {r['rel_volume']}

### ⚠️ Risk
{r['risk']}

### ⏳ Window
{r['window']}
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

sym = st.text_input("Symbol")

if st.button("Analyze") and sym:

    t = yf.Ticker(sym.upper())
    h = t.history(period="5d")

    if h.empty:
        st.warning("No data")
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
