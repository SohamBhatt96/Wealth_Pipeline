import sys
import json
import yfinance as yf
import pandas as pd
import warnings
import logging
from datetime import datetime
from plyer import notification
from risk_manager import calculate_position_size
from database_manager import log_trade

warnings.filterwarnings('ignore')

# ==========================================
# 📝 LOGGING CONFIGURATION
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("scanner.log"), 
        logging.StreamHandler(sys.stdout)   
    ]
)

def load_universes():
    try:
        with open('universes.json', 'r') as file: return json.load(file)
    except FileNotFoundError:
        logging.error("universes.json not found! Run universe_updater.py first.")
        sys.exit()

def get_manual_inputs(universes):
    print("\n[INTERACTIVE MODE]\n")
    capital = float(input("Enter Capital (₹): ").replace(',', ''))
    risk = float(input("Enter Risk %: "))
    reward = float(input("Enter Reward Ratio (e.g., 2): "))
    buffer = float(input("Enter SL Buffer %: "))
    
    cats = list(universes.keys())
    for i, cat in enumerate(cats, 1): print(f"[{i}] {cat}")
    
    choice = int(input("\nSelect list (number): "))
    tickers = universes[cats[choice - 1]]
    return capital, risk, reward, buffer, tickers

def get_automated_inputs(universes):
    if datetime.today().weekday() > 4:
        logging.warning("Weekend detected. Aborting scan.")
        sys.exit()
        
    with open('config.json', 'r') as file: config = json.load(file)
    capital = config['portfolio']['capital']
    risk = config['portfolio']['risk_percentage']
    buffer = config['strategy']['sl_buffer_pct']
    reward = config['strategy']['reward_ratio'] 
    tickers = universes.get("Nifty 100", universes["Nifty 50"]) 
    
    logging.info(f"[AUTO MODE] Cap: ₹{capital} | Risk: {risk}% | Target 1:{reward} | Nifty 100")
    return capital, risk, reward, buffer, tickers

# Initialize System
all_universes = load_universes()
if '--auto' in sys.argv:
    ACCOUNT_CAPITAL, RISK_PCT, REWARD_RATIO, SL_BUFFER, TICKERS = get_automated_inputs(all_universes)
else:
    ACCOUNT_CAPITAL, RISK_PCT, REWARD_RATIO, SL_BUFFER, TICKERS = get_manual_inputs(all_universes)
    logging.info("Starting manual scan...")

def calculate_rsi(data, periods=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Scan Engine
logging.info(f"Scanning {len(TICKERS)} stocks for high-probability setups...")
setups_found = []
for ticker in TICKERS:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        if df.empty: continue

        df['200_EMA'] = df['Close'].ewm(span=200, adjust=False).mean()
        df['44_EMA'] = df['Close'].ewm(span=44, adjust=False).mean()
        df['RSI_14'] = calculate_rsi(df['Close'])
        df['Vol_20_SMA'] = df['Volume'].rolling(window=20).mean()
        
        latest = df.iloc[-1]
        rule_1 = abs((latest['Close'] - latest['200_EMA']) / latest['200_EMA']) * 100 <= 2.0 
        rule_2 = latest['44_EMA'] > latest['200_EMA']
        rule_3 = latest['RSI_14'] < 45
        rule_4 = latest['Volume'] > latest['Vol_20_SMA']

        if rule_1 and rule_2 and rule_3 and rule_4:
            dynamic_sl = latest['200_EMA'] * (1 - (SL_BUFFER / 100))
            take_profit = latest['Close'] + ((latest['Close'] - dynamic_sl) * REWARD_RATIO)
            
            risk_data = calculate_position_size(ACCOUNT_CAPITAL, RISK_PCT, latest['Close'], dynamic_sl)
            clean_ticker = ticker.replace('.NS', '')
            
            log_trade(clean_ticker, risk_data['Shares to Buy'], latest['Close'], dynamic_sl, take_profit, risk_data['Total Trade Value (₹)'])
            
            setups_found.append({'Ticker': clean_ticker, 'Shares': risk_data['Shares to Buy'], 'Target': round(take_profit, 2)})
            logging.info(f"SETUP FOUND: {clean_ticker}")

    except Exception as e: 
        logging.error(f"Failed {ticker}: {e}")

if setups_found:
    msg = "".join([f"{s['Ticker']}: Buy {s['Shares']} (Tgt: ₹{s['Target']})\n" for s in setups_found])
    notification.notify(title="Wealth Pipeline Setups!", message=msg, app_name="Scanner", timeout=10)
    logging.info(f"Scan complete. {len(setups_found)} setups logged to database.")
else:
    logging.info("Scan complete. No setups met criteria today.")