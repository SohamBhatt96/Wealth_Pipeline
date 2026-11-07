import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# 1. Load variables from the .env file into the system
load_dotenv()

# 2. Fetch the secure password
db_password = os.getenv("DB_PASSWORD")

# 3. Create your SQLAlchemy engine string dynamically
# (Update 'postgres' and 'wealth_pipeline' to match your actual local DB user and name)
engine_url = f"postgresql://postgres:{db_password}@localhost:5432/wealth_pipeline"
engine = create_engine(engine_url)
def log_trade(ticker, strategy, atr, shares, entry_price, stop_loss, take_profit, total_value):
    try:
        with engine.connect() as conn:
            # Checks ONLY today's date to prevent same-day duplicates while allowing future signals
            check_query = text("""
                SELECT COUNT(*) FROM public.trade_history 
                WHERE TRIM("Ticker") = TRIM(:ticker) AND "Date"::date = CURRENT_DATE
            """)
            result = conn.execute(check_query, {"ticker": ticker}).scalar()

            if result == 0:
                insert_query = text("""
                    INSERT INTO public.trade_history 
                    ("Date", "Ticker", "Shares", "Entry_Price", "Stop_Loss", "Capital_Risked", "Status", "Target_Price", strategy, atr) 
                    VALUES (CURRENT_DATE, :ticker, :shares, :entry, :sl, :val, 'OPEN', :tp, :strategy, :atr)
                """)
                
                conn.execute(insert_query, {
                    "ticker": ticker,
                    "shares": int(shares),
                    "entry": float(entry_price),
                    "sl": float(stop_loss),
                    "val": float(total_value),
                    "tp": float(take_profit),
                    "strategy": strategy,
                    "atr": float(atr)
                })
                conn.commit()
                logging.info(f"Successfully logged new trade for {ticker}.")
            else:
                logging.info(f"Trade for {ticker} already exists for TODAY. Skipping duplicate.")
                
    except Exception as e:
        logging.error(f"Database Error for {ticker}: {e}")