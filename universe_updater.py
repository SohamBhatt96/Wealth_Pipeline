import pandas as pd
import json
import os
import time
from curl_cffi import requests

def update_nse_universes():
    print("[*] Connecting to NSE servers to fetch LIVE index constituents...")
    # Impersonate a real Chrome browser to bypass NSE firewall
    session = requests.Session(impersonate="chrome")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com/"
    }
    session.headers.update(headers)
    
    try:
        print("[-] Bypassing firewall: Fetching initial session cookies...")
        session.get("https://www.nseindia.com", timeout=10)
        time.sleep(2) # Pause to act like a human
    except Exception as e:
        print(f"[-] Cookie fetch failed: {e}")

    nse_indices = {
        "Nifty 50": "https://archives.nseindia.com/content/indices/ind_nifty50list.csv",
        "Nifty 100": "https://archives.nseindia.com/content/indices/ind_nifty100list.csv",
        "Nifty Bank": "https://archives.nseindia.com/content/indices/ind_niftybanklist.csv",
        "Nifty IT": "https://archives.nseindia.com/content/indices/ind_niftyitlist.csv"
    }
    
    new_universes = {}
    
    for name, url in nse_indices.items():
        try:
            response = session.get(url, timeout=10)
            
            # Safety Check: Did NSE send us the CSV or an error webpage?
            if b'Symbol' not in response.content:
                print(f"[-] Blocked by NSE for {name}. They returned HTML instead of data.")
                continue
                
            with open('temp_index.csv', 'wb') as f:
                f.write(response.content)
            
            df = pd.read_csv('temp_index.csv')
            # Extract live symbols and append .NS for Yahoo Finance
            tickers = [f"{symbol.strip()}.NS" for symbol in df['Symbol'].tolist()]
            new_universes[name] = tickers
            print(f"[+] Successfully fetched LIVE {name} ({len(tickers)} stocks)")
            
        except Exception as e:
            print(f"[-] Failed to update {name}: {e}")
            
    if os.path.exists('temp_index.csv'):
        os.remove('temp_index.csv')
            
    # Final Safety Net: Only save if we actually got live data
    if not new_universes:
        print("\n[!] ERROR: NSE blocked the requests. No files were overwritten.")
    else:
        with open('universes.json', 'w') as f:
            json.dump(new_universes, f, indent=4)
        print("\n[+] Live universes.json generated successfully!")

if __name__ == "__main__":
    update_nse_universes()