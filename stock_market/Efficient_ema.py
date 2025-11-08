import pandas as pd
import itertools

# -----------------------------
# Load NIFTY data
# -----------------------------
df = pd.read_csv(r"C:\Users\DELL\Desktop\Data Science\Stock Market\nifty_data.csv")
df.columns = df.columns.str.strip()
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# -----------------------------
# Parameters
# -----------------------------
ema_range = range(5, 101)
qty = 100
all_trades = []
summary = []

# -----------------------------
# EMA Optimization
# -----------------------------
for short_ema, long_ema in itertools.product(ema_range, repeat=2):
    if short_ema >= long_ema:
        continue  # EMA_short must be less than EMA_long
    
    df["EMA_short"] = df["Close"].ewm(span=short_ema, adjust=False).mean()
    df["EMA_long"] = df["Close"].ewm(span=long_ema, adjust=False).mean()
    
    # Previous EMA values
    df["Prev_EMA_short"] = df["EMA_short"].shift(1)
    df["Prev_EMA_long"] = df["EMA_long"].shift(1)
    
    # Detect crossovers
    df["Buy_Signal"] = (df["Prev_EMA_short"] <= df["Prev_EMA_long"]) & (df["EMA_short"] > df["EMA_long"])
    df["Sell_Signal"] = (df["Prev_EMA_short"] >= df["Prev_EMA_long"]) & (df["EMA_short"] < df["EMA_long"])
    
    # Backtest trades
    position = None
    entry_price = 0
    entry_date = None
    trades = []
    
    for i in range(len(df)):
        row = df.iloc[i]
        
        # CLOSE SHORT if BUY crossover
        if position == "short" and row["Buy_Signal"]:
            exit_price = row["Close"]
            exit_date = row["Date"]
            pnl = (entry_price - exit_price) * qty
            trades.append([short_ema, long_ema, entry_date, exit_date, "Sell", entry_price, exit_price, pnl])
            position = None
        
        # OPEN LONG if BUY crossover
        if row["Buy_Signal"] and position is None:
            entry_price = row["Close"]
            entry_date = row["Date"]
            position = "long"
        
        # CLOSE LONG if SELL crossover
        if position == "long" and row["Sell_Signal"]:
            exit_price = row["Close"]
            exit_date = row["Date"]
            pnl = (exit_price - entry_price) * qty
            trades.append([short_ema, long_ema, entry_date, exit_date, "Buy", entry_price, exit_price, pnl])
            position = None
        
        # OPEN SHORT if SELL crossover
        if row["Sell_Signal"] and position is None:
            entry_price = row["Close"]
            entry_date = row["Date"]
            position = "short"
    
    # Save trades
    all_trades.extend(trades)
    
    # Summary
    total_trades = len(trades)
    profit_trades = sum(1 for t in trades if t[7] > 0)
    loss_trades = total_trades - profit_trades
    net_profit = sum(t[7] for t in trades)
    summary.append([short_ema, long_ema, total_trades, profit_trades, loss_trades, net_profit])

# -----------------------------
# Save all trades
# -----------------------------
trades_df = pd.DataFrame(all_trades, columns=[
    "EMA_short", "EMA_long", "Entry_Date", "Exit_Date", "Trade_Type",
    "Entry_Price", "Exit_Price", "PnL"
])
trades_df.to_csv("all_trades.csv", index=False)

# -----------------------------
# Save summary
# -----------------------------
summary_df = pd.DataFrame(summary, columns=[
    "EMA_short", "EMA_long", "Total_Trades", "Profit_Trades", "Loss_Trades", "Net_Profit"
])
summary_df.to_csv("ema_optimization_summary.csv", index=False)

# -----------------------------
# Print best EMA pair
# -----------------------------
best_row = summary_df.loc[summary_df["Net_Profit"].idxmax()]
print(f"✅ Best EMA pair: ({best_row['EMA_short']}, {best_row['EMA_long']}) → Net Profit: ₹{best_row['Net_Profit']:,}")
