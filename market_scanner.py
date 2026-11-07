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
    
    # Ensures strategy is a string
    strategy = str(input("Enter Strategy (conservative/balanced/aggressive): ")).strip().lower()
    if strategy not in ['conservative', 'balanced', 'aggressive']:
        strategy = 'balanced'
    
    cats = list(universes.keys())
    for i, cat in enumerate(cats, 1): print(f"[{i}] {cat}")
    
    choice = int(input("\nSelect list (number): "))
    tickers = universes[cats[choice - 1]]
    
    return capital, risk, reward, strategy, tickers

def get_automated_inputs(universes):
    if datetime.today().weekday() > 4:
        logging.warning("Weekend detected. Aborting scan.")
        sys.exit()
        
    with open('config.json', 'r') as file: config = json.load(file)
    capital = float(config['portfolio']['capital'])
    risk = float(config['portfolio']['risk_percentage'])
    reward = float(config['strategy']['reward_ratio']) 
    
    # Safely extracts strategy as a string, defaults to balanced if missing
    strategy = str(config.get('strategy', {}).get('profile', 'balanced')).strip().lower()
    
    tickers = universes.get("Nifty 100", universes["Nifty 50"]) 
    
    logging.info(f"[AUTO MODE] Cap: ₹{capital} | Risk: {risk}% | Target 1:{reward} | Strategy: {strategy.upper()}")
    return capital, risk, reward, strategy, tickers

# ==========================================
# 🧮 RAW NATIVE MATH FUNCTIONS (NO DEPENDENCIES)
# ==========================================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_atr_and_adx(df, period=14):
    # 1. Calculate True Range (TR)
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()

    # 2. Calculate Directional Movement (ADX)
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
# 🚀 CORE SCANNER ENGINE 
# ==========================================
def execute_scan(capital, risk, reward, strategy_name, universe):
    logging.info(f"Scanning {len(universe)} stocks using {strategy_name.upper()} strategy...")
    
   profiles = {
        "conservative": {"ema": 200, "rsi": 42, "adx": 18, "turnover": 50000000},
        "balanced":     {"ema": 50,  "rsi": 48, "adx": 20, "turnover": 50000000},
        "aggressive":   {"ema": 20,  "rsi": 55, "adx": 22, "turnover": 50000000}
    }
    rules = profiles.get(strategy_name, profiles["balanced"])
    
    setups_found = []

    for ticker in universe:
        try:
            # Let the upgraded yfinance library handle the connection natively
            stock = yf.Ticker(ticker)
            df = stock.history(period="1y")

            if df.empty or len(df) < rules["ema"]: 
                continue

            # Calculate Technicals manually
            ema_col = f"EMA_{rules['ema']}"
            df[ema_col] = df['Close'].ewm(span=rules["ema"], adjust=False).mean()
            df['RSI_14'] = calculate_rsi(df['Close'], period=14)
            df['ATRr_14'], df['ADX_14'] = calculate_atr_and_adx(df, period=14)

            latest = df.iloc[-1]
            
            if pd.isna(latest[ema_col]) or pd.isna(latest['ATRr_14']):
                continue

            # Apply Strict Rules
            rule_1 = latest['Close'] > latest[ema_col]          
            rule_2 = latest['ADX_14'] > rules["adx"]            
            rule_3 = latest['RSI_14'] < rules["rsi"]            
            rupee_turnover = latest['Volume'] * latest['Close']
            rule_4 = rupee_turnover > rules["turnover"]            

            if rule_1 and rule_2 and rule_3 and rule_4:
                dynamic_sl = latest['Close'] - (latest['ATRr_14'] * 2)
                take_profit = latest['Close'] + ((latest['Close'] - dynamic_sl) * reward)
                
                risk_data = calculate_position_size(capital, risk, latest['Close'], dynamic_sl)
                clean_ticker = ticker.replace('.NS', '')
                
                log_trade(
                    ticker=clean_ticker, 
                    strategy=strategy_name, 
                    atr=latest['ATRr_14'],
                    shares=risk_data['Shares to Buy'], 
                    entry_price=latest['Close'], 
                    stop_loss=dynamic_sl, 
                    take_profit=take_profit, 
                    total_value=risk_data['Total Trade Value (₹)']
                )
                
                setups_found.append({
                    'Ticker': clean_ticker, 
                    'Shares': risk_data['Shares to Buy'], 
                    'SL': round(dynamic_sl, 2),
                    'Target': round(take_profit, 2)
                })
                logging.info(f"SETUP FOUND: {clean_ticker} | ATR: {round(latest['ATRr_14'], 2)} | SL: {round(dynamic_sl, 2)}")

        except Exception as e: 
            logging.error(f"Failed {ticker}: {e}")

    if setups_found:
        msg = "".join([f"{s['Ticker']}: Buy {s['Shares']} (SL: ₹{s['SL']} | Tgt: ₹{s['Target']})\n" for s in setups_found])
        notification.notify(title="Wealth Pipeline Setups!", message=msg, app_name="Scanner", timeout=10)
        logging.info(f"Scan complete. {len(setups_found)} setups logged to database.")
    else:
        logging.info("Scan complete. No setups met criteria today.")

# ==========================================
# ⚙️ EXECUTION TRIGGER 
# ==========================================
if __name__ == "__main__":
    all_universes = load_universes()
    if '--auto' in sys.argv:
        ACCOUNT_CAPITAL, RISK_PCT, REWARD_RATIO, STRATEGY, TICKERS = get_automated_inputs(all_universes)
    else:
        ACCOUNT_CAPITAL, RISK_PCT, REWARD_RATIO, STRATEGY, TICKERS = get_manual_inputs(all_universes)
        logging.info("Starting manual scan...")
        
    execute_scan(ACCOUNT_CAPITAL, RISK_PCT, REWARD_RATIO, STRATEGY, TICKERS)