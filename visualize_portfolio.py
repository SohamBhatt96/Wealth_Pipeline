import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import random
import warnings

warnings.filterwarnings('ignore')

def calculate_rsi(data, periods=14):
    """Calculates the 14-day RSI for our chart."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def view_stock_setup(ticker):
    """
    TOOL 1: THE SETUP VISUALIZER
    Draws a 2-panel chart showing Price, 44 EMA, 200 EMA, and RSI.
    """
    print(f"\n[*] Fetching chart data for {ticker}...")
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    
    if df.empty:
        print(f"Error: No data found for {ticker}")
        return

    # Calculate Indicators
    df['200_EMA'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['44_EMA'] = df['Close'].ewm(span=44, adjust=False).mean()
    df['RSI'] = calculate_rsi(df['Close'])

    # Build the Chart (2 rows, 1 column)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
    fig.suptitle(f"{ticker} - Algorithmic Setup Visualizer", fontsize=16, fontweight='bold')

    # Top Panel: Price and EMAs
    ax1.plot(df.index, df['Close'], label='Close Price', color='black', linewidth=1.5)
    ax1.plot(df.index, df['44_EMA'], label='44 EMA (Trend)', color='blue', linestyle='--')
    ax1.plot(df.index, df['200_EMA'], label='200 EMA (Baseline)', color='red', linewidth=2)
    ax1.set_ylabel('Price (₹)')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # Bottom Panel: Momentum (RSI)
    ax2.plot(df.index, df['RSI'], color='purple', label='14-Day RSI')
    ax2.axhline(45, color='green', linestyle='--', alpha=0.7, label='Oversold Threshold (45)')
    ax2.set_ylabel('RSI')
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show() # Pops open the interactive window


def view_portfolio_curve():
    """
    TOOL 2: THE PORTFOLIO TRACKER
    Draws an equity curve of your account growth.
    (Currently using simulated data until we connect your PostgreSQL database)
    """
    print("\n[*] Generating Portfolio Equity Curve...")
    
    # Generate 50 days of simulated trading growth
    dates = pd.date_range(end=pd.Timestamp.today(), periods=50, freq='B')
    capital = 500000.0
    equity_curve = [capital]
    
    for _ in range(49):
        # Simulate small daily wins and losses
        daily_return = random.uniform(-0.005, 0.008) 
        capital = capital * (1 + daily_return)
        equity_curve.append(capital)
        
    df_port = pd.DataFrame({'Date': dates, 'Equity': equity_curve})
    df_port.set_index('Date', inplace=True)
    
    # Build the Chart
    plt.figure(figsize=(10, 5))
    plt.plot(df_port.index, df_port['Equity'], color='green', linewidth=2, label='Total Account Capital')
    plt.title("Wealth Pipeline: Simulated Equity Curve", fontsize=16, fontweight='bold')
    plt.ylabel("Capital (₹)")
    
    # Fill the area under the curve for a professional look
    plt.fill_between(df_port.index, df_port['Equity'], min(equity_curve) * 0.99, color='green', alpha=0.1)
    
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show() # Pops open the interactive window


# ==========================================
# 🎛️ MAIN DASHBOARD MENU
# ==========================================
if __name__ == "__main__":
    print("="*45)
    print(" 📊 VISUALIZATION DASHBOARD")
    print("="*45)
    print("1. View a Stock Setup Chart")
    print("2. View Portfolio Equity Curve")
    print("3. Run Both")
    
    choice = input("\nEnter your choice (1, 2, or 3): ")
    
    if choice == '1':
        view_stock_setup("BHARTIARTL.NS") 
    elif choice == '2':
        view_portfolio_curve()
    elif choice == '3':
        view_stock_setup("BHARTIARTL.NS")
        view_portfolio_curve()
    else:
        print("Invalid choice.")3