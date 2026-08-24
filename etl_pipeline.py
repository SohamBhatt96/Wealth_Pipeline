import pandas as pd
from sqlalchemy import create_engine
import numpy as np

# 1. Connect to Database
# Password successfully updated to 'postgresql'
db_url = 'postgresql://postgres:postgresql@localhost:5432/wealth_db'
engine = create_engine(db_url)

# 2. Extract Data: Pull everything we need for deep analytics
query = """
    SELECT "Date", "Ticker", "Strategy", "Profit_Loss", "Risk_Amount", "Fees" 
    FROM stock_history 
    ORDER BY "Date" ASC;
"""
df = pd.read_sql(query, engine)

# 3. Transform: Calculate the Deep Analytics

# Total Trades
total_trades = len(df)

# Win Rate
winning_trades = df[df['Profit_Loss'] > 0]
losing_trades = df[df['Profit_Loss'] <= 0]
win_rate = (len(winning_trades) / total_trades) * 100

# Average Winner & Loser
avg_win = winning_trades['Profit_Loss'].mean()
avg_loss = losing_trades['Profit_Loss'].mean()

# Realized Risk-to-Reward Ratio (RR)
# We use 'abs' to turn the negative average loss into a positive number for the ratio
if pd.isna(avg_loss) or avg_loss == 0:
    realized_rr = float('inf') # Prevent division by zero if you have no losses!
else:
    realized_rr = avg_win / abs(avg_loss)

# Max Drawdown (Peak to Trough drop)
# This calculates the biggest dollar amount your account dropped from an all-time high
df['Cumulative_PnL'] = df['Profit_Loss'].cumsum()
df['Peak_PnL'] = df['Cumulative_PnL'].cummax()
df['Drawdown'] = df['Cumulative_PnL'] - df['Peak_PnL']
max_drawdown = df['Drawdown'].min()

# 4. View the Results
print("\n" + "="*45)
print(" 📊 DEEP PORTFOLIO ANALYTICS")
print("="*45)
print(f"Total Trades Taken: {total_trades}")
print(f"Win Rate:           {win_rate:.2f}%")
print(f"Average Win:        ₹{avg_win:.2f}")
print(f"Average Loss:       ₹{avg_loss:.2f}")
print(f"Realized R:R Ratio: 1 : {realized_rr:.2f}")
print(f"Max Drawdown:       ₹{max_drawdown:.2f}")
print("="*45)

# Strategy Deep Dive
print("\n 🎯 STRATEGY BREAKDOWN")
print("-" * 45)
# Grouping by strategy to see which one has the best win rate and total profit
strategy_group = df.groupby('Strategy').agg(
    Total_Trades=('Ticker', 'count'),
    Total_PnL=('Profit_Loss', 'sum'),
    Win_Rate=('Profit_Loss', lambda x: (x > 0).mean() * 100)
).round(2)

print(strategy_group)
print("\n")