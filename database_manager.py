import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv

# Load the hidden password securely
load_dotenv()
db_password = os.getenv("DB_PASSWORD")
engine = create_engine(f'postgresql://postgres:{db_password}@localhost:5432/wealth_db')

def log_trade(ticker, shares, entry_price, stop_loss, target, capital_risked):
    """Saves valid setups permanently to the database."""
    trade_data = {
        'Date': [datetime.now().date()],
        'Ticker': [ticker],
        'Shares': [shares],
        'Entry_Price': [entry_price],
        'Stop_Loss': [stop_loss],
        'Target_Price': [target], 
        'Capital_Risked': [capital_risked],
        'Status': ['OPEN']
    }
    
    df = pd.DataFrame(trade_data)
    try:
        df.to_sql('trade_history', engine, if_exists='append', index=False)
        print(f"[+] Logged {ticker} to wealth_db!")
    except Exception as e:
        print(f"[-] Database Error: {e}")