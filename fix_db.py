from sqlalchemy import text
from database_manager import engine

def update_schema():
    try:
        with engine.connect() as conn:
            # This SQL command adds the missing column to your table
            conn.execute(text('ALTER TABLE trade_history ADD COLUMN "Target_Price" FLOAT;'))
            conn.commit()
        print("[+] Successfully added Target_Price to your PostgreSQL database!")
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    update_schema()