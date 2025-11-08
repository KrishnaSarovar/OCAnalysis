# import pandas as pd
# import matplotlib.pyplot as plt

# # ---------------------------------------
# # 1️⃣ Load NIFTY data with EMA columns
# # ---------------------------------------
# df = pd.read_csv("nifty_data_with_ema.csv")

# # Clean up any extra spaces
# df.columns = df.columns.str.strip()

# # Convert Date to datetime
# df["Date"] = pd.to_datetime(df["Date"])

# # ---------------------------------------
# # 2️⃣ Create Signals and Detect Crossovers
# # ---------------------------------------
# df["Signal"] = 0
# df.loc[df["EMA20"] > df["EMA50"], "Signal"] = 1   # Bullish
# df.loc[df["EMA20"] < df["EMA50"], "Signal"] = -1  # Bearish

# # Detect points where signal changes (crossovers)
# df["Crossover"] = df["Signal"].diff()

# # Keep only crossover points
# crosses = df[df["Crossover"] != 0][["Date", "Signal", "Crossover"]].copy()
# crosses.reset_index(drop=True, inplace=True)

# # ---------------------------------------
# # 3️⃣ Calculate Duration Between Crossovers
# # ---------------------------------------
# crosses["Next_Crossover_Date"] = crosses["Date"].shift(-1)
# crosses["Duration_Days"] = (crosses["Next_Crossover_Date"] - crosses["Date"]).dt.days
# crosses["Trade_Type"] = crosses["Signal"].map({1: "Buy", -1: "Sell"})

# # Remove last row (no next crossover)
# crosses = crosses.dropna(subset=["Next_Crossover_Date"])

# # Save results
# crosses.to_csv("nifty_crossover_durations.csv", index=False)

# # ---------------------------------------
# # 4️⃣ Summary Statistics
# # ---------------------------------------
# avg_buy_duration = crosses.loc[crosses["Trade_Type"] == "Buy", "Duration_Days"].mean()
# avg_sell_duration = crosses.loc[crosses["Trade_Type"] == "Sell", "Duration_Days"].mean()
# overall_avg_duration = crosses["Duration_Days"].mean()

# print("✅ Trade Duration Summary")
# print("-" * 35)
# print(f"📈 Average BUY trade duration : {avg_buy_duration:.1f} days")
# print(f"📉 Average SELL trade duration: {avg_sell_duration:.1f} days")
# print(f"🧮 Overall average duration    : {overall_avg_duration:.1f} days")

# # ---------------------------------------
# # 5️⃣ Visualization
# # ---------------------------------------
# # Map trade type to color safely
# colors = crosses["Trade_Type"].map({"Buy": "green", "Sell": "red"})
# colors = colors.fillna("gray")  # fallback color for any NaN

# plt.figure(figsize=(12,6))
# plt.bar(crosses["Date"], crosses["Duration_Days"], color=colors, alpha=0.6)
# plt.title("Duration Between EMA Crossovers (in Days)")
# plt.xlabel("Crossover Date")
# plt.ylabel("Days in Trade")
# plt.grid(True, linestyle="--", alpha=0.6)
# plt.show()

import pandas as pd

# -----------------------------
# 1️⃣ Load NIFTY data
# -----------------------------
df = pd.read_csv("nifty_data_with_ema.csv")
df.columns = df.columns.str.strip()
df["Date"] = pd.to_datetime(df["Date"])

# -----------------------------
# 2️⃣ Create signals
# -----------------------------
df["Signal"] = 0
df.loc[df["EMA20"] > df["EMA50"], "Signal"] = 1   # Bullish
df.loc[df["EMA20"] < df["EMA50"], "Signal"] = -1  # Bearish

df["Crossover"] = df["Signal"].diff()

# -----------------------------
# 3️⃣ Extract crossovers
# -----------------------------
crosses = df[df["Crossover"] != 0][["Date", "Signal", "Crossover"]].copy()
crosses.reset_index(drop=True, inplace=True)

# Map trade type
crosses["Trade_Type"] = crosses["Signal"].map({1: "Buy", -1: "Sell"})

# Calculate holding period per trade (days)
crosses["Next_Crossover_Date"] = crosses["Date"].shift(-1)
crosses["Holding_Period_Days"] = (crosses["Next_Crossover_Date"] - crosses["Date"]).dt.days

# Drop the last row (no next crossover)
crosses = crosses.dropna(subset=["Next_Crossover_Date"]).reset_index(drop=True)

# -----------------------------
# 4️⃣ Save results
# -----------------------------
crosses.to_csv("nifty_trade_holding_periods.csv", index=False)

print(f"✅ Holding period per trade calculated for {len(crosses)} trades")
print(crosses.head(10))
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Load processed trade holding period CSV
# -----------------------------
crosses = pd.read_csv("nifty_trade_holding_periods.csv")
crosses["Date"] = pd.to_datetime(crosses["Date"])

# Map Trade_Type to colors
colors = crosses["Trade_Type"].map({"Buy": "green", "Sell": "red"}).fillna("gray")

# -----------------------------
# Plot holding period per trade
# -----------------------------
plt.figure(figsize=(14,6))
plt.bar(crosses["Date"], crosses["Holding_Period_Days"], color=colors, alpha=0.7)

plt.title("NIFTY 50: Holding Period per Trade (EMA 20/50 Strategy)")
plt.xlabel("Trade Entry Date")
plt.ylabel("Holding Period (Days)")
plt.grid(True, linestyle="--", alpha=0.5)

# Add legend manually
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='green', label='Buy'),
                   Patch(facecolor='red', label='Sell')]
plt.legend(handles=legend_elements)

plt.show()
