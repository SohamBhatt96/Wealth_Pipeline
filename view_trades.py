import pandas as pd
from database_manager import engine
from rich.console import Console
from rich.table import Table
from rich import box

def view_portfolio():
    console = Console()
    console.print("\n[bold cyan][*] Connecting to PostgreSQL database...[/bold cyan]\n")
    try:
        # Fetch the trades from your database
        query = 'SELECT * FROM trade_history ORDER BY "Date" DESC;'
        df = pd.read_sql(query, engine)
        
        if df.empty:
            console.print("[bold yellow]The database is currently empty. No setups found yet.[/bold yellow]")
        else:
            # Create a customized, colored terminal table
            table = Table(
                title="📊 WEALTH PIPELINE: SAVED TRADE SETUPS", 
                box=box.ROUNDED, 
                header_style="bold magenta",
                title_style="bold green"
            )
            
            # Dynamically add the column headers (Ticker, Shares, Target_Price, etc.)
            for col in df.columns:
                table.add_column(col, justify="center")
                
            # Populate the table with your actual trade data
            for _, row in df.iterrows():
                row_data = [str(val) for val in row]
                table.add_row(*row_data)
                
            # Print the final visual to the terminal
            console.print(table)
            console.print("\n")
            
    except Exception as e:
        console.print(f"[bold red][-] Could not read the database: {e}[/bold red]")

if __name__ == "__main__":
    view_portfolio()