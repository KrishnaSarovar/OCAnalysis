import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, time as dtime, timedelta
import plotly.express as px
import numpy as np
import tempfile
import shutil
import time
import random

st.set_page_config(page_title="📊 NSE Option Chain Intelligence", layout="wide")

# ------------------------------------
# Auto-refresh every 5 minutes
# ------------------------------------
st.markdown("<meta http-equiv='refresh' content='300'>", unsafe_allow_html=True)

# ------------------------------------
# Market Timings
# ------------------------------------
MARKET_OPEN = dtime(9, 10)
MARKET_CLOSE = dtime(22, 00)


def market_is_open():
    now = datetime.now().time()
    return MARKET_OPEN <= now <= MARKET_CLOSE


# ------------------------------------
# Fetch NSE Option Chain JSON
# ------------------------------------
def fetch_option_chain(symbol="NIFTY", retries=3):
    """Fetch NSE Option Chain data with retry and error handling."""
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://www.nseindia.com/option-chain?symbol={symbol}",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    for attempt in range(retries):
        try:
            session = requests.Session()
            # Important: get cookies first
            session.get("https://www.nseindia.com", headers=headers, timeout=60)
            time.sleep(random.uniform(5, 6))  # polite delay

            response = session.get(url, headers=headers, timeout=60)

            # Handle blank or invalid response
            if not response.text.strip():
                raise ValueError("Empty response from NSE")

            # Some responses are HTML (blocked)
            if response.text.strip().startswith("<"):
                raise ValueError("Received HTML instead of JSON (likely blocked)")

            data = response.json()  # Safe to parse JSON now

            records = data.get("records", {}).get("data", [])
            underlying_value = data.get("records", {}).get("underlyingValue", 0)

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

            df = pd.DataFrame(rows).dropna(subset=["StrikePrice"])
            df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df["Underlying"] = underlying_value

            return df

        except Exception as e:
            st.warning(f"⚠️ Attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(2)

    st.error("❌ Failed to fetch NSE Option Chain after multiple attempts.")
    return pd.DataFrame()

# ------------------------------------
# Save tick data safely
# ------------------------------------
def save_tick(df, symbol):
    today = datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join("data", today)
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{symbol}_ticks.xlsx")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    temp_path = temp_file.name
    temp_file.close()

    try:
        if os.path.exists(filename):
            old = pd.read_excel(filename)
            new = pd.concat([old, df], ignore_index=True)
        else:
            new = df

        new.to_excel(temp_path, index=False)
        shutil.move(temp_path, filename)

    except Exception as e:
        st.error(f"❌ Error saving tick data: {e}")


# ------------------------------------
# Helper Functions
# ------------------------------------
def interpret_whale_activity(change_oi, ltp, option_type="CE"):
    if option_type == "CE":
        if change_oi > 0 and ltp > 0:
            return "🟢 Call Buying"
        elif change_oi > 0 and ltp < 0:
            return "🔴 Call Writing"
        elif change_oi < 0 and ltp > 0:
            return "🟡 Call Short Covering"
        elif change_oi < 0 and ltp < 0:
            return "🔵 Call Long Unwinding"
    else:
        if change_oi > 0 and ltp > 0:
            return "🔴 Put Writing"
        elif change_oi > 0 and ltp < 0:
            return "🟢 Put Buying"
        elif change_oi < 0 and ltp > 0:
            return "🔵 Put Long Unwinding"
        elif change_oi < 0 and ltp < 0:
            return "🟡 Put Short Covering"
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
    return min(pain, key=pain.get)


def compute_sentiment(df):
    ce_pressure = df["CE_ChangeOI"].sum()
    pe_pressure = df["PE_ChangeOI"].sum()
    if pe_pressure > ce_pressure * 1.2:
        return "🟢 Bullish Bias"
    elif ce_pressure > pe_pressure * 1.2:
        return "🔴 Bearish Bias"
    else:
        return "⚪ Neutral"


def estimate_range(df):
    call_strikes = df.loc[df["CE_OI"].nlargest(3).index, "StrikePrice"].tolist()
    put_strikes = df.loc[df["PE_OI"].nlargest(3).index, "StrikePrice"].tolist()
    return min(put_strikes), max(call_strikes)


# ------------------------------------
# Time-based OI Distribution
# ------------------------------------
# def compute_oi_distribution(hist, interval_minutes=30, strike_range=500):
#     hist["Timestamp"] = pd.to_datetime(hist["Timestamp"])
#     latest_underlying = hist["Underlying"].iloc[-1]
#     atm = round(latest_underlying / 50) * 50

#     # Filter within ATM ± range
#     hist = hist[(hist["StrikePrice"] >= atm - strike_range) &
#                 (hist["StrikePrice"] <= atm + strike_range)]

#     # Create time buckets
#     start_time = hist["Timestamp"].min().floor("T")
#     end_time = hist["Timestamp"].max().ceil("T")
#     time_bins = pd.date_range(start_time, end_time, freq=f"{interval_minutes}min")

#     hist["TimeBin"] = pd.cut(hist["Timestamp"], bins=time_bins)

#     agg = hist.groupby("TimeBin")[["CE_ChangeOI", "PE_ChangeOI"]].sum().reset_index()

#     agg["StartTime"] = agg["TimeBin"].apply(lambda x: x.left.strftime("%H:%M") if pd.notnull(x) else "")
#     agg["EndTime"] = agg["TimeBin"].apply(lambda x: x.right.strftime("%H:%M") if pd.notnull(x) else "")
#     agg["Window"] = agg["StartTime"].astype(str) + "–" + agg["EndTime"].astype(str)

#     agg = agg.sort_values(by="StartTime")
#     return agg, atm
def compute_strike_time_distribution(hist, interval_minutes=30, strike_range=500):
    hist["Timestamp"] = pd.to_datetime(hist["Timestamp"])
    latest_underlying = hist["Underlying"].iloc[-1]
    atm = round(latest_underlying / 50) * 50

    # Filter within ATM ± range
    hist = hist[
        (hist["StrikePrice"] >= atm - strike_range) &
        (hist["StrikePrice"] <= atm + strike_range)
    ].copy()

    # Create time bins
    start_time = hist["Timestamp"].min().floor("T")
    end_time = hist["Timestamp"].max().ceil("T")
    time_bins = pd.date_range(start_time, end_time, freq=f"{interval_minutes}min")

    hist["TimeBin"] = pd.cut(hist["Timestamp"], bins=time_bins)

    # Aggregate OI change by Strike + Time window
    agg = (
        hist.groupby(["TimeBin", "StrikePrice"])
        [["CE_ChangeOI", "PE_ChangeOI"]]
        .sum()
        .reset_index()
    )

    # Label bins for plotting
    agg["StartTime"] = agg["TimeBin"].apply(lambda x: x.left.strftime("%H:%M") if pd.notnull(x) else "")
    agg["EndTime"] = agg["TimeBin"].apply(lambda x: x.right.strftime("%H:%M") if pd.notnull(x) else "")
    agg["Window"] = agg["StartTime"].astype(str) + "–" + agg["EndTime"].astype(str)

    return agg, atm

# ------------------------------------
# Streamlit UI
# ------------------------------------
st.title("📊 NSE Option Chain Intelligence Dashboard")
st.caption("Live Option Chain Tracker with Max Pain, Sentiment & Position Distribution Analytics")

symbol = st.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

if not market_is_open():
    st.warning("⏳ Market Closed. Dashboard updates only during 9:15–3:30.")
else:
    st.info("🔄 Auto-refresh active (5 min)")

    df = fetch_option_chain(symbol)
    if df is not None and not df.empty:
        save_tick(df, symbol)

        # ---- Expiry Sorting ----
        expiry_sorted = sorted(pd.to_datetime(df["Expiry"].unique()))
        expiry_selected = st.selectbox(
            "Select Expiry", [d.strftime("%d-%b-%Y") for d in expiry_sorted[:6]]
        )

        df = df[df["Expiry"] == pd.to_datetime(expiry_selected).strftime("%d-%b-%Y")]

        # ---- ATM-based Strike Range ----
        atm = round(df["Underlying"].iloc[-1] / 50) * 50
        df = df[(df["StrikePrice"] >= atm - 1500) & (df["StrikePrice"] <= atm + 1500)]

        # ---- Whale Activity ----
        df["CE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["CE_ChangeOI"], x["CE_LTP"], "CE"), axis=1)
        df["PE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["PE_ChangeOI"], x["PE_LTP"], "PE"), axis=1)

        # ---- Active Strikes ----
        threshold_multiplier = 1.5
        active_df = df[
            (abs(df["CE_ChangeOI"]) > df["CE_ChangeOI"].mean() * threshold_multiplier)
            | (abs(df["PE_ChangeOI"]) > df["PE_ChangeOI"].mean() * threshold_multiplier)
        ]

        st.subheader(f"🔥 Active Strike Prices — {symbol} ({expiry_selected})")
        st.dataframe(active_df, use_container_width=True)

        # ---- Key Metrics ----
        pcr = compute_pcr(df)
        max_pain = compute_max_pain(df)
        sentiment = compute_sentiment(df)
        low, high = estimate_range(df)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("PCR", pcr)
        c2.metric("Max Pain", max_pain)
        c3.metric("Range Low", low)
        c4.metric("Range High", high)
        st.markdown(f"**AI Sentiment:** {sentiment}")

        # ---- Visuals ----
        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.bar(active_df, x="StrikePrice", y="CE_ChangeOI", color="CE_Signal",
                          title="Call OI Change (Buying vs Writing)")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.bar(active_df, x="StrikePrice", y="PE_ChangeOI", color="PE_Signal",
                          title="Put OI Change (Buying vs Writing)")
            st.plotly_chart(fig2, use_container_width=True)

        # ---- Max Pain Shift ----
        today = datetime.now().strftime("%Y-%m-%d")
        hist_path = os.path.join("data", today, f"{symbol}_ticks.xlsx")
        if os.path.exists(hist_path):
            hist = pd.read_excel(hist_path)
            hist["Timestamp"] = pd.to_datetime(hist["Timestamp"])

            # compute max pain per timestamp
            mp_list = []
            for t in hist["Timestamp"].unique():
                snap = hist[hist["Timestamp"] == t]
                mp_list.append({"Timestamp": t, "MaxPain": compute_max_pain(snap)})

            hist_pain = pd.DataFrame(mp_list).sort_values("Timestamp")

            fig3 = px.line(hist_pain, x="Timestamp", y="MaxPain", markers=True,
                           title="📈 Max Pain Point Shift Throughout Day")
            st.plotly_chart(fig3, use_container_width=True)

            # ---- Time Interval Selector ----
            interval = st.select_slider("Select Time Interval (minutes)", options=[15, 30, 45, 60], value=30)

            # ---- OI Build-up Distribution ----
            # agg, atm_val = compute_oi_distribution(hist, interval_minutes=interval, strike_range=500)
            # st.subheader(f"🕒 OI Build-up Distribution Around ATM ±500 ({symbol}) — {interval} min")
            # ---- Strike × Time OI Build-up Distribution ----
            agg, atm_val = compute_strike_time_distribution(hist, interval_minutes=interval, strike_range=500)

            st.subheader(f"📈 Strike × Time OI Build-up (ATM ±500) — {symbol} — {interval} min")

            # Heatmap of CALL OI Change
            fig_call = px.density_heatmap(
                agg,
                x="Window",
                y="StrikePrice",
                z="CE_ChangeOI",
                color_continuous_scale="RdYlGn",
                title=f"CALL OI Change Heatmap (per {interval}-min window)",
            )
            st.plotly_chart(fig_call, use_container_width=True)

            # Heatmap of PUT OI Change
            fig_put = px.density_heatmap(
                agg,
                x="Window",
                y="StrikePrice",
                z="PE_ChangeOI",
                color_continuous_scale="RdYlGn",
                title=f"PUT OI Change Heatmap (per {interval}-min window)",
            )
    else:
        st.error("⚠️ Failed to fetch option chain data.")

