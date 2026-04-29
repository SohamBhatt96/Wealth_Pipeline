import pandas as pd
from sqlalchemy import create_engine

print("--- Step 1: Data Extraction ---")
# This is where 'df' is created!
df = pd.read_csv('raw_trades.csv')
print("Raw data loaded successfully.")

print("\n--- Step 2: Data Transformation ---")
# 1. Clean hidden spaces
df['Ticker'] = df['Ticker'].str.strip()
df['Strategy'] = df['Strategy'].str.strip()

# 2. Fix the dates for SQL
df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

# 3. Rename columns to match your pgAdmin database schema exactly
df = df.rename(columns={
    'Date': 'entry_date',  # <--- Matched to your database!
    'Ticker': 'ticker',
    'Strategy': 'setup_type',
    'Profit_Loss': 'net_profit',
    'Risk_Amount': 'initial_risk',
    'Fees': 'brokerage_and_taxes'
})
print("Data cleaned and standardized.")

print("\n--- Step 3: Database Load ---")
# TODO: Just put your pgAdmin password here!
DB_PASSWORD = 'postgresql'  
DB_NAME = 'trading_portfolio'      
DB_USER = 'postgres'                

try:
    print("Connecting to PostgreSQL...")
    # This creates the "bridge" to your local database
    connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}'
    engine = create_engine(connection_string)
    
    # Push the clean dataframe directly into your 'swing_trades' table
    df.to_sql('swing_trades', engine, if_exists='append', index=False)
    
    print("✅ SUCCESS: Pipeline complete! Trades uploaded to database.")
    
except Exception as e:
    print(f"❌ ERROR: Could not upload. Details: {e}")