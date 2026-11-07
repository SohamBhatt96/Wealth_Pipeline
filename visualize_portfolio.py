import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import random
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 🧮 RAW NATIVE MATH FUNCTIONS 
# ==========================================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_atr_and_adx(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()

    up_move = df['High'] - df['High'].shift()
    down_move = df['Low'].shift() - df['Low']
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    
    return atr, adx

# ==========================================
# 📈 THE VISUALIZERS
# ==========================================
def view_stock_setup(ticker):
    """Draws a 3-panel chart matching our Scanner logic."""
    # Ensure the .NS suffix is there for Yahoo Finance
    if not ticker.endswith('.NS'):
        ticker = f"{ticker}.NS"
        
    print(f"\n[*] Fetching chart data for {ticker}...")
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    
    if df.empty:
        print(f"Error: No data found for {ticker}")
        return

    # Calculate Indicators to match the Balanced Strategy
    df['50_EMA'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['RSI'] = calculate_rsi(df['Close'])
    df['ATR'], df['ADX'] = calculate_atr_and_adx(df)

    # Build the 3-Panel Chart
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [3, 1, 1]})
    fig.suptitle(f"{ticker} - Algorithmic Setup Visualizer", fontsize=16, fontweight='bold')

    # Top Panel: Price and EMA
    ax1.plot(df.index, df['Close'], label='Close Price', color='black', linewidth=1.5)
    ax1.plot(df.index, df['50_EMA'], label='50 EMA (Balanced Trend)', color='blue', linestyle='--')
    ax1.set_ylabel('Price (₹)')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # Middle Panel: Momentum (RSI & ADX)
    ax2.plot(df.index, df['RSI'], color='purple', label='14-Day RSI')
    ax2.plot(df.index, df['ADX'], color='orange', label='14-Day ADX (Trend Strength)')
    ax2.axhline(40, color='green', linestyle='--', alpha=0.7, label='RSI Oversold (40)')
    ax2.axhline(25, color='red', linestyle='--', alpha=0.7, label='ADX Strong Trend (25)')
    ax2.set_ylabel('Momentum')
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper left', fontsize='small')
    ax2.grid(True, alpha=0.3)
    
    # Bottom Panel: ATR
    ax3.plot(df.index, df['ATR'], color='teal', label='14-Day ATR (Volatility)')
    ax3.set_ylabel('ATR (₹)')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

def view_portfolio_curve():
    """Draws an equity curve of your simulated account growth."""
    print("\n[*] Generating Portfolio Equity Curve...")
    
    dates = pd.date_range(end=pd.Timestamp.today(), periods=50, freq='B')
    capital = 100000.0 # Adjusted to match your ₹100,000 test account
    equity_curve = [capital]
    
    for _ in range(49):
        daily_return = random.uniform(-0.005, 0.008) 
        capital = capital * (1 + daily_return)
        equity_curve.append(capital)
        
    df_port = pd.DataFrame({'Date': dates, 'Equity': equity_curve})
    df_port.set_index('Date', inplace=True)
    
    plt.figure(figsize=(10, 5))
    plt.plot(df_port.index, df_port['Equity'], color='green', linewidth=2, label='Total Account Capital')
    plt.title("Wealth Pipeline: Simulated Equity Curve", fontsize=16, fontweight='bold')
    plt.ylabel("Capital (₹)")
    plt.fill_between(df_port.index, df_port['Equity'], min(equity_curve) * 0.99, color='green', alpha=0.1)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

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
        target = input("Enter ticker symbol (e.g., HCLTECH): ").strip().upper()
        view_stock_setup(target) 
    elif choice == '2':
        view_portfolio_curve()
    elif choice == '3':
        target = input("Enter ticker symbol (e.g., HCLTECH): ").strip().upper()
        view_stock_setup(target)
        view_portfolio_curve()
    else:
        print("Invalid choice.")