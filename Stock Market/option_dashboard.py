import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, time as dtime
import plotly.express as px
import numpy as np
import time
import random
from supabase import create_client, Client

# ----------------------------
# Supabase Configuration
# ----------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="📊 NSE Option Chain Intelligence", layout="wide")
st.title("📊 NSE Option Chain Intelligence Dashboard")
st.caption("Live Option Chain Tracker with Max Pain, Sentiment & OI Distribution Analytics")

# ------------------------------------
# Auto-refresh every 5 minutes
# ------------------------------------
st.markdown("<meta http-equiv='refresh' content='300'>", unsafe_allow_html=True)

# ------------------------------------
# Market Timings
# ------------------------------------
MARKET_OPEN = dtime(9, 10)
MARKET_CLOSE = dtime(22, 0)

def market_is_open():
    now = datetime.now().time()
    return MARKET_OPEN <= now <= MARKET_CLOSE

# ------------------------------------
# Fetch NSE Option Chain JSON
# ------------------------------------
def fetch_option_chain(symbol="NIFTY", retries=3):
    """Fetch NSE Option Chain data."""
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://www.nseindia.com/option-chain?symbol={symbol}",
    }

    for attempt in range(retries):
        try:
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers, timeout=60)
            time.sleep(random.uniform(5, 6))
            response = session.get(url, headers=headers, timeout=60)

            if not response.text.strip() or response.text.startswith("<"):
                raise ValueError("Invalid NSE response")

            data = response.json()
            records = data.get("records", {}).get("data", [])
            underlying = data.get("records", {}).get("underlyingValue", 0)

            rows = []
            for rec in records:
                strike = rec.get("strikePrice")
                expiry = rec.get("expiryDate")
                ce = rec.get("CE", {})
                pe = rec.get("PE", {})
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

            df = pd.DataFrame(rows).dropna(subset=["StrikePrice"])
            df["Underlying"] = underlying
            df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return df
        except Exception as e:
            st.warning(f"Attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(2)
    st.error("❌ Failed to fetch data after retries")
    return pd.DataFrame()

# ------------------------------------
# Supabase Integration
# ------------------------------------
def save_to_supabase(df, symbol):
    try:
        records = [
            {
                "symbol": symbol,
                "expiry": row["Expiry"],
                "strike_price": row["StrikePrice"],
                "ce_oi": row["CE_OI"],
                "ce_change_oi": row["CE_ChangeOI"],
                "ce_ltp": row["CE_LTP"],
                "pe_oi": row["PE_OI"],
                "pe_change_oi": row["PE_ChangeOI"],
                "pe_ltp": row["PE_LTP"],
                "underlying": row["Underlying"],
                "timestamp": row["Timestamp"]
            }
            for _, row in df.iterrows()
        ]
        supabase.table("option_chain_data").insert(records).execute()
        st.success(f"✅ {len(records)} rows uploaded to Supabase")
    except Exception as e:
        st.error(f"❌ Supabase insert failed: {e}")

def load_from_supabase(symbol):
    try:
        res = supabase.table("option_chain_data").select("*").eq("symbol", symbol).execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"❌ Failed to load history: {e}")
        return pd.DataFrame()

# ------------------------------------
# Helper Calculations
# ------------------------------------
def compute_pcr(df):
    return round(df["PE_OI"].sum() / df["CE_OI"].sum(), 2) if df["CE_OI"].sum() else 0

def compute_max_pain(df):
    strikes = df["StrikePrice"].unique()
    pain = {s: ((s - df["StrikePrice"]).clip(lower=0)*df["CE_OI"]).sum() +
              ((df["StrikePrice"] - s).clip(lower=0)*df["PE_OI"]).sum() for s in strikes}
    return min(pain, key=pain.get)

def compute_sentiment(df):
    ce, pe = df["CE_ChangeOI"].sum(), df["PE_ChangeOI"].sum()
    if pe > ce * 1.2: return "🟢 Bullish Bias"
    elif ce > pe * 1.2: return "🔴 Bearish Bias"
    return "⚪ Neutral"

# ------------------------------------
# Streamlit UI Logic
# ------------------------------------
symbol = st.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

if not market_is_open():
    st.warning("⏳ Market Closed (9:15–3:30 updates only)")
else:
    df = fetch_option_chain(symbol)
    if not df.empty:
        save_to_supabase(df, symbol)

        expiry_sorted = sorted(pd.to_datetime(df["Expiry"].unique()))
        expiry_selected = st.selectbox("Select Expiry", [d.strftime("%d-%b-%Y") for d in expiry_sorted[:6]])
        df = df[df["Expiry"] == pd.to_datetime(expiry_selected).strftime("%d-%b-%Y")]

        pcr = compute_pcr(df)
        max_pain = compute_max_pain(df)
        sentiment = compute_sentiment(df)

        c1, c2, c3 = st.columns(3)
        c1.metric("PCR", pcr)
        c2.metric("Max Pain", max_pain)
        c3.metric("Sentiment", sentiment)

        fig = px.bar(df, x="StrikePrice", y=["CE_ChangeOI", "PE_ChangeOI"], barmode="group",
                     title=f"OI Change — {symbol}")
        st.plotly_chart(fig, use_container_width=True)

        st.success(f"✅ Updated at {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.error("⚠️ Could not fetch live data")

# Historical view
st.subheader("📈 Historical OI Data (Supabase)")
hist = load_from_supabase(symbol)
if not hist.empty:
    st.dataframe(hist.tail(10), use_container_width=True)
else:
    st.info("No historical data available yet.")
