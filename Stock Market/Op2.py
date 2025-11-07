import streamlit as st
import pandas as pd
import requests
import os
import time
from datetime import datetime
import plotly.express as px
import numpy as np

st.set_page_config(page_title="NSE Option Chain Intelligence", layout="wide")

# ------------------------------------
# Fetch NSE Option Chain JSON
# ------------------------------------
@st.cache_data(ttl=300)  # cache for 5 minutes
def fetch_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://www.nseindia.com/option-chain?symbol={symbol}",
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers, timeout=10)
    r = session.get(url, headers=headers, timeout=10)
    data = r.json()

    records = data.get("records", {}).get("data", [])
    rows = []
    for record in records:
        strike = record.get("strikePrice")
        expiry = record.get("expiryDate")
        ce = record.get("CE", {})
        pe = record.get("PE", {})

        rows.append({
            "Expiry": expiry,
            "StrikePrice": strike,
            "CE_OI": ce.get("openInterest"),
            "CE_ChangeOI": ce.get("changeinOpenInterest"),
            "CE_LTP": ce.get("lastPrice"),
            "PE_OI": pe.get("openInterest"),
            "PE_ChangeOI": pe.get("changeinOpenInterest"),
            "PE_LTP": pe.get("lastPrice"),
        })

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["StrikePrice"])
    df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df


# ------------------------------------
# Save tick data
# ------------------------------------
def save_tick(df, symbol):
    today = datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join("data", today)
    os.makedirs(folder, exist_ok=True)

    filename = os.path.join(folder, f"{symbol}_ticks.xlsx")

    if os.path.exists(filename):
        old = pd.read_excel(filename)
        new = pd.concat([old, df], ignore_index=True)
    else:
        new = df

    new.to_excel(filename, index=False)


# ------------------------------------
# Helper Functions
# ------------------------------------
def interpret_signal(change_oi, ltp_change):
    if change_oi > 0 and ltp_change > 0:
        return "🟢 Long Build-up"
    elif change_oi > 0 and ltp_change < 0:
        return "🔴 Short Build-up"
    elif change_oi < 0 and ltp_change > 0:
        return "🟡 Short Covering"
    elif change_oi < 0 and ltp_change < 0:
        return "🔵 Long Unwinding"
    else:
        return "⚪ Neutral"


def compute_pcr(df):
    total_put_oi = df["PE_OI"].sum()
    total_call_oi = df["CE_OI"].sum()
    return round(total_put_oi / total_call_oi, 2) if total_call_oi else 0


def compute_max_pain(df):
    strikes = df["StrikePrice"].unique()
    pain = {}
    for strike in strikes:
        ce_loss = ((strike - df["StrikePrice"]).clip(lower=0) * df["CE_OI"]).sum()
        pe_loss = ((df["StrikePrice"] - strike).clip(lower=0) * df["PE_OI"]).sum()
        pain[strike] = ce_loss + pe_loss
    min_pain_strike = min(pain, key=pain.get)
    return min_pain_strike


def compute_sentiment(df):
    ce_pressure = df["CE_ChangeOI"].sum()
    pe_pressure = df["PE_ChangeOI"].sum()
    if pe_pressure > ce_pressure * 1.2:
        return "🟢 Bullish Bias"
    elif ce_pressure > pe_pressure * 1.2:
        return "🔴 Bearish Bias"
    else:
        return "⚪ Neutral"


# ------------------------------------
# Streamlit UI
# ------------------------------------
st.title("📊 NSE Option Chain Intelligence Dashboard")
st.caption("Live Option Chain Tracker with Alerts, PCR, Max Pain, and OI Insights")

symbol = st.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
st.info("Fetching data every 5 minutes automatically.")

df = fetch_option_chain(symbol)
if df is not None and not df.empty:
    save_tick(df, symbol)

    expiry_selected = st.selectbox("Select Expiry", sorted(df["Expiry"].unique()))
    df = df[df["Expiry"] == expiry_selected].copy()

    df["CE_Signal"] = df.apply(lambda x: interpret_signal(x["CE_ChangeOI"], x["CE_LTP"]), axis=1)
    df["PE_Signal"] = df.apply(lambda x: interpret_signal(x["PE_ChangeOI"], x["PE_LTP"]), axis=1)

    # Identify Active and Neutral
    active_df = df[
        (abs(df["CE_ChangeOI"]) > df["CE_ChangeOI"].mean()) | (abs(df["PE_ChangeOI"]) > df["PE_ChangeOI"].mean())
    ]
    neutral_df = df.drop(active_df.index)

    st.subheader(f"🔥 Active Strike Prices — {symbol} ({expiry_selected})")
    st.dataframe(active_df, use_container_width=True)

    with st.expander("⚪ Neutral Strikes"):
        st.dataframe(neutral_df, use_container_width=True)

    # OI Change Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Call OI Change (CE)")
        fig1 = px.bar(active_df, x="StrikePrice", y="CE_ChangeOI", color="CE_Signal", title="Call Side Activity")
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("Put OI Change (PE)")
        fig2 = px.bar(active_df, x="StrikePrice", y="PE_ChangeOI", color="PE_Signal", title="Put Side Activity")
        st.plotly_chart(fig2, use_container_width=True)

    # Metrics
    pcr = compute_pcr(df)
    max_pain = compute_max_pain(df)
    sentiment = compute_sentiment(df)

    st.markdown("### 📈 Market Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("PCR (Put/Call Ratio)", pcr)
    col2.metric("Max Pain Strike", max_pain)
    col3.metric("AI Sentiment", sentiment)

    # Alerts
    alerts = df[
        (abs(df["CE_ChangeOI"]) > df["CE_OI"].mean() * 0.1) | (abs(df["PE_ChangeOI"]) > df["PE_OI"].mean() * 0.1)
    ]
    if not alerts.empty:
        st.warning("🚨 Significant OI Change Detected!")
        st.dataframe(alerts[["StrikePrice", "CE_ChangeOI", "PE_ChangeOI", "CE_LTP", "PE_LTP"]])

    # Cumulative OI trend (top 10 active)
    top10 = df.nlargest(10, ["CE_ChangeOI", "PE_ChangeOI"])
    fig3 = px.line(top10, x="StrikePrice", y=["CE_ChangeOI", "PE_ChangeOI"], markers=True, title="Cumulative OI Change (Top 10)")
    st.plotly_chart(fig3, use_container_width=True)

    # Save summary at end of day
    today = datetime.now().strftime("%H:%M:%S")
    st.success(f"✅ Data refreshed successfully at {today}")
else:
    st.error("Failed to fetch data. Please try again later.")
    