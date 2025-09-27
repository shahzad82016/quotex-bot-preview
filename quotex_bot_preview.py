# quotex_bot_preview_fixed.py

import streamlit as st  # Must be first
st.set_page_config(page_title="Quotex Bot Preview", layout="wide")

import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

st.title("Quotex Bot Preview - Live Signal Simulation")

# Sidebar settings
st.sidebar.header("Bot Settings")
asset = st.sidebar.text_input("Asset (symbol)", "EUR/USD")
stake = st.sidebar.number_input("Stake amount", min_value=1.0, value=1.0, step=0.5)
start_button = st.sidebar.button("Start Bot")
stop_button = st.sidebar.button("Stop Bot")

# Placeholders
chart_placeholder = st.empty()
log_placeholder = st.empty()

# Strategy class
class OneMinStrategy:
    def __init__(self):
        self.df = pd.DataFrame(columns=["close"])
        self.signals = []

    def add_price(self, price):
        self.df = pd.concat([self.df, pd.DataFrame([{"close": price}])], ignore_index=True)
        if len(self.df) > 100:
            self.df = self.df.iloc[-100:].reset_index(drop=True)
        sig = self.signal()
        if sig:
            self.signals.append((len(self.df)-1, sig))
        return sig

    def signal(self):
        if len(self.df) < 20:
            return None
        closes = self.df['close']
        sma_short = closes.rolling(3).mean().iloc[-1]
        sma_long  = closes.rolling(20).mean().iloc[-1]
        delta = closes.iloc[-1] - closes.iloc[-3]
        if sma_short > sma_long and delta > 0:
            return "CALL"
        if sma_short < sma_long and delta < 0:
            return "PUT"
        return None

# Initialize session state
if "bot_running" not in st.session_state:
    st.session_state.bot_running = False

strategy = OneMinStrategy()
logs = []

# Update chart function
def update_chart():
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(strategy.df['close'], label="Price", color="blue")
    for idx, sig in strategy.signals:
        color = "green" if sig=="CALL" else "red"
        ax.scatter(idx, strategy.df['close'].iloc[idx], color=color, marker="^" if sig=="CALL" else "v")
    ax.set_title(f"Live Price Chart - {asset}")
    ax.legend()
    chart_placeholder.pyplot(fig)

# Start/Stop
if start_button:
    st.session_state.bot_running = True
if stop_button:
    st.session_state.bot_running = False

# Run simulation
while st.session_state.bot_running:
    new_price = 1.10 + np.random.randn()*0.001  # simulated price
    sig = strategy.add_price(new_price)
    if sig:
        logs.append(f"{time.strftime('%H:%M:%S')} - Signal: {sig} - Price: {new_price:.5f}")
    if len(logs) > 100:
        logs = logs[-100:]
    update_chart()
    log_placeholder.text("\n".join(logs))
    time.sleep(0.5)
