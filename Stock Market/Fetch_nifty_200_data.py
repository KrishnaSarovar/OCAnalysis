import yfinance as yf
import pandas as pd
import time
import os

# ----------------------------------
# 1️⃣ Fetch NIFTY 200 Symbol List
# ----------------------------------
nifty200_url = "https://archives.nseindia.com/content/indices/ind_nifty200list.csv"
nifty200 = pd.read_csv(nifty200_url)
symbols = nifty200['Symbol'].tolist()

print(f"✅ Total NIFTY 200 stocks found: {len(symbols)}")

# Create folder for saving data
os.makedirs("nifty200_data", exist_ok=True)

# ----------------------------------
# 2️⃣ Download Historical Data & Apply EMA
# ----------------------------------
start_date = "2010-01-01"
end_date = "2025-10-20"

# Loop through all symbols
failed = []
for i, sym in enumerate(symbols, 1):
    try:
        yahoo_symbol = sym + ".NS"  # Yahoo Finance format for NSE stocks
        print(f"[{i}/{len(symbols)}] 📥 Downloading {sym}...")
        
        df = yf.download(yahoo_symbol, start=start_date, end=end_date, progress=False)
        if df.empty:
            print(f"⚠️ No data for {sym}")
            failed.append(sym)
            continue
        
        # Compute EMAs
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        
        # Save to CSV
        file_path = f"nifty200_data/{sym}_data.csv"
        df.to_csv(file_path)
        print(f"💾 Saved {sym} → {file_path}")
        
        time.sleep(1)  # small delay to avoid rate limiting
        
    except Exception as e:
        print(f"❌ Error for {sym}: {e}")
        failed.append(sym)
        continue

# ----------------------------------
# 3️⃣ Summary
# ----------------------------------
print("\n✅ Download completed!")
if failed:
    print(f"⚠️ Failed symbols ({len(failed)}): {failed}")
else:
    print("🎉 All symbols downloaded successfully!")
