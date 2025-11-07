# import pandas as pd
# import streamlit as st
# import matplotlib.pyplot as plt

# st.set_page_config(page_title="NIFTY EMA Backtest", layout="wide")
# st.title("📊 NIFTY 50 EMA (20/50) Crossover Backtest Dashboard")

# # -------------------------------
# # 1️⃣ Upload CSV
# # -------------------------------
# uploaded_file = st.file_uploader("Upload your cleaned nifty_data_with_ema.csv", type=["csv"])

# if uploaded_file is not None:
#     df = pd.read_csv(uploaded_file)

#     # -------------------------------
#     # 2️⃣ Clean Column Names
#     # -------------------------------
#     df.columns = df.columns.str.replace(" ", "", regex=False).str.upper()
#     required_cols = ["DATE", "CLOSE", "EMA20", "EMA50"]
#     missing = [col for col in required_cols if col not in df.columns]
#     if missing:
#         st.error(f"❌ Missing required columns: {missing}")
#         st.stop()

#     # Ensure Date is datetime
#     df["DATE"] = pd.to_datetime(df["DATE"])
#     df.sort_values("DATE", inplace=True)
#     df.reset_index(drop=True, inplace=True)

#     st.success("✅ Data loaded successfully!")
#     st.dataframe(df.head())

#     # -------------------------------
#     # 3️⃣ Generate Signals
#     # -------------------------------
#     df["SIGNAL"] = 0
#     df.loc[df["EMA20"] > df["EMA50"], "SIGNAL"] = 1   # bullish
#     df.loc[df["EMA20"] < df["EMA50"], "SIGNAL"] = -1  # bearish
#     df["CROSSOVER"] = df["SIGNAL"].diff()  # detect crossovers

#     # -------------------------------
#     # 4️⃣ Backtesting Logic
#     # -------------------------------
#     trades = []
#     position = None  # 'long' or 'short'
#     entry_price = 0
#     entry_date = None
#     qty = 100

#     for i in range(1, len(df)):
#         close_price = df.loc[i, "CLOSE"]

#         # BUY entry: 20 EMA crosses above 50 EMA
#         if df.loc[i, "CROSSOVER"] == 2 and position is None:
#             position = "long"
#             entry_price = close_price
#             entry_date = df.loc[i, "DATE"]

#         # SELL entry: 50 EMA crosses above 20 EMA
#         elif df.loc[i, "CROSSOVER"] == -2 and position is None:
#             position = "short"
#             entry_price = close_price
#             entry_date = df.loc[i, "DATE"]

#         # EXIT long when close < EMA50
#         elif position == "long" and close_price < df.loc[i, "EMA50"]:
#             exit_price = close_price
#             exit_date = df.loc[i, "DATE"]
#             profit = (exit_price - entry_price) * qty
#             trades.append(["BUY", entry_date, entry_price, exit_date, exit_price, profit])
#             position = None

#         # EXIT short when close > EMA50
#         elif position == "short" and close_price > df.loc[i, "EMA50"]:
#             exit_price = close_price
#             exit_date = df.loc[i, "DATE"]
#             profit = (entry_price - exit_price) * qty
#             trades.append(["SELL", entry_date, entry_price, exit_date, exit_price, profit])
#             position = None

#     # -------------------------------
#     # 5️⃣ Trade Results DataFrame
#     # -------------------------------
#     trade_df = pd.DataFrame(trades, columns=["Type", "Entry_Date", "Entry_Price", "Exit_Date", "Exit_Price", "Profit"])
#     trade_df["Profit"] = trade_df["Profit"].round(2)

#     st.subheader("💼 Trade History")
#     st.dataframe(trade_df)

#     # Download CSV
#     st.download_button(
#         "📥 Download Backtest Results CSV",
#         data=trade_df.to_csv(index=False),
#         file_name="backtest_results.csv",
#         mime="text/csv"
#     )

#     # -------------------------------
#     # 6️⃣ Performance Summary
#     # -------------------------------
#     total_trades = len(trade_df)
#     wins = (trade_df["Profit"] > 0).sum()
#     losses = (trade_df["Profit"] <= 0).sum()
#     net_profit = trade_df["Profit"].sum()
#     avg_profit = trade_df["Profit"].mean() if total_trades > 0 else 0

#     st.subheader("📊 Performance Summary")
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("Total Trades", total_trades)
#     col2.metric("Winning Trades", wins)
#     col3.metric("Losing Trades", losses)
#     col4.metric("Net P&L (₹)", f"{net_profit:,.0f}")
#     col5.metric("Avg Profit per Trade (₹)", f"{avg_profit:,.2f}")

#     # -------------------------------
#     # 7️⃣ Plot Price + EMAs + Signals
#     # -------------------------------
#     st.subheader("📈 Price Chart with EMA Signals")
#     fig, ax = plt.subplots(figsize=(14,6))
#     ax.plot(df["DATE"], df["CLOSE"], label="Close", color="blue", linewidth=1)
#     ax.plot(df["DATE"], df["EMA20"], label="EMA20", color="green", linewidth=1)
#     ax.plot(df["DATE"], df["EMA50"], label="EMA50", color="red", linewidth=1)

#     # Plot buy/sell entry markers
#     for _, trade in trade_df.iterrows():
#         if trade["Type"] == "BUY":
#             ax.scatter(trade["Entry_Date"], trade["Entry_Price"], marker="^", color="lime", s=80)
#         else:
#             ax.scatter(trade["Entry_Date"], trade["Entry_Price"], marker="v", color="orange", s=80)

#     ax.set_title("NIFTY 50 EMA 20/50 Crossover Signals")
#     ax.set_xlabel("Date")
#     ax.set_ylabel("Price (INR)")
#     ax.legend()
#     ax.grid(True)
#     st.pyplot(fig)

# else:
#     st.info("⬆️ Please upload your cleaned `nifty_data_with_ema.csv` to start backtesting.")


# Candlestick__________________________________________________________________________________________________________

# import pandas as pd
# import streamlit as st
# import plotly.graph_objects as go

# st.set_page_config(page_title="NIFTY EMA Backtest", layout="wide")
# st.title("📊 NIFTY 50 EMA (20/50) Crossover Backtest with Candlestick Chart")

# # -------------------------------
# # 1️⃣ Upload CSV
# # -------------------------------
# uploaded_file = st.file_uploader("Upload your cleaned nifty_data_with_ema.csv", type=["csv"])

# if uploaded_file is not None:
#     df = pd.read_csv(uploaded_file)

#     # -------------------------------
#     # 2️⃣ Clean Columns
#     # -------------------------------
#     df.columns = df.columns.str.replace(" ", "", regex=False).str.upper()
#     required_cols = ["DATE", "OPEN", "HIGH", "LOW", "CLOSE", "EMA20", "EMA50"]
#     missing = [col for col in required_cols if col not in df.columns]
#     if missing:
#         st.error(f"❌ Missing required columns: {missing}")
#         st.stop()

#     df["DATE"] = pd.to_datetime(df["DATE"])
#     df.sort_values("DATE", inplace=True)
#     df.reset_index(drop=True, inplace=True)

#     st.success("✅ Data loaded successfully!")
#     st.dataframe(df.head())

#     # -------------------------------
#     # 3️⃣ Generate Signals
#     # -------------------------------
#     df["SIGNAL"] = 0
#     df.loc[df["EMA20"] > df["EMA50"], "SIGNAL"] = 1
#     df.loc[df["EMA20"] < df["EMA50"], "SIGNAL"] = -1
#     df["CROSSOVER"] = df["SIGNAL"].diff()

#     # -------------------------------
#     # 4️⃣ Backtesting Logic
#     # -------------------------------
#     trades = []
#     position = None
#     entry_price = 0
#     entry_date = None
#     qty = 100

#     for i in range(1, len(df)):
#         close_price = df.loc[i, "CLOSE"]

#         # BUY entry
#         if df.loc[i, "CROSSOVER"] == 2 and position is None:
#             position = "long"
#             entry_price = close_price
#             entry_date = df.loc[i, "DATE"]

#         # SELL entry
#         elif df.loc[i, "CROSSOVER"] == -2 and position is None:
#             position = "short"
#             entry_price = close_price
#             entry_date = df.loc[i, "DATE"]

#         # EXIT long
#         elif position == "long" and close_price < df.loc[i, "EMA50"]:
#             exit_price = close_price
#             exit_date = df.loc[i, "DATE"]
#             profit = (exit_price - entry_price) * qty
#             trades.append(["BUY", entry_date, entry_price, exit_date, exit_price, profit])
#             position = None

#         # EXIT short
#         elif position == "short" and close_price > df.loc[i, "EMA50"]:
#             exit_price = close_price
#             exit_date = df.loc[i, "DATE"]
#             profit = (entry_price - exit_price) * qty
#             trades.append(["SELL", entry_date, entry_price, exit_date, exit_price, profit])
#             position = None

#     # -------------------------------
#     # 5️⃣ Trade Results
#     # -------------------------------
#     trade_df = pd.DataFrame(trades, columns=["Type", "Entry_Date", "Entry_Price", "Exit_Date", "Exit_Price", "Profit"])
#     trade_df["Profit"] = trade_df["Profit"].round(2)

#     st.subheader("💼 Trade History")
#     st.dataframe(trade_df)

#     # Download CSV
#     st.download_button(
#         "📥 Download Backtest Results CSV",
#         data=trade_df.to_csv(index=False),
#         file_name="backtest_results.csv",
#         mime="text/csv"
#     )

#     # -------------------------------
#     # 6️⃣ Summary Metrics
#     # -------------------------------
#     total_trades = len(trade_df)
#     wins = (trade_df["Profit"] > 0).sum()
#     losses = (trade_df["Profit"] <= 0).sum()
#     net_profit = trade_df["Profit"].sum()
#     avg_profit = trade_df["Profit"].mean() if total_trades > 0 else 0

#     st.subheader("📊 Performance Summary")
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("Total Trades", total_trades)
#     col2.metric("Winning Trades", wins)
#     col3.metric("Losing Trades", losses)
#     col4.metric("Net P&L (₹)", f"{net_profit:,.0f}")
#     col5.metric("Avg Profit per Trade (₹)", f"{avg_profit:,.2f}")

#     # -------------------------------
#     # 7️⃣ Plot Candlestick Chart with EMAs and Signals
#     # -------------------------------
#     st.subheader("📈 Candlestick Chart with EMA Signals")

#     fig = go.Figure()

#     # Candlestick
#     fig.add_trace(go.Candlestick(
#         x=df["DATE"],
#         open=df["OPEN"],
#         high=df["HIGH"],
#         low=df["LOW"],
#         close=df["CLOSE"],
#         name="OHLC"
#     ))

#     # EMA20 & EMA50
#     fig.add_trace(go.Scatter(
#         x=df["DATE"], y=df["EMA20"], mode="lines", name="EMA20",
#         line=dict(color="green", width=1.5)
#     ))
#     fig.add_trace(go.Scatter(
#         x=df["DATE"], y=df["EMA50"], mode="lines", name="EMA50",
#         line=dict(color="red", width=1.5)
#     ))

#     # Buy/Sell markers
#     for _, trade in trade_df.iterrows():
#         if trade["Type"] == "BUY":
#             fig.add_trace(go.Scatter(
#                 x=[trade["Entry_Date"]], y=[trade["Entry_Price"]],
#                 mode="markers", marker_symbol="triangle-up", marker_color="lime", marker_size=12,
#                 name="Buy"
#             ))
#         else:
#             fig.add_trace(go.Scatter(
#                 x=[trade["Entry_Date"]], y=[trade["Entry_Price"]],
#                 mode="markers", marker_symbol="triangle-down", marker_color="orange", marker_size=12,
#                 name="Sell"
#             ))

#     fig.update_layout(
#         xaxis_title="Date",
#         yaxis_title="Price (INR)",
#         xaxis_rangeslider_visible=False,
#         title="NIFTY 50 EMA 20/50 Crossover Candlestick Chart"
#     )

#     st.plotly_chart(fig, use_container_width=True)

# else:
#     st.info("⬆️ Upload your cleaned `nifty_data_with_ema.csv` to start backtesting.")
# ______________________________________________________________________________________________________________

# import pandas as pd
# import streamlit as st
# import plotly.graph_objects as go

# st.set_page_config(page_title="NIFTY EMA Backtest Dashboard", layout="wide")
# st.title("📊 NIFTY 50 EMA (20/50) Backtest Dashboard")

# # -------------------------------
# # 1️⃣ Upload CSV
# # -------------------------------
# uploaded_file = st.file_uploader("Upload your cleaned nifty_data_with_ema.csv", type=["csv"])

# if uploaded_file is not None:
#     df = pd.read_csv(uploaded_file)

#     # -------------------------------
#     # 2️⃣ Clean Columns
#     # -------------------------------
#     df.columns = df.columns.str.replace(" ", "", regex=False).str.upper()
#     required_cols = ["DATE", "OPEN", "HIGH", "LOW", "CLOSE", "EMA20", "EMA50"]
#     missing = [col for col in required_cols if col not in df.columns]
#     if missing:
#         st.error(f"❌ Missing required columns: {missing}")
#         st.stop()

#     df["DATE"] = pd.to_datetime(df["DATE"])
#     df.sort_values("DATE", inplace=True)
#     df.reset_index(drop=True, inplace=True)

#     st.success("✅ Data loaded successfully!")
#     st.dataframe(df.head())

#     # -------------------------------
#     # 3️⃣ Generate Signals
#     # -------------------------------
#     df["SIGNAL"] = 0
#     df.loc[df["EMA20"] > df["EMA50"], "SIGNAL"] = 1
#     df.loc[df["EMA20"] < df["EMA50"], "SIGNAL"] = -1
#     df["CROSSOVER"] = df["SIGNAL"].diff()

#     # -------------------------------
#     # 4️⃣ Backtesting Logic
#     # -------------------------------
#     trades = []
#     position = None
#     entry_price = 0
#     entry_date = None
#     qty = 100

#     for i in range(1, len(df)):
#         close_price = df.loc[i, "CLOSE"]

#         # BUY entry
#         if df.loc[i, "CROSSOVER"] == 2 and position is None:
#             position = "long"
#             entry_price = close_price
#             entry_date = df.loc[i, "DATE"]

#         # SELL entry
#         elif df.loc[i, "CROSSOVER"] == -2 and position is None:
#             position = "short"
#             entry_price = close_price
#             entry_date = df.loc[i, "DATE"]

#         # EXIT long
#         elif position == "long" and close_price < df.loc[i, "EMA50"]:
#             exit_price = close_price
#             exit_date = df.loc[i, "DATE"]
#             profit = (exit_price - entry_price) * qty
#             trades.append(["BUY", entry_date, entry_price, exit_date, exit_price, profit])
#             position = None

#         # EXIT short
#         elif position == "short" and close_price > df.loc[i, "EMA50"]:
#             exit_price = close_price
#             exit_date = df.loc[i, "DATE"]
#             profit = (entry_price - exit_price) * qty
#             trades.append(["SELL", entry_date, entry_price, exit_date, exit_price, profit])
#             position = None

#     # -------------------------------
#     # 5️⃣ Trade Results
#     # -------------------------------
#     trade_df = pd.DataFrame(trades, columns=["Type", "Entry_Date", "Entry_Price", "Exit_Date", "Exit_Price", "Profit"])
#     trade_df["Profit"] = trade_df["Profit"].round(2)

#     st.subheader("💼 Trade History")
#     st.dataframe(trade_df)

#     st.download_button(
#         "📥 Download Backtest Results CSV",
#         data=trade_df.to_csv(index=False),
#         file_name="backtest_results.csv",
#         mime="text/csv"
#     )

#     # -------------------------------
#     # 6️⃣ Summary Metrics
#     # -------------------------------
#     total_trades = len(trade_df)
#     wins = (trade_df["Profit"] > 0).sum()
#     losses = (trade_df["Profit"] <= 0).sum()
#     net_profit = trade_df["Profit"].sum()
#     avg_profit = trade_df["Profit"].mean() if total_trades > 0 else 0

#     st.subheader("📊 Performance Summary")
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.metric("Total Trades", total_trades)
#     col2.metric("Winning Trades", wins)
#     col3.metric("Losing Trades", losses)
#     col4.metric("Net P&L (₹)", f"{net_profit:,.0f}")
#     col5.metric("Avg Profit per Trade (₹)", f"{avg_profit:,.2f}")

#     # -------------------------------
#     # 7️⃣ Interactive Candlestick Chart with EMA & Buy/Sell
#     # -------------------------------
#     st.subheader("📈 Interactive Candlestick Chart")

#     fig = go.Figure()

#     # Candlestick
#     fig.add_trace(go.Candlestick(
#         x=df["DATE"], open=df["OPEN"], high=df["HIGH"], low=df["LOW"], close=df["CLOSE"],
#         name="OHLC"
#     ))

#     # EMA overlays
#     fig.add_trace(go.Scatter(x=df["DATE"], y=df["EMA20"], mode='lines', name='EMA20', line=dict(color='green', width=1.5)))
#     fig.add_trace(go.Scatter(x=df["DATE"], y=df["EMA50"], mode='lines', name='EMA50', line=dict(color='red', width=1.5)))

#     # Buy/Sell markers
#     for _, trade in trade_df.iterrows():
#         if trade["Type"] == "BUY":
#             fig.add_trace(go.Scatter(
#                 x=[trade["Entry_Date"]], y=[trade["Entry_Price"]],
#                 mode="markers", marker_symbol="triangle-up", marker_color="lime", marker_size=12,
#                 name="Buy"
#             ))
#         else:
#             fig.add_trace(go.Scatter(
#                 x=[trade["Entry_Date"]], y=[trade["Entry_Price"]],
#                 mode="markers", marker_symbol="triangle-down", marker_color="orange", marker_size=12,
#                 name="Sell"
#             ))

#     # Range slider & selector
#     fig.update_layout(
#         xaxis=dict(
#             rangeslider=dict(visible=True),
#             rangeselector=dict(
#                 buttons=list([
#                     dict(count=1, label="1m", step="month", stepmode="backward"),
#                     dict(count=3, label="3m", step="month", stepmode="backward"),
#                     dict(count=6, label="6m", step="month", stepmode="backward"),
#                     dict(count=1, label="YTD", step="year", stepmode="todate"),
#                     dict(count=1, label="1y", step="year", stepmode="backward"),
#                     dict(step="all")
#                 ])
#             ),
#             type='date'
#         ),
#         yaxis=dict(
#             autorange=True,
#             fixedrange=False,
#             title='Price (INR)'
#         ),
#         title="NIFTY 50 EMA 20/50 Crossover Candlestick Chart",
#         hovermode="x unified"
#     )

#     st.plotly_chart(fig, use_container_width=True)

# else:
#     st.info("⬆️ Upload your cleaned `nifty_data_with_ema.csv` to start backtesting.")


# import pandas as pd
# import streamlit as st
# import plotly.graph_objects as go

# st.set_page_config(page_title="NIFTY EMA Backtest Dashboard", layout="wide")
# st.title("📊 NIFTY 50 EMA (20/50) Backtest Dashboard — Rolling 30-Candle View")

# # -------------------------------
# # 1️⃣ Upload CSV
# # -------------------------------
# uploaded_file = st.file_uploader("Upload your cleaned nifty_data_with_ema.csv", type=["csv"])

# if uploaded_file is not None:
#     df = pd.read_csv(uploaded_file)

#     # -------------------------------
#     # 2️⃣ Clean Columns
#     # -------------------------------
#     df.columns = df.columns.str.replace(" ", "", regex=False).str.upper()
#     required_cols = ["DATE", "OPEN", "HIGH", "LOW", "CLOSE", "EMA20", "EMA50", "VOLUME"]
#     missing = [col for col in required_cols if col not in df.columns]
#     if missing:
#         st.error(f"❌ Missing required columns: {missing}")
#         st.stop()

#     df["DATE"] = pd.to_datetime(df["DATE"])
#     df.sort_values("DATE", inplace=True)
#     df.reset_index(drop=True, inplace=True)

#     st.success("✅ Data loaded successfully!")
#     st.dataframe(df.head())

#     # -------------------------------
#     # 3️⃣ Generate Signals
#     # -------------------------------
#     df["SIGNAL"] = 0
#     df.loc[df["EMA20"] > df["EMA50"], "SIGNAL"] = 1
#     df.loc[df["EMA20"] < df["EMA50"], "SIGNAL"] = -1
#     df["CROSSOVER"] = df["SIGNAL"].diff()

#     # -------------------------------
#     # 4️⃣ Backtesting Logic
#     # -------------------------------
#     trades = []
#     position = None
#     entry_price = 0
#     entry_date = None
#     qty = 100

#     for i in range(1, len(df)):
#         close_price = df.loc[i, "CLOSE"]

#         # BUY entry
#         if df.loc[i, "CROSSOVER"] == 2 and position is None:
#             position = "long"
#             entry_price = close_price
#             entry_date = df.loc[i, "DATE"]

#         # SELL entry
#         elif df.loc[i, "CROSSOVER"] == -2 and position is None:
#             position = "short"
#             entry_price = close_price
#             entry_date = df.loc[i, "DATE"]

#         # EXIT long
#         elif position == "long" and close_price < df.loc[i, "EMA50"]:
#             exit_price = close_price
#             exit_date = df.loc[i, "DATE"]
#             profit = (exit_price - entry_price) * qty
#             trades.append(["BUY", entry_date, entry_price, exit_date, exit_price, profit])
#             position = None

#         # EXIT short
#         elif position == "short" and close_price > df.loc[i, "EMA50"]:
#             exit_price = close_price
#             exit_date = df.loc[i, "DATE"]
#             profit = (entry_price - exit_price) * qty
#             trades.append(["SELL", entry_date, entry_price, exit_date, exit_price, profit])
#             position = None

#     # -------------------------------
#     # 5️⃣ Trade Results
#     # -------------------------------
#     trade_df = pd.DataFrame(trades, columns=["Type", "Entry_Date", "Entry_Price", "Exit_Date", "Exit_Price", "Profit"])
#     trade_df["Profit"] = trade_df["Profit"].round(2)

#     st.subheader("💼 Trade History")
#     st.dataframe(trade_df)

#     # -------------------------------
#     # 6️⃣ Dynamic Rolling 30-Candle Range
#     # -------------------------------
#     st.subheader("📅 Select Candle Window")
#     window_size = 150
#     total_points = len(df)

#     # Slider to move window
#     start_idx = st.slider("Scroll through data", 0, total_points - window_size, total_points - window_size, 1)
#     end_idx = start_idx + window_size

#     df_window = df.iloc[start_idx:end_idx]

#     # -------------------------------
#     # 7️⃣ Price + EMA Chart
#     # -------------------------------
#     fig = go.Figure()

#     # Candlestick
#     fig.add_trace(go.Candlestick(
#         x=df_window["DATE"], open=df_window["OPEN"], high=df_window["HIGH"],
#         low=df_window["LOW"], close=df_window["CLOSE"], name="OHLC"
#     ))

#     # EMAs
#     fig.add_trace(go.Scatter(x=df_window["DATE"], y=df_window["EMA20"], mode="lines", name="EMA20", line=dict(color="green", width=1.5)))
#     fig.add_trace(go.Scatter(x=df_window["DATE"], y=df_window["EMA50"], mode="lines", name="EMA50", line=dict(color="red", width=1.5)))

#     # Mark trades within visible window
#     for _, trade in trade_df.iterrows():
#         if trade["Entry_Date"] >= df_window["DATE"].iloc[0] and trade["Entry_Date"] <= df_window["DATE"].iloc[-1]:
#             color = "lime" if trade["Type"] == "BUY" else "orange"
#             symbol = "triangle-up" if trade["Type"] == "BUY" else "triangle-down"
#             fig.add_trace(go.Scatter(
#                 x=[trade["Entry_Date"]], y=[trade["Entry_Price"]],
#                 mode="markers", marker_symbol=symbol, marker_color=color, marker_size=12,
#                 name=trade["Type"]
#             ))

#     fig.update_layout(
#         title=f"NIFTY 50 EMA 20/50 Crossover (Candles {start_idx+1}–{end_idx})",
#         xaxis_title="Date", yaxis_title="Price (INR)",
#         hovermode="x unified", xaxis_rangeslider_visible=False
#     )

#     st.plotly_chart(fig, use_container_width=True)

#     # -------------------------------
#     # 8️⃣ Volume Chart (for same 30 days)
#     # -------------------------------
#     st.subheader("🔊 Volume (30-Candle Window)")

#     df_window["VOL_MA20"] = df_window["VOLUME"].rolling(window=20).mean()
#     df_window["VOL_COLOR"] = ["green" if c >= o else "red" for c, o in zip(df_window["CLOSE"], df_window["OPEN"])]

#     fig_vol = go.Figure()
#     fig_vol.add_trace(go.Bar(x=df_window["DATE"], y=df_window["VOLUME"],
#                              marker_color=df_window["VOL_COLOR"], name="Volume"))
#     fig_vol.add_trace(go.Scatter(x=df_window["DATE"], y=df_window["VOL_MA20"],
#                                  mode="lines", name="20-Day Avg Volume", line=dict(color="yellow", width=2)))

#     fig_vol.update_layout(
#         title="Volume with 20-Day Average (Synced with Price Window)",
#         xaxis_title="Date", yaxis_title="Volume",
#         hovermode="x unified", bargap=0.1
#     )

#     st.plotly_chart(fig_vol, use_container_width=True)

# else:
#     st.info("⬆️ Upload your cleaned `nifty_data_with_ema.csv` to start backtesting.")

import pandas as pd
import numpy as np
from scipy import stats
import streamlit as st
import plotly.graph_objects as go

# -------------------------------
# Streamlit setup
# -------------------------------
st.set_page_config(page_title="NIFTY EMA + Volume Confirmation", layout="wide")
st.title("📊 NIFTY 50 EMA (20/50) with Volume Confirmation Dashboard")

# -------------------------------
# Upload data
# -------------------------------
uploaded_file = st.file_uploader("Upload your cleaned nifty_data_with_ema.csv", type=["csv"])

# -------------------------------
# Helper Functions
# -------------------------------
def compute_volume_features(df, vol_col="VOLUME", price_col="CLOSE",
                            vol_ma_window=20, slope_window=6, vol_roc_window=5, cmf_window=20):
    df = df.copy()
    df = df.sort_values("DATE").reset_index(drop=True)

    df["VOL_MA"] = df[vol_col].rolling(vol_ma_window).mean()
    df["VOL_STD"] = df[vol_col].rolling(vol_ma_window).std().replace(0, np.nan)
    df["VOL_Z"] = ((df[vol_col] - df["VOL_MA"]) / df["VOL_STD"]).fillna(0)
    df["VOL_ROC"] = (df[vol_col] / df[vol_col].shift(vol_roc_window) - 1).fillna(0)

    slopes = np.full(len(df), np.nan)
    idxs = np.arange(slope_window)
    for i in range(slope_window - 1, len(df)):
        y = df[vol_col].iloc[i - slope_window + 1: i + 1].values
        try:
            slope, _, _, _, _ = stats.linregress(idxs, y)
        except Exception:
            slope = 0.0
        slopes[i] = slope
    df["VOL_SLOPE"] = slopes
    df["VOL_SLOPE_NORM"] = (df["VOL_SLOPE"] /
                            df[vol_col].rolling(vol_ma_window).mean().replace(0, np.nan)).fillna(0)

    # OBV
    obv = [0]
    for i in range(1, len(df)):
        if df[price_col].iat[i] > df[price_col].iat[i-1]:
            obv.append(obv[-1] + df[vol_col].iat[i])
        elif df[price_col].iat[i] < df[price_col].iat[i-1]:
            obv.append(obv[-1] - df[vol_col].iat[i])
        else:
            obv.append(obv[-1])
    df["OBV"] = obv
    df["OBV_MA20"] = df["OBV"].rolling(vol_ma_window).mean()

    # CMF
    mf_mult = ((df[price_col] - df["LOW"]) - (df["HIGH"] - df[price_col])) / (
        df["HIGH"] - df["LOW"]).replace(0, np.nan)
    mf_vol = mf_mult * df[vol_col]
    df["CMF"] = mf_vol.rolling(cmf_window).sum() / df[vol_col].rolling(cmf_window).sum()
    df["CMF"] = df["CMF"].fillna(0)

    return df


def volume_confirmed_crossover(df, ema_short="EMA20", ema_long="EMA50",
                               vol_z_thresh=1.0, slope_norm_thresh=0.0):
    df = df.copy()
    prev_short = df[ema_short].shift(1)
    prev_long = df[ema_long].shift(1)

    buy_x = (prev_short <= prev_long) & (df[ema_short] > df[ema_long])
    sell_x = (prev_short >= prev_long) & (df[ema_short] < df[ema_long])

    df["BUY_X"] = buy_x
    df["SELL_X"] = sell_x

    df["CONFIRMED_BUY"] = buy_x & (
        (df["VOL_Z"] >= vol_z_thresh) |
        ((df["VOL_SLOPE_NORM"] > slope_norm_thresh) & (df["CMF"] > 0))
    )
    df["CONFIRMED_SELL"] = sell_x & (
        (df["VOL_Z"] >= vol_z_thresh) |
        ((df["VOL_SLOPE_NORM"] < -slope_norm_thresh) & (df["CMF"] < 0))
    )

    return df


# -------------------------------
# Main logic
# -------------------------------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.upper()

    required_cols = ["DATE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "EMA20", "EMA50"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"❌ Missing required columns: {missing}")
        st.stop()

    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df.sort_values("DATE").reset_index(drop=True)

    # Parameter sliders
    st.sidebar.header("⚙️ Volume Confirmation Settings")
    vol_z_thresh = st.sidebar.slider("Volume Z Threshold", 0.0, 2.0, 1.0, 0.1)
    slope_norm_thresh = st.sidebar.slider("Volume Slope Threshold", 0.0, 0.05, 0.01, 0.005)

    st.sidebar.markdown("---")
    start_idx = st.sidebar.slider("Scroll through candles", 0, len(df)-100, 0, 1)

    # Compute features
    df = compute_volume_features(df)
    df = volume_confirmed_crossover(df, vol_z_thresh=vol_z_thresh, slope_norm_thresh=slope_norm_thresh)

    # Extract window (100 candles)
    end_idx = start_idx + 150
    df_window = df.iloc[start_idx:end_idx]

    # --------------------------------
    # Candlestick + EMA + Confirmed markers
    # --------------------------------
    fig_price = go.Figure()
    fig_price.add_trace(go.Candlestick(
        x=df_window["DATE"], open=df_window["OPEN"], high=df_window["HIGH"],
        low=df_window["LOW"], close=df_window["CLOSE"], name="Price"
    ))
    fig_price.add_trace(go.Scatter(x=df_window["DATE"], y=df_window["EMA20"],
                                   mode="lines", name="EMA20", line=dict(color="green", width=1.5)))
    fig_price.add_trace(go.Scatter(x=df_window["DATE"], y=df_window["EMA50"],
                                   mode="lines", name="EMA50", line=dict(color="red", width=1.5)))

    confirmed_buys = df_window[df_window["CONFIRMED_BUY"]]
    confirmed_sells = df_window[df_window["CONFIRMED_SELL"]]
    unconfirmed_buys = df_window[df_window["BUY_X"] & ~df_window["CONFIRMED_BUY"]]
    unconfirmed_sells = df_window[df_window["SELL_X"] & ~df_window["CONFIRMED_SELL"]]

    fig_price.add_trace(go.Scatter(
        x=confirmed_buys["DATE"], y=confirmed_buys["CLOSE"],
        mode="markers", marker=dict(symbol="triangle-up", color="lime", size=14),
        name="Confirmed Buy"
    ))
    fig_price.add_trace(go.Scatter(
        x=unconfirmed_buys["DATE"], y=unconfirmed_buys["CLOSE"],
        mode="markers", marker=dict(symbol="triangle-up-open", color="lime", size=10),
        name="Unconfirmed Buy"
    ))
    fig_price.add_trace(go.Scatter(
        x=confirmed_sells["DATE"], y=confirmed_sells["CLOSE"],
        mode="markers", marker=dict(symbol="triangle-down", color="orange", size=14),
        name="Confirmed Sell"
    ))
    fig_price.add_trace(go.Scatter(
        x=unconfirmed_sells["DATE"], y=unconfirmed_sells["CLOSE"],
        mode="markers", marker=dict(symbol="triangle-down-open", color="orange", size=10),
        name="Unconfirmed Sell"
    ))

    fig_price.update_layout(
        title="EMA (20/50) Crossover with Volume Confirmation",
        xaxis_title="Date", yaxis_title="Price (INR)",
        xaxis_rangeslider_visible=False, height=600, hovermode="x unified"
    )

    # --------------------------------
    # Volume Chart
    # --------------------------------
    df_window["VOL_COLOR"] = df_window["VOL_Z"].apply(
        lambda z: "red" if z > 1.2 else ("orange" if z > 0.8 else "gray"))

    fig_vol = go.Figure()
    fig_vol.add_trace(go.Bar(
        x=df_window["DATE"], y=df_window["VOLUME"], marker_color=df_window["VOL_COLOR"], name="Volume"
    ))
    fig_vol.add_trace(go.Scatter(
        x=df_window["DATE"], y=df_window["VOL_MA"], mode="lines", name="VOL_MA20", line=dict(color="blue", width=1)
    ))

    fig_vol.update_layout(
        title="Volume Activity (colored by Z-score)",
        xaxis_title="Date", yaxis_title="Volume", height=250, hovermode="x unified",
        xaxis_rangeslider_visible=False
    )

    # --------------------------------
    # Display Charts
    # --------------------------------
    st.plotly_chart(fig_price, use_container_width=True)
    st.plotly_chart(fig_vol, use_container_width=True)

else:
    st.info("⬆️ Upload your `nifty_data_with_ema.csv` to begin.")



