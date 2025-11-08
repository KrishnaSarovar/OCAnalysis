<<<<<<< HEAD
# import streamlit as st
# import pandas as pd
# import requests
# import os
# import time
# from datetime import datetime
# import plotly.express as px
# import numpy as np

# st.set_page_config(page_title="NSE Option Chain Intelligence", layout="wide")

# # ------------------------------------
# # Fetch NSE Option Chain JSON
# # ------------------------------------
# @st.cache_data(ttl=300)  # cache for 5 minutes
# def fetch_option_chain(symbol="NIFTY"):
#     url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Referer": f"https://www.nseindia.com/option-chain?symbol={symbol}",
#     }

#     session = requests.Session()
#     session.get("https://www.nseindia.com", headers=headers, timeout=10)
#     r = session.get(url, headers=headers, timeout=10)
#     data = r.json()

#     records = data.get("records", {}).get("data", [])
#     rows = []
#     for record in records:
#         strike = record.get("strikePrice")
#         expiry = record.get("expiryDate")
#         ce = record.get("CE", {})
#         pe = record.get("PE", {})

#         rows.append({
#             "Expiry": expiry,
#             "StrikePrice": strike,
#             "CE_OI": ce.get("openInterest"),
#             "CE_ChangeOI": ce.get("changeinOpenInterest"),
#             "CE_LTP": ce.get("lastPrice"),
#             "PE_OI": pe.get("openInterest"),
#             "PE_ChangeOI": pe.get("changeinOpenInterest"),
#             "PE_LTP": pe.get("lastPrice"),
#         })

#     df = pd.DataFrame(rows)
#     df = df.dropna(subset=["StrikePrice"])
#     df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     return df


# # ------------------------------------
# # Save tick data
# # ------------------------------------
# def save_tick(df, symbol):
#     today = datetime.now().strftime("%Y-%m-%d")
#     folder = os.path.join("data", today)
#     os.makedirs(folder, exist_ok=True)

#     filename = os.path.join(folder, f"{symbol}_ticks.xlsx")

#     if os.path.exists(filename):
#         old = pd.read_excel(filename)
#         new = pd.concat([old, df], ignore_index=True)
#     else:
#         new = df

#     new.to_excel(filename, index=False)


# # ------------------------------------
# # Helper Functions
# # ------------------------------------
# def interpret_signal(change_oi, ltp_change):
#     if change_oi > 0 and ltp_change > 0:
#         return "🟢 Long Build-up"
#     elif change_oi > 0 and ltp_change < 0:
#         return "🔴 Short Build-up"
#     elif change_oi < 0 and ltp_change > 0:
#         return "🟡 Short Covering"
#     elif change_oi < 0 and ltp_change < 0:
#         return "🔵 Long Unwinding"
#     else:
#         return "⚪ Neutral"


# def compute_pcr(df):
#     total_put_oi = df["PE_OI"].sum()
#     total_call_oi = df["CE_OI"].sum()
#     return round(total_put_oi / total_call_oi, 2) if total_call_oi else 0


# def compute_max_pain(df):
#     strikes = df["StrikePrice"].unique()
#     pain = {}
#     for strike in strikes:
#         ce_loss = ((strike - df["StrikePrice"]).clip(lower=0) * df["CE_OI"]).sum()
#         pe_loss = ((df["StrikePrice"] - strike).clip(lower=0) * df["PE_OI"]).sum()
#         pain[strike] = ce_loss + pe_loss
#     min_pain_strike = min(pain, key=pain.get)
#     return min_pain_strike


# def compute_sentiment(df):
#     ce_pressure = df["CE_ChangeOI"].sum()
#     pe_pressure = df["PE_ChangeOI"].sum()
#     if pe_pressure > ce_pressure * 1.2:
#         return "🟢 Bullish Bias"
#     elif ce_pressure > pe_pressure * 1.2:
#         return "🔴 Bearish Bias"
#     else:
#         return "⚪ Neutral"


# # ------------------------------------
# # Streamlit UI
# # ------------------------------------
# st.title("📊 NSE Option Chain Intelligence Dashboard")
# st.caption("Live Option Chain Tracker with Alerts, PCR, Max Pain, and OI Insights")

# symbol = st.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
# st.info("Fetching data every 5 minutes automatically.")

# df = fetch_option_chain(symbol)
# if df is not None and not df.empty:
#     save_tick(df, symbol)

#     expiry_selected = st.selectbox("Select Expiry", sorted(df["Expiry"].unique()))
#     df = df[df["Expiry"] == expiry_selected].copy()

#     df["CE_Signal"] = df.apply(lambda x: interpret_signal(x["CE_ChangeOI"], x["CE_LTP"]), axis=1)
#     df["PE_Signal"] = df.apply(lambda x: interpret_signal(x["PE_ChangeOI"], x["PE_LTP"]), axis=1)

#     # Identify Active and Neutral
#     active_df = df[
#         (abs(df["CE_ChangeOI"]) > df["CE_ChangeOI"].mean()) | (abs(df["PE_ChangeOI"]) > df["PE_ChangeOI"].mean())
#     ]
#     neutral_df = df.drop(active_df.index)

#     st.subheader(f"🔥 Active Strike Prices — {symbol} ({expiry_selected})")
#     st.dataframe(active_df, use_container_width=True)

#     with st.expander("⚪ Neutral Strikes"):
#         st.dataframe(neutral_df, use_container_width=True)

#     # OI Change Charts
#     c1, c2 = st.columns(2)
#     with c1:
#         st.subheader("Call OI Change (CE)")
#         fig1 = px.bar(active_df, x="StrikePrice", y="CE_ChangeOI", color="CE_Signal", title="Call Side Activity")
#         st.plotly_chart(fig1, use_container_width=True)

#     with c2:
#         st.subheader("Put OI Change (PE)")
#         fig2 = px.bar(active_df, x="StrikePrice", y="PE_ChangeOI", color="PE_Signal", title="Put Side Activity")
#         st.plotly_chart(fig2, use_container_width=True)

#     # Metrics
#     pcr = compute_pcr(df)
#     max_pain = compute_max_pain(df)
#     sentiment = compute_sentiment(df)

#     st.markdown("### 📈 Market Metrics")
#     col1, col2, col3 = st.columns(3)
#     col1.metric("PCR (Put/Call Ratio)", pcr)
#     col2.metric("Max Pain Strike", max_pain)
#     col3.metric("AI Sentiment", sentiment)

#     # Alerts
#     alerts = df[
#         (abs(df["CE_ChangeOI"]) > df["CE_OI"].mean() * 0.1) | (abs(df["PE_ChangeOI"]) > df["PE_OI"].mean() * 0.1)
#     ]
#     if not alerts.empty:
#         st.warning("🚨 Significant OI Change Detected!")
#         st.dataframe(alerts[["StrikePrice", "CE_ChangeOI", "PE_ChangeOI", "CE_LTP", "PE_LTP"]])

#     # Cumulative OI trend (top 10 active)
#     top10 = df.nlargest(10, ["CE_ChangeOI", "PE_ChangeOI"])
#     fig3 = px.line(top10, x="StrikePrice", y=["CE_ChangeOI", "PE_ChangeOI"], markers=True, title="Cumulative OI Change (Top 10)")
#     st.plotly_chart(fig3, use_container_width=True)

#     # Save summary at end of day
#     today = datetime.now().strftime("%H:%M:%S")
#     st.success(f"✅ Data refreshed successfully at {today}")
# else:
#     st.error("Failed to fetch data. Please try again later.")


# import streamlit as st
# import pandas as pd
# import requests
# import os
# import time
# from datetime import datetime
# import plotly.express as px
# import numpy as np

# st.set_page_config(page_title="NSE Option Chain Intelligence", layout="wide")

# # ------------------------------------
# # Fetch NSE Option Chain JSON
# # ------------------------------------
# @st.cache_data(ttl=300)  # cache for 5 minutes
# def fetch_option_chain(symbol="NIFTY"):
#     url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Referer": f"https://www.nseindia.com/option-chain?symbol={symbol}",
#     }

#     session = requests.Session()
#     session.get("https://www.nseindia.com", headers=headers, timeout=10)
#     r = session.get(url, headers=headers, timeout=10)
#     data = r.json()

#     records = data.get("records", {}).get("data", [])
#     rows = []
#     for record in records:
#         strike = record.get("strikePrice")
#         expiry = record.get("expiryDate")
#         ce = record.get("CE", {})
#         pe = record.get("PE", {})

#         rows.append({
#             "Expiry": expiry,
#             "StrikePrice": strike,
#             "CE_OI": ce.get("openInterest"),
#             "CE_ChangeOI": ce.get("changeinOpenInterest"),
#             "CE_LTP": ce.get("lastPrice"),
#             "PE_OI": pe.get("openInterest"),
#             "PE_ChangeOI": pe.get("changeinOpenInterest"),
#             "PE_LTP": pe.get("lastPrice"),
#         })

#     df = pd.DataFrame(rows)
#     df = df.dropna(subset=["StrikePrice"])
#     df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     return df


# # ------------------------------------
# # Save tick data
# # ------------------------------------
# def save_tick(df, symbol):
#     today = datetime.now().strftime("%Y-%m-%d")
#     folder = os.path.join("data", today)
#     os.makedirs(folder, exist_ok=True)

#     filename = os.path.join(folder, f"{symbol}_ticks.xlsx")

#     if os.path.exists(filename):
#         old = pd.read_excel(filename)
#         new = pd.concat([old, df], ignore_index=True)
#     else:
#         new = df

#     new.to_excel(filename, index=False)


# # ------------------------------------
# # Helper Functions
# # ------------------------------------
# def interpret_whale_activity(change_oi, ltp, option_type="CE"):
#     """
#     Detect buying/writing for Calls (CE) or Puts (PE)
#     """
#     if option_type == "CE":
#         if change_oi > 0 and ltp > 0:
#             return "🟢 Call Buying"
#         elif change_oi > 0 and ltp < 0:
#             return "🔴 Call Writing"
#         elif change_oi < 0 and ltp > 0:
#             return "🟡 Call Writing Unwinding"
#         elif change_oi < 0 and ltp < 0:
#             return "🔵 Call Selling"
#     else:  # PE
#         if change_oi > 0 and ltp < 0:
#             return "🟢 Put Buying"
#         elif change_oi > 0 and ltp > 0:
#             return "🔴 Put Writing"
#         elif change_oi < 0 and ltp < 0:
#             return "🟡 Put Writing Unwinding"
#         elif change_oi < 0 and ltp > 0:
#             return "🔵 Put Selling"
#     return "⚪ Neutral"


# def compute_pcr(df):
#     total_put_oi = df["PE_OI"].sum()
#     total_call_oi = df["CE_OI"].sum()
#     return round(total_put_oi / total_call_oi, 2) if total_call_oi else 0


# def compute_max_pain(df):
#     strikes = df["StrikePrice"].unique()
#     pain = {}
#     for strike in strikes:
#         ce_loss = ((strike - df["StrikePrice"]).clip(lower=0) * df["CE_OI"]).sum()
#         pe_loss = ((df["StrikePrice"] - strike).clip(lower=0) * df["PE_OI"]).sum()
#         pain[strike] = ce_loss + pe_loss
#     min_pain_strike = min(pain, key=pain.get)
#     return min_pain_strike


# def compute_sentiment(df):
#     ce_pressure = df["CE_ChangeOI"].sum()
#     pe_pressure = df["PE_ChangeOI"].sum()
#     if pe_pressure > ce_pressure * 1.2:
#         return "🟢 Bullish Bias"
#     elif ce_pressure > pe_pressure * 1.2:
#         return "🔴 Bearish Bias"
#     else:
#         return "⚪ Neutral"
    



# # ------------------------------------
# # Streamlit UI
# # ------------------------------------
# st.title("📊 NSE Option Chain Intelligence Dashboard")
# st.caption("Live Option Chain Tracker with Alerts, PCR, Max Pain, and OI Insights")

# symbol = st.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
# st.info("Fetching data every 5 minutes automatically.")

# df = fetch_option_chain(symbol)
# if df is not None and not df.empty:
#     save_tick(df, symbol)

#     expiry_selected = st.selectbox("Select Expiry", sorted(df["Expiry"].unique()))
#     df = df[df["Expiry"] == expiry_selected].copy()

#     df["CE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["CE_ChangeOI"], x["CE_LTP"], "CE"), axis=1)
#     df["PE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["PE_ChangeOI"], x["PE_LTP"], "PE"), axis=1)


#     threshold_multiplier = 1.5
#     active_df = df[
#         (abs(df["CE_ChangeOI"]) > df["CE_ChangeOI"].mean() * threshold_multiplier) |
#         (abs(df["PE_ChangeOI"]) > df["PE_ChangeOI"].mean() * threshold_multiplier)
#     ]
#     neutral_df = df.drop(active_df.index)

#     st.subheader(f"🔥 Active Strike Prices — {symbol} ({expiry_selected})")
#     st.dataframe(active_df, use_container_width=True)

#     with st.expander("⚪ Neutral Strikes"):
#         st.dataframe(neutral_df, use_container_width=True)

#     # OI Change Charts
#     c1, c2 = st.columns(2)
#     with c1:
#         st.subheader("Call OI Change (CE)")
#         fig1 = px.bar(active_df, x="StrikePrice", y="CE_ChangeOI", color="CE_Signal", title="Call Side Activity")
#         st.plotly_chart(fig1, use_container_width=True)

#     with c2:
#         st.subheader("Put OI Change (PE)")
#         fig2 = px.bar(active_df, x="StrikePrice", y="PE_ChangeOI", color="PE_Signal", title="Put Side Activity")
#         st.plotly_chart(fig2, use_container_width=True)

#     fig1 = px.bar(active_df, x="StrikePrice", y="CE_ChangeOI", color="CE_Signal",
#               title="Call Side Activity (Buying vs Writing)")
#     st.plotly_chart(fig1, use_container_width=True)

#     fig2 = px.bar(active_df, x="StrikePrice", y="PE_ChangeOI", color="PE_Signal",
#                 title="Put Side Activity (Buying vs Writing)")
#     st.plotly_chart(fig2, use_container_width=True)

#     # Metrics
#     pcr = compute_pcr(df)
#     max_pain = compute_max_pain(df)
#     sentiment = compute_sentiment(df)

#     st.markdown("### 📈 Market Metrics")
#     col1, col2, col3 = st.columns(3)
#     col1.metric("PCR (Put/Call Ratio)", pcr)
#     col2.metric("Max Pain Strike", max_pain)
#     col3.metric("AI Sentiment", sentiment)

#     # Alerts
#     alerts = df[
#         (abs(df["CE_ChangeOI"]) > df["CE_OI"].mean() * 0.1) | (abs(df["PE_ChangeOI"]) > df["PE_OI"].mean() * 0.1)
#     ]
#     if not alerts.empty:
#         st.warning("🚨 Significant OI Change Detected!")
#         st.dataframe(alerts[["StrikePrice", "CE_ChangeOI", "PE_ChangeOI", "CE_LTP", "PE_LTP"]])

#     # Cumulative OI trend (top 10 active)
#     top10 = df.nlargest(10, ["CE_ChangeOI", "PE_ChangeOI"])
#     fig3 = px.line(top10, x="StrikePrice", y=["CE_ChangeOI", "PE_ChangeOI"], markers=True, title="Cumulative OI Change (Top 10)")
#     st.plotly_chart(fig3, use_container_width=True)

#     # Save summary at end of day
#     today = datetime.now().strftime("%H:%M:%S")
#     st.success(f"✅ Data refreshed successfully at {today}")
# else:
#     st.error("Failed to fetch data. Please try again later.")

# import streamlit as st
# import pandas as pd
# import requests
# import os
# from datetime import datetime, time as dtime
# import plotly.express as px
# import numpy as np
# import time
# import threading

# def background_fetch(symbol="NIFTY"):
#     while True:
#         try:
#             df = fetch_option_chain(symbol)
#             if not df.empty:
#                 save_tick(df, symbol)
#                 print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Tick saved for {symbol}")
#         except Exception as e:
#             print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Error in background fetch: {e}")
#         time.sleep(300)  # Wait 5 minutes before next fetch

# # Start background thread
# threading.Thread(target=background_fetch, args=("NIFTY",), daemon=True).start()

# st.set_page_config(page_title="📊 NSE Option Chain Intelligence", layout="wide")
# st_autorefresh = st.experimental_rerun if hasattr(st, 'experimental_rerun') else None
# st_autorefresh = st_autorefresh or st.experimental_rerun  # Fallback for older versions

# st_autorefresh(interval=5 * 60 * 1000, key="data_refresh")


# # ------------------------------------
# # Market Timings
# # ------------------------------------
# MARKET_OPEN = dtime(9, 10)
# MARKET_CLOSE = dtime(15, 30)


# def market_is_open():
#     now = datetime.now().time()
#     return MARKET_OPEN <= now <= MARKET_CLOSE


# # ------------------------------------
# # Fetch NSE Option Chain JSON
# # ------------------------------------
# @st.cache_data(ttl=300)
# def fetch_option_chain(symbol="NIFTY"):
#     url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Referer": f"https://www.nseindia.com/option-chain?symbol={symbol}",
#     }

#     session = requests.Session()
#     session.get("https://www.nseindia.com", headers=headers, timeout=10)
#     r = session.get(url, headers=headers, timeout=10)
#     data = r.json()

#     records = data.get("records", {}).get("data", [])
#     rows = []
#     for record in records:
#         strike = record.get("strikePrice")
#         expiry = record.get("expiryDate")
#         ce = record.get("CE", {})
#         pe = record.get("PE", {})

#         rows.append({
#             "Expiry": expiry,
#             "StrikePrice": strike,
#             "CE_OI": ce.get("openInterest"),
#             "CE_ChangeOI": ce.get("changeinOpenInterest"),
#             "CE_LTP": ce.get("lastPrice"),
#             "PE_OI": pe.get("openInterest"),
#             "PE_ChangeOI": pe.get("changeinOpenInterest"),
#             "PE_LTP": pe.get("lastPrice"),
#         })

#     df = pd.DataFrame(rows)
#     df = df.dropna(subset=["StrikePrice"])
#     df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     return df


# # ------------------------------------
# # Save tick data
# # ------------------------------------
# def save_tick(df, symbol):
#     today = datetime.now().strftime("%Y-%m-%d")
#     folder = os.path.join("data", today)
#     os.makedirs(folder, exist_ok=True)
#     filename = os.path.join(folder, f"{symbol}_ticks.xlsx")

#     # Add timestamp column if missing
#     if "Timestamp" not in df.columns:
#         df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     if os.path.exists(filename):
#         old = pd.read_excel(filename)
#         combined = pd.concat([old, df]).drop_duplicates(subset=["Timestamp", "StrikePrice"], keep="last")
#     else:
#         combined = df

#     combined.to_excel(filename, index=False)


# # ------------------------------------
# # Helper Functions
# # ------------------------------------
# def interpret_whale_activity(change_oi, ltp, option_type="CE"):
#     if option_type == "CE":
#         if change_oi > 0 and ltp > 0:
#             return "🟢 Call Buying"
#         elif change_oi > 0 and ltp < 0:
#             return "🔴 Call Writing"
#         elif change_oi < 0 and ltp > 0:
#             return "🟡 Call Short Covering"
#         elif change_oi < 0 and ltp < 0:
#             return "🔵 Call Long Unwinding"
#     else:
#         if change_oi > 0 and ltp > 0:
#             return "🔴 Put Writing"
#         elif change_oi > 0 and ltp < 0:
#             return "🟢 Put Buying"
#         elif change_oi < 0 and ltp > 0:
#             return "🔵 Put Long Unwinding"
#         elif change_oi < 0 and ltp < 0:
#             return "🟡 Put Short Covering"
#     return "⚪ Neutral"


# def compute_pcr(df):
#     total_put_oi = df["PE_OI"].sum()
#     total_call_oi = df["CE_OI"].sum()
#     return round(total_put_oi / total_call_oi, 2) if total_call_oi else 0


# def compute_max_pain(df):
#     strikes = df["StrikePrice"].unique()
#     pain = {}
#     for strike in strikes:
#         ce_loss = ((strike - df["StrikePrice"]).clip(lower=0) * df["CE_OI"]).sum()
#         pe_loss = ((df["StrikePrice"] - strike).clip(lower=0) * df["PE_OI"]).sum()
#         pain[strike] = ce_loss + pe_loss
#     return min(pain, key=pain.get)


# def compute_sentiment(df):
#     ce_pressure = df["CE_ChangeOI"].sum()
#     pe_pressure = df["PE_ChangeOI"].sum()
#     if pe_pressure > ce_pressure * 1.2:
#         return "🟢 Bullish Bias"
#     elif ce_pressure > pe_pressure * 1.2:
#         return "🔴 Bearish Bias"
#     else:
#         return "⚪ Neutral"


# def estimate_range(df):
#     """Estimate support/resistance range based on OI clusters"""
#     call_strikes = df.loc[df["CE_OI"].nlargest(3).index, "StrikePrice"].tolist()
#     put_strikes = df.loc[df["PE_OI"].nlargest(3).index, "StrikePrice"].tolist()
#     return min(put_strikes), max(call_strikes)


# # ------------------------------------
# # Streamlit UI
# # ------------------------------------
# st.title("📊 NSE Option Chain Intelligence Dashboard")
# st.caption("Live Option Chain Tracker with Max Pain & Range Shift Analytics")

# if not market_is_open():
#     st.warning("⏳ Market Closed. Dashboard updates only during 9:15 AM – 3:30 PM IST.")
# else:
#     symbol = st.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
#     st.info("Fetching NSE data every 5 minutes automatically...")

#     df = fetch_option_chain(symbol)

#     if df is not None and not df.empty:
#         save_tick(df, symbol)

#         expiry_selected = st.selectbox("Select Expiry", sorted(df["Expiry"].unique()))
#         df = df[df["Expiry"] == expiry_selected].copy()

#         # Signals
#         df["CE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["CE_ChangeOI"], x["CE_LTP"], "CE"), axis=1)
#         df["PE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["PE_ChangeOI"], x["PE_LTP"], "PE"), axis=1)

#         # Active strikes
#         threshold_multiplier = 1.5
#         active_df = df[
#             (abs(df["CE_ChangeOI"]) > df["CE_ChangeOI"].mean() * threshold_multiplier)
#             | (abs(df["PE_ChangeOI"]) > df["PE_ChangeOI"].mean() * threshold_multiplier)
#         ]

#         neutral_df = df.drop(active_df.index)

#         st.subheader(f"🔥 Active Strike Prices — {symbol} ({expiry_selected})")
#         st.dataframe(active_df, use_container_width=True)

#         # Market metrics
#         pcr = compute_pcr(df)
#         max_pain = compute_max_pain(df)
#         sentiment = compute_sentiment(df)
#         low, high = estimate_range(df)

#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("PCR", pcr)
#         c2.metric("Max Pain", max_pain)
#         c3.metric("Range Low", low)
#         c4.metric("Range High", high)

#         st.markdown(f"**AI Sentiment:** {sentiment}")

#         # Visuals
#         c1, c2 = st.columns(2)
#         with c1:
#             fig1 = px.bar(active_df, x="StrikePrice", y="CE_ChangeOI", color="CE_Signal",
#                           title="Call OI Change (Buying vs Writing)")
#             st.plotly_chart(fig1, use_container_width=True)
#         with c2:
#             fig2 = px.bar(active_df, x="StrikePrice", y="PE_ChangeOI", color="PE_Signal",
#                           title="Put OI Change (Buying vs Writing)")
#             st.plotly_chart(fig2, use_container_width=True)

#         # Track Max Pain Shift
#         today = datetime.now().strftime("%Y-%m-%d")
#         hist_path = os.path.join("data", today, f"{symbol}_ticks.xlsx")
#         if os.path.exists(hist_path):
#             hist = pd.read_excel(hist_path)
#             hist["MaxPain"] = hist.groupby("Timestamp").apply(lambda g: compute_max_pain(g)).reset_index(drop=True)
#             hist_pain = hist[["Timestamp", "MaxPain"]].drop_duplicates()

#             fig3 = px.line(hist_pain, x="Timestamp", y="MaxPain", markers=True,
#                            title="📈 Max Pain Point Shift Throughout Day")
#             st.plotly_chart(fig3, use_container_width=True)

#         # Range visualization
#         range_df = pd.DataFrame({"Type": ["Support", "Resistance"], "Strike": [low, high]})
#         fig4 = px.bar(range_df, x="Type", y="Strike", color="Type", text="Strike",
#                       title="📊 Estimated Market Range Shift")
#         st.plotly_chart(fig4, use_container_width=True)

#         st.success(f"✅ Updated at {datetime.now().strftime('%H:%M:%S')}")
#     else:
#         st.error("⚠️ Failed to fetch option chain data.")
# __________________________________________________________________________________________________________
# import streamlit as st
# import pandas as pd
# import requests
# import os
# from datetime import datetime, time as dtime
# import plotly.express as px
# import numpy as np
# import tempfile
# import shutil

# st.set_page_config(page_title="📊 NSE Option Chain Intelligence", layout="wide")

# # ------------------------------------
# # Auto-refresh every 5 minutes
# # ------------------------------------
# st.markdown("""
#     <meta http-equiv="refresh" content="300">
# """, unsafe_allow_html=True)
# # (300 sec = 5 min)


# # ------------------------------------
# # Market Timings
# # ------------------------------------
# MARKET_OPEN = dtime(9, 10)
# MARKET_CLOSE = dtime(15, 30)


# def market_is_open():
#     now = datetime.now().time()
#     return MARKET_OPEN <= now <= MARKET_CLOSE


# # ------------------------------------
# # Fetch NSE Option Chain JSON
# # ------------------------------------
# def fetch_option_chain(symbol="NIFTY"):
#     url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Referer": f"https://www.nseindia.com/option-chain?symbol={symbol}",
#     }

#     session = requests.Session()
#     session.get("https://www.nseindia.com", headers=headers, timeout=10)
#     r = session.get(url, headers=headers, timeout=10)
#     data = r.json()

#     records = data.get("records", {}).get("data", [])
#     rows = []
#     for record in records:
#         strike = record.get("strikePrice")
#         expiry = record.get("expiryDate")
#         ce = record.get("CE", {})
#         pe = record.get("PE", {})

#         rows.append({
#             "Expiry": expiry,
#             "StrikePrice": strike,
#             "CE_OI": ce.get("openInterest"),
#             "CE_ChangeOI": ce.get("changeinOpenInterest"),
#             "CE_LTP": ce.get("lastPrice"),
#             "PE_OI": pe.get("openInterest"),
#             "PE_ChangeOI": pe.get("changeinOpenInterest"),
#             "PE_LTP": pe.get("lastPrice"),
#         })

#     df = pd.DataFrame(rows)
#     df = df.dropna(subset=["StrikePrice"])
#     df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     return df


# # ------------------------------------
# # Save tick data
# # ------------------------------------
# def save_tick(df, symbol):
#     """Safely append today's tick data to Excel file without corruption."""
#     today = datetime.now().strftime("%Y-%m-%d")
#     folder = os.path.join("data", today)
#     os.makedirs(folder, exist_ok=True)
#     filename = os.path.join(folder, f"{symbol}_ticks.xlsx")

#     # Write safely to a temp file first
#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
#     temp_path = temp_file.name
#     temp_file.close()

#     try:
#         if os.path.exists(filename):
#             try:
#                 old = pd.read_excel(filename)
#                 new = pd.concat([old, df], ignore_index=True)
#             except Exception:
#                 # Fallback in case of read error (partial/corrupt file)
#                 st.warning("⚠️ Detected a partially written Excel file, creating a new one...")
#                 new = df
#         else:
#             new = df

#         new.to_excel(temp_path, index=False)

#         # Atomic replace (safe swap)
#         shutil.move(temp_path, filename)

#     except Exception as e:
#         st.error(f"❌ Error saving tick data: {e}")

#     finally:
#         # Clean up temp file if it exists
#         if os.path.exists(temp_path):
#             try:
#                 os.remove(temp_path)
#             except:
#                 pass

# # ------------------------------------
# # Helper Functions
# # ------------------------------------
# def interpret_whale_activity(change_oi, ltp, option_type="CE"):
#     if option_type == "CE":
#         if change_oi > 0 and ltp > 0:
#             return "🟢 Call Buying"
#         elif change_oi > 0 and ltp < 0:
#             return "🔴 Call Writing"
#         elif change_oi < 0 and ltp > 0:
#             return "🟡 Call Short Covering"
#         elif change_oi < 0 and ltp < 0:
#             return "🔵 Call Long Unwinding"
#     else:
#         if change_oi > 0 and ltp > 0:
#             return "🔴 Put Writing"
#         elif change_oi > 0 and ltp < 0:
#             return "🟢 Put Buying"
#         elif change_oi < 0 and ltp > 0:
#             return "🔵 Put Long Unwinding"
#         elif change_oi < 0 and ltp < 0:
#             return "🟡 Put Short Covering"
#     return "⚪ Neutral"


# def compute_pcr(df):
#     total_put_oi = df["PE_OI"].sum()
#     total_call_oi = df["CE_OI"].sum()
#     return round(total_put_oi / total_call_oi, 2) if total_call_oi else 0


# def compute_max_pain(df):
#     strikes = df["StrikePrice"].unique()
#     pain = {}
#     for strike in strikes:
#         ce_loss = ((strike - df["StrikePrice"]).clip(lower=0) * df["CE_OI"]).sum()
#         pe_loss = ((df["StrikePrice"] - strike).clip(lower=0) * df["PE_OI"]).sum()
#         pain[strike] = ce_loss + pe_loss
#     return min(pain, key=pain.get)


# def compute_sentiment(df):
#     ce_pressure = df["CE_ChangeOI"].sum()
#     pe_pressure = df["PE_ChangeOI"].sum()
#     if pe_pressure > ce_pressure * 1.2:
#         return "🟢 Bullish Bias"
#     elif ce_pressure > pe_pressure * 1.2:
#         return "🔴 Bearish Bias"
#     else:
#         return "⚪ Neutral"


# def estimate_range(df):
#     """Estimate support/resistance range based on OI clusters"""
#     call_strikes = df.loc[df["CE_OI"].nlargest(3).index, "StrikePrice"].tolist()
#     put_strikes = df.loc[df["PE_OI"].nlargest(3).index, "StrikePrice"].tolist()
#     return min(put_strikes), max(call_strikes)


# # ------------------------------------
# # Streamlit UI
# # ------------------------------------
# st.title("📊 NSE Option Chain Intelligence Dashboard")
# st.caption("Live Option Chain Tracker with Max Pain & Range Shift Analytics")

# symbol = st.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

# if not market_is_open():
#     st.warning("⏳ Market Closed. Dashboard updates only during 9:15 AM – 3:30 PM IST.")
# else:
#     st.info("🔄 Auto-refresh active: Data will update every 5 minutes.")

#     df = fetch_option_chain(symbol)

#     if df is not None and not df.empty:
#         save_tick(df, symbol)

#         expiry_selected = st.selectbox("Select Expiry", sorted(df["Expiry"].unique()))
#         df = df[df["Expiry"] == expiry_selected].copy()

#         # Signals
#         df["CE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["CE_ChangeOI"], x["CE_LTP"], "CE"), axis=1)
#         df["PE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["PE_ChangeOI"], x["PE_LTP"], "PE"), axis=1)

#         # Active strikes
#         threshold_multiplier = 1.5
#         active_df = df[
#             (abs(df["CE_ChangeOI"]) > df["CE_ChangeOI"].mean() * threshold_multiplier)
#             | (abs(df["PE_ChangeOI"]) > df["PE_ChangeOI"].mean() * threshold_multiplier)
#         ]

#         st.subheader(f"🔥 Active Strike Prices — {symbol} ({expiry_selected})")
#         st.dataframe(active_df, use_container_width=True)

#         # Market metrics
#         pcr = compute_pcr(df)
#         max_pain = compute_max_pain(df)
#         sentiment = compute_sentiment(df)
#         low, high = estimate_range(df)

#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("PCR", pcr)
#         c2.metric("Max Pain", max_pain)
#         c3.metric("Range Low", low)
#         c4.metric("Range High", high)
#         st.markdown(f"**AI Sentiment:** {sentiment}")

#         # Visuals
#         c1, c2 = st.columns(2)
#         with c1:
#             fig1 = px.bar(active_df, x="StrikePrice", y="CE_ChangeOI", color="CE_Signal",
#                           title="Call OI Change (Buying vs Writing)")
#             st.plotly_chart(fig1, use_container_width=True)
#         with c2:
#             fig2 = px.bar(active_df, x="StrikePrice", y="PE_ChangeOI", color="PE_Signal",
#                           title="Put OI Change (Buying vs Writing)")
#             st.plotly_chart(fig2, use_container_width=True)

#         # Track Max Pain Shift
#         today = datetime.now().strftime("%Y-%m-%d")
#         hist_path = os.path.join("data", today, f"{symbol}_ticks.xlsx")
#         if os.path.exists(hist_path):
#             hist = pd.read_excel(hist_path)
#             hist["MaxPain"] = hist.groupby("Timestamp").apply(lambda g: compute_max_pain(g)).reset_index(drop=True)
#             hist_pain = hist[["Timestamp", "MaxPain"]].drop_duplicates()

#             fig3 = px.line(hist_pain, x="Timestamp", y="MaxPain", markers=True,
#                            title="📈 Max Pain Point Shift Throughout Day")
#             st.plotly_chart(fig3, use_container_width=True)

#         st.success(f"✅ Updated at {datetime.now().strftime('%H:%M:%S')}")
#     else:
#         st.error("⚠️ Failed to fetch option chain data.")

# _________________________________________________________________________________________________________
# import streamlit as st
# import pandas as pd
# import requests
# import os
# from datetime import datetime, time as dtime, timedelta
# import plotly.express as px
# import numpy as np
# import tempfile
# import shutil

# st.set_page_config(page_title="📊 NSE Option Chain Intelligence", layout="wide")

# # ------------------------------------
# # Auto-refresh every 5 minutes
# # ------------------------------------
# st.markdown("<meta http-equiv='refresh' content='300'>", unsafe_allow_html=True)

# # ------------------------------------
# # Market Timings
# # ------------------------------------
# MARKET_OPEN = dtime(9, 10)
# MARKET_CLOSE = dtime(21, 30)


# def market_is_open():
#     now = datetime.now().time()
#     return MARKET_OPEN <= now <= MARKET_CLOSE


# # ------------------------------------
# # Fetch NSE Option Chain JSON
# # ------------------------------------
# def fetch_option_chain(symbol="NIFTY"):
#     url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Referer": f"https://www.nseindia.com/option-chain?symbol={symbol}",
#     }

#     session = requests.Session()
#     session.get("https://www.nseindia.com", headers=headers, timeout=10)
#     r = session.get(url, headers=headers, timeout=10)
#     data = r.json()

#     records = data.get("records", {}).get("data", [])
#     underlying_value = data.get("records", {}).get("underlyingValue", 0)

#     rows = []
#     for record in records:
#         strike = record.get("strikePrice")
#         expiry = record.get("expiryDate")
#         ce = record.get("CE", {})
#         pe = record.get("PE", {})

#         rows.append({
#             "Expiry": expiry,
#             "StrikePrice": strike,
#             "CE_OI": ce.get("openInterest"),
#             "CE_ChangeOI": ce.get("changeinOpenInterest"),
#             "CE_LTP": ce.get("lastPrice"),
#             "PE_OI": pe.get("openInterest"),
#             "PE_ChangeOI": pe.get("changeinOpenInterest"),
#             "PE_LTP": pe.get("lastPrice"),
#         })

#     df = pd.DataFrame(rows)
#     df = df.dropna(subset=["StrikePrice"])
#     df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     df["Underlying"] = underlying_value
#     return df


# # ------------------------------------
# # Save tick data safely
# # ------------------------------------
# def save_tick(df, symbol):
#     today = datetime.now().strftime("%Y-%m-%d")
#     folder = os.path.join("data", today)
#     os.makedirs(folder, exist_ok=True)
#     filename = os.path.join(folder, f"{symbol}_ticks.xlsx")

#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
#     temp_path = temp_file.name
#     temp_file.close()

#     try:
#         if os.path.exists(filename):
#             old = pd.read_excel(filename)
#             new = pd.concat([old, df], ignore_index=True)
#         else:
#             new = df

#         new.to_excel(temp_path, index=False)
#         shutil.move(temp_path, filename)

#     except Exception as e:
#         st.error(f"❌ Error saving tick data: {e}")


# # ------------------------------------
# # Helper Functions
# # ------------------------------------
# def interpret_whale_activity(change_oi, ltp, option_type="CE"):
#     if option_type == "CE":
#         if change_oi > 0 and ltp > 0:
#             return "🟢 Call Buying"
#         elif change_oi > 0 and ltp < 0:
#             return "🔴 Call Writing"
#         elif change_oi < 0 and ltp > 0:
#             return "🟡 Call Short Covering"
#         elif change_oi < 0 and ltp < 0:
#             return "🔵 Call Long Unwinding"
#     else:
#         if change_oi > 0 and ltp > 0:
#             return "🔴 Put Writing"
#         elif change_oi > 0 and ltp < 0:
#             return "🟢 Put Buying"
#         elif change_oi < 0 and ltp > 0:
#             return "🔵 Put Long Unwinding"
#         elif change_oi < 0 and ltp < 0:
#             return "🟡 Put Short Covering"
#     return "⚪ Neutral"


# def compute_pcr(df):
#     total_put_oi = df["PE_OI"].sum()
#     total_call_oi = df["CE_OI"].sum()
#     return round(total_put_oi / total_call_oi, 2) if total_call_oi else 0


# def compute_max_pain(df):
#     strikes = df["StrikePrice"].unique()
#     pain = {}
#     for strike in strikes:
#         ce_loss = ((strike - df["StrikePrice"]).clip(lower=0) * df["CE_OI"]).sum()
#         pe_loss = ((df["StrikePrice"] - strike).clip(lower=0) * df["PE_OI"]).sum()
#         pain[strike] = ce_loss + pe_loss
#     return min(pain, key=pain.get)


# def compute_sentiment(df):
#     ce_pressure = df["CE_ChangeOI"].sum()
#     pe_pressure = df["PE_ChangeOI"].sum()
#     if pe_pressure > ce_pressure * 1.2:
#         return "🟢 Bullish Bias"
#     elif ce_pressure > pe_pressure * 1.2:
#         return "🔴 Bearish Bias"
#     else:
#         return "⚪ Neutral"


# def estimate_range(df):
#     call_strikes = df.loc[df["CE_OI"].nlargest(3).index, "StrikePrice"].tolist()
#     put_strikes = df.loc[df["PE_OI"].nlargest(3).index, "StrikePrice"].tolist()
#     return min(put_strikes), max(call_strikes)


# # ------------------------------------
# # Time-based OI Distribution
# # ------------------------------------
# def compute_oi_distribution(hist, interval_minutes=30, strike_range=1000):
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

#     # Extract readable time windows
#     agg["StartTime"] = agg["TimeBin"].apply(lambda x: x.left.strftime("%H:%M") if pd.notnull(x) else "")
#     agg["EndTime"] = agg["TimeBin"].apply(lambda x: x.right.strftime("%H:%M") if pd.notnull(x) else "")

#     # Convert to string explicitly before concatenation
#     agg["Window"] = agg["StartTime"].astype(str) + "–" + agg["EndTime"].astype(str)

#     return agg, atm


# # ------------------------------------
# # Streamlit UI
# # ------------------------------------
# st.title("📊 NSE Option Chain Intelligence Dashboard")

# symbol = st.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

# if not market_is_open():
#     st.warning("⏳ Market Closed. Dashboard updates only during 9:15–3:30.")
# else:
#     st.info("🔄 Auto-refresh active (5 min)")

#     df = fetch_option_chain(symbol)
#     save_tick(df, symbol)

#     # ---- Expiry Sorting & Filter ----
#     expiry_sorted = sorted(pd.to_datetime(df["Expiry"].unique()))
#     expiry_selected = st.selectbox(
#         "Select Expiry", [d.strftime("%d-%b-%Y") for d in expiry_sorted[:5]]
#     )

#     df = df[df["Expiry"] == pd.to_datetime(expiry_selected).strftime("%d-%b-%Y")]

#     # ---- Strike Range Filter ----
#     atm = round(df["Underlying"].iloc[-1] / 50) * 50
#     df = df[(df["StrikePrice"] >= atm - 1500) & (df["StrikePrice"] <= atm + 1500)]

#     # ---- Signals ----
#     df["CE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["CE_ChangeOI"], x["CE_LTP"], "CE"), axis=1)
#     df["PE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["PE_ChangeOI"], x["PE_LTP"], "PE"), axis=1)

#     # ---- Metrics ----
#     pcr = compute_pcr(df)
#     max_pain = compute_max_pain(df)
#     sentiment = compute_sentiment(df)
#     low, high = estimate_range(df)

#     c1, c2, c3, c4 = st.columns(4)
#     c1.metric("PCR", pcr)
#     c2.metric("Max Pain", max_pain)
#     c3.metric("Range Low", low)
#     c4.metric("Range High", high)
#     st.markdown(f"**AI Sentiment:** {sentiment}")

#     # ---- Charts ----
#     c1, c2 = st.columns(2)
#     with c1:
#         fig1 = px.bar(df, x="StrikePrice", y="CE_ChangeOI", color="CE_Signal",
#                       title="Call OI Change (Buying vs Writing)")
#         st.plotly_chart(fig1, use_container_width=True)
#     with c2:
#         fig2 = px.bar(df, x="StrikePrice", y="PE_ChangeOI", color="PE_Signal",
#                       title="Put OI Change (Buying vs Writing)")
#         st.plotly_chart(fig2, use_container_width=True)

#     # ---- OI Distribution by Time ----
#     today = datetime.now().strftime("%Y-%m-%d")
#     hist_path = os.path.join("data", today, f"{symbol}_ticks.xlsx")
#     if os.path.exists(hist_path):
#         hist = pd.read_excel(hist_path)
#         agg, atm_val = compute_oi_distribution(hist, interval_minutes=30, strike_range=1000)

#         st.subheader(f"🕒 OI Build-up Distribution Around ATM ±1000 ({symbol})")
#         fig3 = px.bar(
#             agg,
#             x="Window",
#             y=["CE_ChangeOI", "PE_ChangeOI"],
#             barmode="group",
#             title="OI Changes in 30-min Buckets",
#         )
#         st.plotly_chart(fig3, use_container_width=True)

#         st.dataframe(agg, use_container_width=True)

#     st.success(f"✅ Updated at {datetime.now().strftime('%H:%M:%S')}")
# _______________________________________________________________________________________________________________________________
# import streamlit as st
# import pandas as pd
# import requests
# import os
# from datetime import datetime, time as dtime, timedelta
# import plotly.express as px
# import numpy as np
# import tempfile
# import shutil
# import time
# import random

# from supabase import create_client, Client

# SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://dnsjlwzipsqzfhztassn.supabase.co")
# SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuc2psd3ppcHNxemZoenRhc3NuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE1NjkyNDAsImV4cCI6MjA3NzE0NTI0MH0.TM4VN59lVljI1RC1V09PW1P5t3HDEqcVqYYD88UOtig")

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# st.set_page_config(page_title="📊 NSE Option Chain Intelligence", layout="wide")

# # ------------------------------------
# # Auto-refresh every 5 minutes
# # ------------------------------------
# st.markdown("<meta http-equiv='refresh' content='300'>", unsafe_allow_html=True)

# # ------------------------------------
# # Market Timings
# # ------------------------------------
# MARKET_OPEN = dtime(9, 10)
# MARKET_CLOSE = dtime(22, 00)


# def market_is_open():
#     now = datetime.now().time()
#     return MARKET_OPEN <= now <= MARKET_CLOSE


# # ------------------------------------
# # Fetch NSE Option Chain JSON
# # ------------------------------------
# def fetch_option_chain(symbol="NIFTY", retries=3):
#     """Fetch NSE Option Chain data with retry and error handling."""
#     url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
#     headers = {
#         "User-Agent": (
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#             "AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/120.0 Safari/537.36"
#         ),
#         "Accept": "application/json, text/plain, */*",
#         "Referer": f"https://www.nseindia.com/option-chain?symbol={symbol}",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Connection": "keep-alive",
#     }

#     for attempt in range(retries):
#         try:
#             session = requests.Session()
#             # Important: get cookies first
#             session.get("https://www.nseindia.com", headers=headers, timeout=60)
#             time.sleep(random.uniform(5, 6))  # polite delay

#             response = session.get(url, headers=headers, timeout=60)

#             # Handle blank or invalid response
#             if not response.text.strip():
#                 raise ValueError("Empty response from NSE")

#             # Some responses are HTML (blocked)
#             if response.text.strip().startswith("<"):
#                 raise ValueError("Received HTML instead of JSON (likely blocked)")

#             data = response.json()  # Safe to parse JSON now

#             records = data.get("records", {}).get("data", [])
#             underlying_value = data.get("records", {}).get("underlyingValue", 0)

#             rows = []
#             for record in records:
#                 strike = record.get("strikePrice")
#                 expiry = record.get("expiryDate")
#                 ce = record.get("CE", {})
#                 pe = record.get("PE", {})

#                 rows.append({
#                     "Expiry": expiry,
#                     "StrikePrice": strike,
#                     "CE_OI": ce.get("openInterest"),
#                     "CE_ChangeOI": ce.get("changeinOpenInterest"),
#                     "CE_LTP": ce.get("lastPrice"),
#                     "PE_OI": pe.get("openInterest"),
#                     "PE_ChangeOI": pe.get("changeinOpenInterest"),
#                     "PE_LTP": pe.get("lastPrice"),
#                 })

#             df = pd.DataFrame(rows).dropna(subset=["StrikePrice"])
#             df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             df["Underlying"] = underlying_value

#             return df

#         except Exception as e:
#             st.warning(f"⚠️ Attempt {attempt+1}/{retries} failed: {e}")
#             time.sleep(2)

#     st.error("❌ Failed to fetch NSE Option Chain after multiple attempts.")
#     return pd.DataFrame()

# # ------------------------------------
# # Save tick data safely
# # ------------------------------------
# def save_tick(df, symbol):
#     today = datetime.now().strftime("%Y-%m-%d")
#     folder = os.path.join("data", today)
#     os.makedirs(folder, exist_ok=True)
#     filename = os.path.join(folder, f"{symbol}_ticks.xlsx")

#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
#     temp_path = temp_file.name
#     temp_file.close()

#     try:
#         if os.path.exists(filename):
#             old = pd.read_excel(filename)
#             new = pd.concat([old, df], ignore_index=True)
#         else:
#             new = df

#         new.to_excel(temp_path, index=False)
#         shutil.move(temp_path, filename)

#     except Exception as e:
#         st.error(f"❌ Error saving tick data: {e}")

# def save_tick_to_supabase(df, symbol):
#     """Save option chain snapshot to Supabase."""
#     try:
#         records = []
#         for _, row in df.iterrows():
#             records.append({
#                 "symbol": symbol,
#                 "expiry": row["Expiry"],
#                 "strike_price": row["StrikePrice"],
#                 "ce_oi": row["CE_OI"],
#                 "ce_change_oi": row["CE_ChangeOI"],
#                 "ce_ltp": row["CE_LTP"],
#                 "pe_oi": row["PE_OI"],
#                 "pe_change_oi": row["PE_ChangeOI"],
#                 "pe_ltp": row["PE_LTP"],
#                 "underlying": row["Underlying"],
#                 "timestamp": row["Timestamp"]
#             })

#         # Bulk insert into Supabase
#         supabase.table("option_chain_data").insert(records).execute()
#         st.success(f"✅ {len(records)} rows uploaded to Supabase")

#     except Exception as e:
#         st.error(f"❌ Failed to upload to Supabase: {e}")



# # ------------------------------------
# # Helper Functions
# # ------------------------------------
# def interpret_whale_activity(change_oi, ltp, option_type="CE"):
#     if option_type == "CE":
#         if change_oi > 0 and ltp > 0:
#             return "🟢 Call Buying"
#         elif change_oi > 0 and ltp < 0:
#             return "🔴 Call Writing"
#         elif change_oi < 0 and ltp > 0:
#             return "🟡 Call Short Covering"
#         elif change_oi < 0 and ltp < 0:
#             return "🔵 Call Long Unwinding"
#     else:
#         if change_oi > 0 and ltp > 0:
#             return "🔴 Put Writing"
#         elif change_oi > 0 and ltp < 0:
#             return "🟢 Put Buying"
#         elif change_oi < 0 and ltp > 0:
#             return "🔵 Put Long Unwinding"
#         elif change_oi < 0 and ltp < 0:
#             return "🟡 Put Short Covering"
#     return "⚪ Neutral"


# def compute_pcr(df):
#     total_put_oi = df["PE_OI"].sum()
#     total_call_oi = df["CE_OI"].sum()
#     return round(total_put_oi / total_call_oi, 2) if total_call_oi else 0


# def compute_max_pain(df):
#     strikes = df["StrikePrice"].unique()
#     pain = {}
#     for strike in strikes:
#         ce_loss = ((strike - df["StrikePrice"]).clip(lower=0) * df["CE_OI"]).sum()
#         pe_loss = ((df["StrikePrice"] - strike).clip(lower=0) * df["PE_OI"]).sum()
#         pain[strike] = ce_loss + pe_loss
#     return min(pain, key=pain.get)


# def compute_sentiment(df):
#     ce_pressure = df["CE_ChangeOI"].sum()
#     pe_pressure = df["PE_ChangeOI"].sum()
#     if pe_pressure > ce_pressure * 1.2:
#         return "🟢 Bullish Bias"
#     elif ce_pressure > pe_pressure * 1.2:
#         return "🔴 Bearish Bias"
#     else:
#         return "⚪ Neutral"


# def estimate_range(df):
#     call_strikes = df.loc[df["CE_OI"].nlargest(3).index, "StrikePrice"].tolist()
#     put_strikes = df.loc[df["PE_OI"].nlargest(3).index, "StrikePrice"].tolist()
#     return min(put_strikes), max(call_strikes)

# def load_history(symbol):
#     res = supabase.table("option_chain_data").select("*").eq("symbol", symbol).execute()
#     return pd.DataFrame(res.data)



# # ------------------------------------
# # Time-based OI Distribution
# # ------------------------------------
# # def compute_oi_distribution(hist, interval_minutes=30, strike_range=500):
# #     hist["Timestamp"] = pd.to_datetime(hist["Timestamp"])
# #     latest_underlying = hist["Underlying"].iloc[-1]
# #     atm = round(latest_underlying / 50) * 50

# #     # Filter within ATM ± range
# #     hist = hist[(hist["StrikePrice"] >= atm - strike_range) &
# #                 (hist["StrikePrice"] <= atm + strike_range)]

# #     # Create time buckets
# #     start_time = hist["Timestamp"].min().floor("T")
# #     end_time = hist["Timestamp"].max().ceil("T")
# #     time_bins = pd.date_range(start_time, end_time, freq=f"{interval_minutes}min")

# #     hist["TimeBin"] = pd.cut(hist["Timestamp"], bins=time_bins)

# #     agg = hist.groupby("TimeBin")[["CE_ChangeOI", "PE_ChangeOI"]].sum().reset_index()

# #     agg["StartTime"] = agg["TimeBin"].apply(lambda x: x.left.strftime("%H:%M") if pd.notnull(x) else "")
# #     agg["EndTime"] = agg["TimeBin"].apply(lambda x: x.right.strftime("%H:%M") if pd.notnull(x) else "")
# #     agg["Window"] = agg["StartTime"].astype(str) + "–" + agg["EndTime"].astype(str)

# #     agg = agg.sort_values(by="StartTime")
# #     return agg, atm


# def compute_strike_time_distribution(hist, interval_minutes=30, strike_range=500):
#     hist["Timestamp"] = pd.to_datetime(hist["Timestamp"])
#     latest_underlying = hist["Underlying"].iloc[-1]
#     atm = round(latest_underlying / 50) * 50

#     # Filter within ATM ± range
#     hist = hist[
#         (hist["StrikePrice"] >= atm - strike_range) &
#         (hist["StrikePrice"] <= atm + strike_range)
#     ].copy()

#     # Create time bins
#     start_time = hist["Timestamp"].min().floor("T")
#     end_time = hist["Timestamp"].max().ceil("T")
#     time_bins = pd.date_range(start_time, end_time, freq=f"{interval_minutes}min")

#     hist["TimeBin"] = pd.cut(hist["Timestamp"], bins=time_bins)

#     # Aggregate OI change by Strike + Time window
#     agg = (
#         hist.groupby(["TimeBin", "StrikePrice"])
#         [["CE_ChangeOI", "PE_ChangeOI"]]
#         .sum()
#         .reset_index()
#     )

#     # Label bins for plotting
#     agg["StartTime"] = agg["TimeBin"].apply(lambda x: x.left.strftime("%H:%M") if pd.notnull(x) else "")
#     agg["EndTime"] = agg["TimeBin"].apply(lambda x: x.right.strftime("%H:%M") if pd.notnull(x) else "")
#     agg["Window"] = agg["StartTime"].astype(str) + "–" + agg["EndTime"].astype(str)

#     return agg, atm

# # ------------------------------------
# # Streamlit UI
# # ------------------------------------
# st.title("📊 NSE Option Chain Intelligence Dashboard")
# st.caption("Live Option Chain Tracker with Max Pain, Sentiment & Position Distribution Analytics")

# symbol = st.selectbox("Select Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY"])

# if not market_is_open():
#     st.warning("⏳ Market Closed. Dashboard updates only during 9:15–3:30.")
# else:
#     st.info("🔄 Auto-refresh active (5 min)")

#     hist = load_history(symbol)
#     if not hist.empty:
#         st.dataframe(hist.tail(10))


#     df = fetch_option_chain(symbol)
#     if df is not None and not df.empty:
#         save_tick_to_supabase(df, symbol)
#         save_tick(df, symbol)

#         # ---- Expiry Sorting ----
#         expiry_sorted = sorted(pd.to_datetime(df["Expiry"].unique()))
#         expiry_selected = st.selectbox(
#             "Select Expiry", [d.strftime("%d-%b-%Y") for d in expiry_sorted[:6]]
#         )

#         df = df[df["Expiry"] == pd.to_datetime(expiry_selected).strftime("%d-%b-%Y")]

#         # ---- ATM-based Strike Range ----
#         atm = round(df["Underlying"].iloc[-1] / 50) * 50
#         df = df[(df["StrikePrice"] >= atm - 1500) & (df["StrikePrice"] <= atm + 1500)]

#         # ---- Whale Activity ----
#         df["CE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["CE_ChangeOI"], x["CE_LTP"], "CE"), axis=1)
#         df["PE_Signal"] = df.apply(lambda x: interpret_whale_activity(x["PE_ChangeOI"], x["PE_LTP"], "PE"), axis=1)

#         # ---- Active Strikes ----
#         threshold_multiplier = 1.5
#         active_df = df[
#             (abs(df["CE_ChangeOI"]) > df["CE_ChangeOI"].mean() * threshold_multiplier)
#             | (abs(df["PE_ChangeOI"]) > df["PE_ChangeOI"].mean() * threshold_multiplier)
#         ]

#         st.subheader(f"🔥 Active Strike Prices — {symbol} ({expiry_selected})")
#         st.dataframe(active_df, use_container_width=True)

#         # ---- Key Metrics ----
#         pcr = compute_pcr(df)
#         max_pain = compute_max_pain(df)
#         sentiment = compute_sentiment(df)
#         low, high = estimate_range(df)

#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric("PCR", pcr)
#         c2.metric("Max Pain", max_pain)
#         c3.metric("Range Low", low)
#         c4.metric("Range High", high)
#         st.markdown(f"**AI Sentiment:** {sentiment}")

#         # ---- Visuals ----
#         c1, c2 = st.columns(2)
#         with c1:
#             fig1 = px.bar(active_df, x="StrikePrice", y="CE_ChangeOI", color="CE_Signal",
#                           title="Call OI Change (Buying vs Writing)")
#             st.plotly_chart(fig1, use_container_width=True)
#         with c2:
#             fig2 = px.bar(active_df, x="StrikePrice", y="PE_ChangeOI", color="PE_Signal",
#                           title="Put OI Change (Buying vs Writing)")
#             st.plotly_chart(fig2, use_container_width=True)

#         # ---- Max Pain Shift ----
#         today = datetime.now().strftime("%Y-%m-%d")
#         hist_path = os.path.join("data", today, f"{symbol}_ticks.xlsx")
#         if os.path.exists(hist_path):
#             hist = pd.read_excel(hist_path)
#             hist["Timestamp"] = pd.to_datetime(hist["Timestamp"])

#             # compute max pain per timestamp
#             mp_list = []
#             for t in hist["Timestamp"].unique():
#                 snap = hist[hist["Timestamp"] == t]
#                 mp_list.append({"Timestamp": t, "MaxPain": compute_max_pain(snap)})

#             hist_pain = pd.DataFrame(mp_list).sort_values("Timestamp")

#             fig3 = px.line(hist_pain, x="Timestamp", y="MaxPain", markers=True,
#                            title="📈 Max Pain Point Shift Throughout Day")
#             st.plotly_chart(fig3, use_container_width=True)

#             # ---- Time Interval Selector ----
#             interval = st.select_slider("Select Time Interval (minutes)", options=[15, 30, 45, 60], value=30)

#             # ---- OI Build-up Distribution ----
#             # agg, atm_val = compute_oi_distribution(hist, interval_minutes=interval, strike_range=500)
#             # st.subheader(f"🕒 OI Build-up Distribution Around ATM ±500 ({symbol}) — {interval} min")
#             # ---- Strike × Time OI Build-up Distribution ----
#             agg, atm_val = compute_strike_time_distribution(hist, interval_minutes=interval, strike_range=500)

#             st.subheader(f"📈 Strike × Time OI Build-up (ATM ±500) — {symbol} — {interval} min")

#             # Heatmap of CALL OI Change
#             fig_call = px.density_heatmap(
#                 agg,
#                 x="Window",
#                 y="StrikePrice",
#                 z="CE_ChangeOI",
#                 color_continuous_scale="RdYlGn",
#                 title=f"CALL OI Change Heatmap (per {interval}-min window)",
#             )
#             st.plotly_chart(fig_call, use_container_width=True)

#             # Heatmap of PUT OI Change
#             fig_put = px.density_heatmap(
#                 agg,
#                 x="Window",
#                 y="StrikePrice",
#                 z="PE_ChangeOI",
#                 color_continuous_scale="RdYlGn",
#                 title=f"PUT OI Change Heatmap (per {interval}-min window)",
#             )
#             st.plotly_chart(fig_put, use_container_width=True)

#             # Optional grouped bar view (aggregated per time window)
#             agg_time = agg.groupby("Window")[["CE_ChangeOI", "PE_ChangeOI"]].sum().reset_index()
#             fig_bar = px.bar(
#                 agg_time, x="Window", y=["CE_ChangeOI", "PE_ChangeOI"],
#                 barmode="group", title=f"Net OI Change per {interval}-min Window"
#             )
#             st.plotly_chart(fig_bar, use_container_width=True)

#             st.dataframe(agg, use_container_width=True)

#             fig4 = px.bar(agg, x="Window", y=["CE_ChangeOI", "PE_ChangeOI"],
#                           barmode="group", title=f"OI Changes per {interval}-min Window")
#             st.plotly_chart(fig4, use_container_width=True)
#             st.dataframe(agg, use_container_width=True)

#         st.success(f"✅ Updated at {datetime.now().strftime('%H:%M:%S')}")
#     else:
#         st.error("⚠️ Failed to fetch option chain data.")

# _______________________________________________________________________________________________________________________________

=======
>>>>>>> eb4cc8a479d046cb9035b15c6195599fb306fe7a
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
<<<<<<< HEAD

=======
>>>>>>> eb4cc8a479d046cb9035b15c6195599fb306fe7a
