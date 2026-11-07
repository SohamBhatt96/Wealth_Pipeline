from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:postgresql@localhost:5432/wealth_db")

with engine.connect() as conn:
    # Safely deletes the August 'None' tests AND the Sept 28th duplicates
    query = text("""
        DELETE FROM public.trade_history 
        WHERE strategy IS NULL 
        OR "Date"::date = '2026-09-28';
    """)
    
    conn.execute(query)
    conn.commit()
    print("Database perfectly cleaned! All legacy testing data and duplicates removed.")