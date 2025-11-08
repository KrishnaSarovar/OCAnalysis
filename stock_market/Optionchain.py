# # """
# # nse_option_chain_selenium.py

# # Scrapes NSE option-chain JSON using undetected-chromedriver and appends results to CSV.
# # Adjust SYMBOL, INTERVAL_SECS, OUTPUT_CSV, and WRITE_EXCEL flags as needed.
# # """

# # import time
# # import random
# # import csv
# # import sys
# # from datetime import datetime
# # import pandas as pd

# # import undetected_chromedriver as uc
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC

# # # ---------------------------
# # # Config
# # # ---------------------------
# # SYMBOL = "NIFTY"              # "NIFTY" or "BANKNIFTY" or other index symbol NSE accepts
# # INTERVAL_SECS = 60            # polling interval in seconds
# # OUTPUT_CSV = f"{SYMBOL}_option_chain_live.csv"
# # WRITE_EXCEL = True            # if True will write an Excel snapshot each cycle (openpyxl required)
# # OUTPUT_XLSX = f"{SYMBOL}_option_chain_live.xlsx"

# # # Optionally add a proxy if you want (format: "host:port" or "http://user:pass@host:port")
# # PROXY = None  # e.g. "http://user:pass@12.34.56.78:8000" or None to not use proxy

# # # Browser visibility: set headless=False to watch browser; True runs headless (less reliable)
# # HEADLESS = True

# # # ---------------------------
# # # Helpers
# # # ---------------------------
# # def init_driver(headless=HEADLESS, proxy=None):
# #     options = uc.ChromeOptions()
# #     if headless:
# #         options.add_argument("--headless=new")
# #         options.add_argument("--disable-gpu")
# #     # basic options to look like a real user
# #     options.add_argument("--no-sandbox")
# #     options.add_argument("--disable-dev-shm-usage")
# #     options.add_argument("--disable-blink-features=AutomationControlled")
# #     options.add_argument("--disable-infobars")
# #     options.add_argument("--lang=en-US")
# #     # optional proxy
# #     if proxy:
# #         options.add_argument(f'--proxy-server={proxy}')
# #     # random minor UA tweaks are handled by undetected_chromedriver
# #     driver = uc.Chrome(options=options)
# #     driver.set_page_load_timeout(30)
# #     return driver

# # def append_rows_to_csv(csv_path, rows, fieldnames):
# #     write_header = False
# #     try:
# #         with open(csv_path, "r", newline="", encoding="utf-8") as f:
# #             pass
# #     except FileNotFoundError:
# #         write_header = True

# #     with open(csv_path, "a", newline="", encoding="utf-8") as f:
# #         writer = csv.DictWriter(f, fieldnames=fieldnames)
# #         if write_header:
# #             writer.writeheader()
# #         for r in rows:
# #             writer.writerow(r)

# # def write_excel_from_csv(csv_path, xlsx_path):
# #     # convert CSV to Excel snapshot
# #     df = pd.read_csv(csv_path)
# #     df.to_excel(xlsx_path, index=False)

# # # ---------------------------
# # # Fetcher using page JS fetch (same-origin - uses session cookies)
# # # ---------------------------
# # def fetch_option_chain_via_browser(driver, symbol):
# #     """
# #     Loads the NSE option-chain page (to get cookies) then executes a fetch()
# #     for the API endpoint in page context, returning Python dict (JSON).
# #     """
# #     base_url = "https://www.nseindia.com"
# #     page_url = f"{base_url}/option-chain"
# #     api_url = f"{base_url}/api/option-chain-indices?symbol={symbol}"

# #     # 1) load homepage to obtain cookies (some sites require this)
# #     driver.get(base_url)
# #     # short randomized wait so cookies set
# #     time.sleep(1.0 + random.random()*1.5)

# #     # 2) load option-chain page (this often sets additional cookies/headers)
# #     driver.get(page_url)
# #     # wait until some page element appears or short sleep
# #     try:
# #         WebDriverWait(driver, 10).until(
# #             EC.presence_of_element_located((By.TAG_NAME, "body"))
# #         )
# #     except Exception:
# #         # page may still be fine; continue
# #         pass
# #     time.sleep(1.0 + random.random()*1.0)

# #     # 3) fetch JSON using the browser context (so cookies and headers are included)
# #     js = f"""
# #     const url = "{api_url}";
# #     return fetch(url, {{ method: 'GET', credentials: 'include' }})
# #       .then(async resp => {{
# #           const txt = await resp.text()
# #           try {{ return JSON.parse(txt); }} catch(e) {{ return {{__raw: txt, __status: resp.status}}; }}
# #       }})
# #       .catch(err => {{ return {{__error: String(err)}}, null }});
# #     """
# #     result = driver.execute_script(js)
# #     return result

# # # ---------------------------
# # # Main loop
# # # ---------------------------
# # def main():
# #     print(f"🚀 Starting NSE Option Chain scraping for {SYMBOL} every {INTERVAL_SECS} sec...")
# #     driver = None
# #     try:
# #         driver = init_driver(headless=HEADLESS, proxy=PROXY)

# #         all_fieldnames = [
# #             "timestamp", "symbol", "expiry", "strikePrice",
# #             "CE_LTP", "CE_change", "CE_totalTradedVolume", "CE_openInterest", "CE_changeinOpenInterest",
# #             "PE_LTP", "PE_change", "PE_totalTradedVolume", "PE_openInterest", "PE_changeinOpenInterest"
# #         ]

# #         while True:
# #             ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #             try:
# #                 data = fetch_option_chain_via_browser(driver, SYMBOL)
# #                 # if blocked, data might be dict with __raw or __error or status
# #                 if not data or isinstance(data, dict) and ("__error" in data or "__raw" in data):
# #                     raise ValueError(f"Invalid/empty JSON returned: {data}")

# #                 records = data.get("records", {}).get("data", [])
# #                 rows = []
# #                 for rec in records:
# #                     strike = rec.get("strikePrice")
# #                     expiry = rec.get("expiryDate") or rec.get("expiry")
# #                     ce = rec.get("CE") or {}
# #                     pe = rec.get("PE") or {}
# #                     rows.append({
# #                         "timestamp": ts,
# #                         "symbol": SYMBOL,
# #                         "expiry": expiry,
# #                         "strikePrice": strike,
# #                         "CE_LTP": ce.get("lastPrice"),
# #                         "CE_change": ce.get("change"),
# #                         "CE_totalTradedVolume": ce.get("totalTradedVolume"),
# #                         "CE_openInterest": ce.get("openInterest"),
# #                         "CE_changeinOpenInterest": ce.get("changeinOpenInterest"),
# #                         "PE_LTP": pe.get("lastPrice"),
# #                         "PE_change": pe.get("change"),
# #                         "PE_totalTradedVolume": pe.get("totalTradedVolume"),
# #                         "PE_openInterest": pe.get("openInterest"),
# #                         "PE_changeinOpenInterest": pe.get("changeinOpenInterest"),
# #                     })

# #                 if rows:
# #                     append_rows_to_csv(OUTPUT_CSV, rows, all_fieldnames)
# #                     if WRITE_EXCEL:
# #                         # write snapshot Excel (overwrites each cycle; keeps CSV as append-log)
# #                         write_excel_from_csv(OUTPUT_CSV, OUTPUT_XLSX)
# #                     print(f"✅ {ts}: saved {len(rows)} strikes (to {OUTPUT_CSV})")
# #                 else:
# #                     print(f"⚠️ {ts}: no rows returned from NSE payload")

# #             except Exception as e:
# #                 print(f"⚠️ Error fetching data: {e}")

# #             # wait interval
# #             print(f"⏳ Waiting {INTERVAL_SECS} seconds before next fetch...\n")
# #             time.sleep(INTERVAL_SECS)

# #     except KeyboardInterrupt:
# #         print("⏹️ Stopped by user (KeyboardInterrupt).")
# #     except Exception as e:
# #         print(f"Fatal error initialising driver or main loop: {e}")
# #     finally:
# #         try:
# #             if driver:
# #                 driver.quit()
# #         except Exception:
# #             pass

# # if __name__ == "__main__":
# #     main()


# import time
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from datetime import datetime
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# def setup_driver():
#     chrome_options = Options()
#     chrome_options.add_argument("--headless=new")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--window-size=1920,1080")

#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     driver.set_page_load_timeout(30)
#     return driver

# driver = setup_driver()

# # -------------------------------
# # 2️⃣ Scrape Option Chain Table
# # -------------------------------
# def fetch_option_chain(symbol="NIFTY"):
#     driver = setup_driver()
#     url = f"https://www.nseindia.com/option-chain?symbol={symbol}"
#     driver.get(url)

#     try:
#         # Wait up to 20 seconds for the table to appear
#         wait = WebDriverWait(driver, 20)
#         table = wait.until(
#             EC.presence_of_element_located((By.XPATH, "//table[contains(@class,'option-chain-table')]"))
#         )

#         rows = table.find_elements(By.TAG_NAME, "tr")
#         data = []
#         headers = [th.text for th in rows[0].find_elements(By.TAG_NAME, "th")]

#         for row in rows[1:]:
#             cols = [td.text for td in row.find_elements(By.TAG_NAME, "td")]
#             if len(cols) == len(headers):
#                 data.append(cols)

#         df = pd.DataFrame(data, columns=headers)
#         print(f"✅ Successfully fetched {len(df)} rows from {symbol} Option Chain")

#         driver.quit()
#         return df

#     except Exception as e:
#         print(f"⚠️ Error parsing Option Chain: {e}")
#         driver.quit()
#         return None

# # -------------------------------
# # 3️⃣ Save to Excel
# # -------------------------------
# def save_to_excel(df, filename="nifty_option_chain.xlsx"):
#     try:
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         df["Timestamp"] = timestamp
#         with pd.ExcelWriter(filename, mode="a", if_sheet_exists="overlay", engine="openpyxl") as writer:
#             df.to_excel(writer, sheet_name="Data", index=False, startrow=writer.sheets["Data"].max_row if "Data" in writer.sheets else 0, header=False)
#         print(f"✅ Data appended successfully at {timestamp}")
#     except FileNotFoundError:
#         # Create new file
#         df.to_excel(filename, sheet_name="Data", index=False)
#         print(f"✅ File created and data saved at {timestamp}")

# # -------------------------------
# # 4️⃣ Loop every 1 minute
# # -------------------------------
# def run_scraper(interval=60):
#     print(f"🚀 Starting NSE Option-Chain scraping for NIFTY every {interval} sec...")

#     while True:
#         df = fetch_option_chain("NIFTY")
#         if df is not None and not df.empty:
#             save_to_excel(df)
#         else:
#             print("⚠️ No data fetched or empty dataframe.")
#         print(f"⏳ Waiting {interval} seconds before next fetch...\n")
#         time.sleep(interval)

# # -------------------------------
# # Run
# # -------------------------------
# if __name__ == "__main__":
#     run_scraper(interval=300)


import requests
import pandas as pd
import time
from datetime import datetime

# -------------------------------
# 1️⃣ Get Option Chain JSON safely
# -------------------------------
def fetch_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://www.nseindia.com/option-chain?symbol={symbol}",
    }

    try:
        session = requests.Session()
        # get cookies first from homepage (important)
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        response = session.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"⚠️ NSE returned status {response.status_code}")
            return None

        data = response.json()
        records = data.get("records", {}).get("data", [])
        rows = []

        for record in records:
            strike = record.get("strikePrice")
            expiry = record.get("expiryDate")

            ce = record.get("CE", {})
            pe = record.get("PE", {})

            rows.append({
                "Expiry": expiry,
                "StrikePrice": strike,
                "CE_OpenInterest": ce.get("openInterest"),
                "CE_ChangeInOI": ce.get("changeinOpenInterest"),
                "CE_Volume": ce.get("totalTradedVolume"),
                "CE_LTP": ce.get("lastPrice"),
                "PE_OpenInterest": pe.get("openInterest"),
                "PE_ChangeInOI": pe.get("changeinOpenInterest"),
                "PE_Volume": pe.get("totalTradedVolume"),
                "PE_LTP": pe.get("lastPrice"),
            })

        df = pd.DataFrame(rows)
        print(f"✅ Successfully fetched {len(df)} rows for {symbol}")
        return df

    except Exception as e:
        print(f"⚠️ Error fetching data: {e}")
        return None


# -------------------------------
# 2️⃣ Save to Excel
# -------------------------------
def save_to_excel(df, filename="nifty_option_chain.xlsx"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df["Timestamp"] = timestamp

    try:
        with pd.ExcelWriter(filename, mode="a", if_sheet_exists="overlay", engine="openpyxl") as writer:
            startrow = writer.sheets["Data"].max_row if "Data" in writer.sheets else 0
            df.to_excel(writer, sheet_name="Data", index=False, startrow=startrow, header=(startrow == 0))
        print(f"✅ Appended data at {timestamp}")
    except FileNotFoundError:
        df.to_excel(filename, sheet_name="Data", index=False)
        print(f"✅ Created new file and saved data at {timestamp}")


# -------------------------------
# 3️⃣ Run scraper every 5 min
# -------------------------------
def run_scraper(interval=60):
    print(f"🚀 Starting NSE Option Chain scraping for NIFTY every {interval} sec...")
    while True:
        df = fetch_option_chain("NIFTY")
        if df is not None and not df.empty:
            save_to_excel(df)
        else:
            print("⚠️ No data fetched or empty dataframe.")
        print(f"⏳ Waiting {interval} seconds before next fetch...\n")
        time.sleep(interval)


if __name__ == "__main__":
    run_scraper(interval=60)
