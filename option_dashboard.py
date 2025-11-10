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
import pytz
from zoneinfo import ZoneInfo  # built-in (Python 3.9+). prefer over pytz

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
st.markdown("<meta http-equiv='refresh' content='180'>", unsafe_allow_html=True)

IST = ZoneInfo("Asia/Kolkata")

# ------------------------------------
# Market Timings
# ------------------------------------
MARKET_OPEN = dtime(9, 10)
MARKET_CLOSE = dtime(15, 30)

def market_is_open():
    now_ist = datetime.now(IST).time()
    return MARKET_OPEN <= now_ist <= MARKET_CLOSE

# ------------------------------------
# Fetch NSE Option Chain JSON
# ------------------------------------
def fetch_option_chain(symbol="NIFTY", retries=300):
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
            session.get("https://www.nseindia.com", headers=headers, timeout=60)
            time.sleep(random.uniform(5, 6))
            response = session.get(url, headers=headers, timeout=60)

            if not response.text.strip() or response.text.startswith("<"):
                raise ValueError("Invalid NSE response")
            # Some responses are HTML (blocked)
            if response.text.strip().startswith("<"):
                raise ValueError("Received HTML instead of JSON (likely blocked)")

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
            df["Timestamp"] = datetime.now(IST).isoformat()
            return df
        except Exception as e:
            st.warning(f"Attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(2)
    st.error("❌ Failed to fetch data after retries")
    return pd.DataFrame()

def sanitize_row_for_json(row: dict) -> dict:
    """
    Replace NaN with None and convert numpy scalar types to native Python types.
    """
    sanitized = {}
    for k, v in row.items():
        # pandas uses numpy NaN, None, or python types
        if pd.isna(v):
            sanitized[k] = None
            continue
        # convert numpy scalar -> native
        if isinstance(v, (np.integer,)):
            sanitized[k] = int(v)
        elif isinstance(v, (np.floating,)):
            # make sure not to send inf/-inf (JSON invalid) — map to None
            if np.isfinite(v):
                sanitized[k] = float(v)
            else:
                sanitized[k] = None
        elif isinstance(v, (np.bool_ , bool)):
            sanitized[k] = bool(v)
        else:
            # keep strings, datetimes etc.
            sanitized[k] = v
    return sanitized

# ------------------------------------
# Supabase Integration
# ------------------------------------
def save_to_supabase(df, symbol):
    if df is None or df.empty:
        st.info("No rows to save to Supabase.")
        return
        
    try:
        # Ensure df columns exist — coerce to expected names
        records = []
        for _, r in df.iterrows():
            rec = {
                "symbol": symbol,
                "expiry": r.get("Expiry"),
                "strike_price": r.get("StrikePrice"),
                "ce_oi": r.get("CE_OI"),
                "ce_change_oi": r.get("CE_ChangeOI"),
                "ce_ltp": r.get("CE_LTP"),
                "pe_oi": r.get("PE_OI"),
                "pe_change_oi": r.get("PE_ChangeOI"),
                "pe_ltp": r.get("PE_LTP"),
                "underlying": r.get("Underlying"),
                "timestamp": r.get("Timestamp"),
            }
            records.append(sanitize_row_for_json(rec))

            # Supabase expects a list of dicts (JSON serializable)
        # Insert in chunks to avoid huge payloads (optional)
        chunk_size = 500
        for i in range(0, len(records), chunk_size):
            chunk = records[i : i + chunk_size]
            res = supabase.table("option_chain_data").insert(chunk).execute()
            # basic error handling if supabase returns error
            if hasattr(res, "status_code") and res.status_code >= 400:
                st.error(f"Supabase returned error: {res}")  # keep simple
                return

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

def estimate_range(df):
    call_strikes = df.loc[df["CE_OI"].nlargest(3).index, "StrikePrice"].tolist()
    put_strikes = df.loc[df["PE_OI"].nlargest(3).index, "StrikePrice"].tolist()
    return min(put_strikes), max(call_strikes)

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
# Streamlit UI Logic
# ------------------------------------
symbol = st.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

if not market_is_open():
    st.warning("⏳ Market Closed (9:15–3:30 updates only)")
else:
    df = fetch_option_chain(symbol)
    # -------------------------
    # Expiry selection & filtering
    # -------------------------
    # Replace your expiry selection/filter block with this safer approach:

    if not df is None and not df.empty:
        save_to_supabase(df, symbol)
    
        # Ensure Expiry column is parsed as datetime (some records may already be strings)
        df["Expiry_dt"] = pd.to_datetime(df["Expiry"], errors="coerce")
        expiry_sorted = sorted(df["Expiry_dt"].dropna().unique())
        expiry_options = [d.strftime("%d-%b-%Y") for d in expiry_sorted[:6]]
        expiry_selected = st.selectbox("Select Expiry", expiry_options)
    
        # Filter by the parsed expiry datetime
        selected_dt = datetime.strptime(expiry_selected, "%d-%b-%Y").date()
        df = df[df["Expiry_dt"].dt.date == selected_dt].copy()

        
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

        pcr = compute_pcr(df)
        max_pain = compute_max_pain(df)
        sentiment = compute_sentiment(df)
        low, high = estimate_range(df)

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

        st.success(f"✅ Updated at {datetime.now(IST).strftime('%H:%M:%S')}")
    else:
        st.error("⚠️ Could not fetch live data")
