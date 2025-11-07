# collector_push_to_supabase.py
import os
import time
import random
import requests
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# -------------------------------
# CONFIG (use env vars in CI)
# -------------------------------
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
SYMBOL = os.environ.get("SYMBOL", "NIFTY")  # NIFTY/BANKNIFTY etc.

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# Fetch NSE Option Chain Data
# -------------------------------
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
            session.get("https://www.nseindia.com", headers=headers, timeout=30)
            time.sleep(random.uniform(3, 5))  # polite delay

            response = session.get(url, headers=headers, timeout=30)

            # Handle blank or invalid response
            if not response.text.strip():
                raise ValueError("Empty response from NSE")

            if response.text.strip().startswith("<"):
                raise ValueError("Received HTML instead of JSON (likely blocked)")

            data = response.json()
            records = data.get("records", {}).get("data", [])
            underlying_value = data.get("records", {}).get("underlyingValue", 0)

            rows = []
            for record in records:
                strike = record.get("strikePrice")
                expiry = record.get("expiryDate")
                ce = record.get("CE", {})
                pe = record.get("PE", {})

                rows.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "symbol": symbol,
                    "expiry": expiry,
                    "strike_price": strike,
                    "underlying": underlying_value,
                    "ce_oi": ce.get("openInterest"),
                    "ce_chg_oi": ce.get("changeinOpenInterest"),
                    "ce_ltp": ce.get("lastPrice"),
                    "pe_oi": pe.get("openInterest"),
                    "pe_chg_oi": pe.get("changeinOpenInterest"),
                    "pe_ltp": pe.get("lastPrice"),
                })

            df = pd.DataFrame(rows)
            print(f"✅ Fetched {len(df)} option strikes for {symbol}")
            return df

        except Exception as e:
            print(f"⚠️ Attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(3)

    print("❌ Failed to fetch NSE Option Chain after multiple attempts.")
    return pd.DataFrame()

# -------------------------------
# Push to Supabase
# -------------------------------
def push_to_supabase(df: pd.DataFrame):
    if df.empty:
        print("⚠️ No data to push.")
        return

    rows = df.to_dict(orient="records")

    try:
        response = supabase.table("option_ticks").insert(rows).execute()
        print(f"✅ Pushed {len(rows)} rows to Supabase at {datetime.utcnow().isoformat()}")
    except Exception as e:
        print("❌ Supabase insert error:", e)

# -------------------------------
# Main Execution
# -------------------------------
if __name__ == "__main__":
    df = fetch_option_chain(SYMBOL)
    push_to_supabase(df)
