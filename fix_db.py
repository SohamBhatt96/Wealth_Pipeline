import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DB_PASS = os.getenv("DB_PASSWORD")
DATABASE_URL = f"postgresql://postgres:{DB_PASS}@localhost:5432/wealth_db"
engine = create_engine(DATABASE_URL)

try:
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE public.trade_history ADD COLUMN IF NOT EXISTS strategy VARCHAR(50);"))
        connection.execute(text("ALTER TABLE public.trade_history ADD COLUMN IF NOT EXISTS atr NUMERIC;"))
    print("Database columns added successfully!")
except Exception as e:
    print(f"Error updating database: {e}")