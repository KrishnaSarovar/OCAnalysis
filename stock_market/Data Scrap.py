# # We want to get the Nifty Indices data from 01-01-2001.
# import yfinance as yf
# import pandas as pd
# import matplotlib.pyplot as plt

# # Fetch Historical NIFTY Data
# symbol = "^NSEI" #Nifty 50 Index

# start_date = "1999-01-01"
# end_date = "2025-10-20"

# print("Downloading NIFTY 50 data.....")
# nifty = yf.download(symbol,start=start_date,end=end_date)

# #Ensure we have volume and price columns
# print("Data fetched:",nifty.shape)
# print(nifty.head())

# #save raw data as CSV
# csv_path = "nifty_data.csv"
# nifty.to_csv(csv_path)

# # Compute 20 & 50 day EMA
# nifty["EMA20"] = nifty["Close"].ewm(span=20, adjust=False).mean()
# nifty["EMA50"] = nifty["Close"].ewm(span=50,adjust=False).mean()

# # Save again with EMA's
# nifty.to_csv("nifty_data_with_ema.csv")

# print("📊 Added EMA20 & EMA50 columns → nifty_data_with_ema.csv")

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# 1️⃣ Fetch Historical NIFTY Data
# -----------------------------
symbol = "^NSEI"  # NIFTY 50 index
start_date = "1999-01-01"
end_date = "2025-10-20"

print("📥 Downloading NIFTY 50 data...")
nifty = yf.download(symbol, start=start_date, end=end_date, auto_adjust=False)

print("✅ Data fetched:", nifty.shape)

# --------------------------------
# 2️⃣ Handle MultiIndex Columns if Any
# --------------------------------
if isinstance(nifty.columns, pd.MultiIndex):
    nifty.columns = [col[0] for col in nifty.columns]  # flatten level 0
    print("🧹 Flattened MultiIndex columns:", list(nifty.columns))

# --------------------------------
# 3️⃣ Compute 20- & 50-day EMA
# --------------------------------
nifty["EMA20"] = nifty["Close"].ewm(span=20, adjust=False).mean()
nifty["EMA50"] = nifty["Close"].ewm(span=50, adjust=False).mean()

# --------------------------------
# 4️⃣ Reset index so Date becomes a column
# --------------------------------
nifty.reset_index(inplace=True)

# --------------------------------
# 5️⃣ Save Clean CSV
# --------------------------------
csv_path = "nifty_data_with_ema.csv"
nifty.to_csv(csv_path, index=False)

print(f"💾 Clean file saved to: {csv_path}")
print("✅ Columns in saved file:", list(nifty.columns))

# --------------------------------
# 6️⃣ Optional: Quick Visual Check
# --------------------------------
plt.figure(figsize=(12,6))
plt.plot(nifty["Date"], nifty["Close"], label="Close Price", linewidth=1.2)
plt.plot(nifty["Date"], nifty["EMA20"], label="20-day EMA", linewidth=1.0)
plt.plot(nifty["Date"], nifty["EMA50"], label="50-day EMA", linewidth=1.0)
plt.title("NIFTY 50 with 20 & 50-day EMA")
plt.xlabel("Date")
plt.ylabel("Price (INR)")
plt.legend()
plt.grid(True)
plt.show()

