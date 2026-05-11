import streamlit as st
import numpy as np
import time

st.title("🧠 Fiduciary Guardian AI")

symbol = st.text_input("Enter Stock Symbol", "AAPL")
start = st.button("Start")

def engine():
    return {
        "confidence": np.random.randint(40, 95),
        "risk": np.random.randint(10, 90),
        "sentiment": np.random.uniform(-1, 1),
    }

if start:
    box = st.empty()

    for _ in range(50):
        data = engine()

        with box.container():
            st.metric("Confidence", data["confidence"])
            st.metric("Risk", data["risk"])
            st.metric("Sentiment", round(data["sentiment"], 2))

            if data["risk"] > 70:
                st.error("High Risk Zone")
            elif data["confidence"] > 75:
                st.success("Strong Signal")
            else:
                st.warning("Neutral Zone")

        time.sleep(1)
