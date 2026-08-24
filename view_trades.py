import pandas as pd
from database_manager import engine

def view_portfolio():
    print("\nConnecting to PostgreSQL database...\n")
    try:
        # Fetch everything from the trade_history table, newest trades first
        query = 'SELECT * FROM trade_history ORDER BY "Date" DESC;'
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("The database is currently empty. No setups found yet.")
        else:
            print("="*90)
            print(" 📊 WEALTH PIPELINE: SAVED TRADE SETUPS")
            print("="*90)
            # .to_string() prints the entire dataframe cleanly in the terminal
            print(df.to_string(index=False))
            print("="*90 + "\n")
            
    except Exception as e:
        print(f"[-] Could not read the database: {e}")

if __name__ == "__main__":
    view_portfolio()