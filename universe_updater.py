import pandas as pd
import json
import os
from curl_cffi import requests

def update_nse_universes():
    print("[*] Connecting to NSE servers to fetch latest index constituents...")
    session = requests.Session(impersonate="chrome")
    
    nse_indices = {
        "Nifty 50": "https://archives.nseindia.com/content/indices/ind_nifty50list.csv",
        "Nifty 100": "https://archives.nseindia.com/content/indices/ind_nifty100list.csv",
        "Nifty Bank": "https://archives.nseindia.com/content/indices/ind_niftybanklist.csv",
        "Nifty IT": "https://archives.nseindia.com/content/indices/ind_niftyitlist.csv"
    }
    
    new_universes = {}
    
    for name, url in nse_indices.items():
        try:
            response = session.get(url)
            with open('temp_index.csv', 'wb') as f:
                f.write(response.content)
            
            df = pd.read_csv('temp_index.csv')
            tickers = [f"{symbol.strip()}.NS" for symbol in df['Symbol'].tolist()]
            new_universes[name] = tickers
            print(f"[+] Rebuilt {name} ({len(tickers)} stocks)")
        except Exception as e:
            print(f"[-] Failed to update {name}: {e}")
            
    if os.path.exists('temp_index.csv'):
        os.remove('temp_index.csv')
            
    with open('universes.json', 'w') as f:
        json.dump(new_universes, f, indent=4)
    print("\n[+] universes.json generated successfully!")

if __name__ == "__main__":
    update_nse_universes()