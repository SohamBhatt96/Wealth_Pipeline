# 📈 Wealth Pipeline

**Wealth Pipeline** is a quantitative swing trading algorithmic scanner and risk management engine built in Python. It scans Indian Equities (NSE), identifies high-probability pullbacks using technical indicators, and automatically calculates strict, volatility-adjusted position sizing before logging actionable setups to a PostgreSQL database.

---

## 🚀 Key Features

* **Automated Risk Management:** Calculates position sizes dynamically based on Account Capital and Risk Per Trade (%). 
* **Volatility-Adjusted Stop Loss:** Uses a 14-period Average True Range (ATR) to place stop losses safely outside the zone of normal market noise.
* **Institutional Liquidity Filtering:** Filters out illiquid operator traps by demanding a minimum **₹5 Crore daily Rupee Turnover**, protecting capital from slippage without artificially blocking high-priced blue-chip stocks.
* **Streamlit UI:** A fully interactive web dashboard for running live market scans and tracking historical setups.
* **Database Integration:** Automatically logs all qualified trades (Entry, Stop Loss, Target, Shares, and Capital Allocated) directly to a PostgreSQL database.

---

## 📊 Strategy Profiles

The engine features three distinct swing-trading algorithms tailored to different market environments.

| Strategy | Description | Technical Criteria |
| :--- | :--- | :--- |
| **Conservative** | Deep value pullbacks near major institutional support. | `Price > 200 EMA`, `RSI < 42`, `ADX > 18` |
| **Balanced** | Healthy mid-trend pullbacks offering clean 1:2 R:R entries. | `Price > 50 EMA`, `RSI < 48`, `ADX > 20` |
| **Aggressive** | Fast breakouts and strong runners taking shallow breathers. | `Price > 20 EMA`, `RSI < 55`, `ADX > 22` |

*(All strategies require a minimum Rupee Turnover of ₹5,000,000)*

---

## 🛠️ Tech Stack

* **Core Engine:** Python 3, `pandas`, `numpy`
* **Market Data:** `yfinance`
* **Database:** PostgreSQL, `SQLAlchemy`
* **Frontend UI:** `Streamlit`
* **Desktop Alerts:** `plyer`

---

## ⚙️ Installation & Setup

1. Clone the repository and install dependencies:
    git clone [https://github.com/yourusername/wealth-pipeline.git](https://github.com/yourusername/wealth-pipeline.git)
    cd wealth-pipeline
    pip install -r requirements.txt

2. Database Configuration:
    Ensure PostgreSQL is installed and running. The engine expects a local PostgreSQL connection (configured in `database_manager.py`). 

3. Generate Stock Universes:
    Run the universe updater to fetch the latest Nifty index constituents:
    python universe_updater.py

---

## 💻 Usage

Wealth Pipeline can be operated via the interactive web dashboard or the command-line interface.

### Option 1: Streamlit Dashboard (Recommended)
Launch the graphical interface to configure risk parameters, select strategies, and view database logs.
    python -m streamlit run dashboard.py

### Option 2: Manual Terminal Scan
Run the engine directly from the terminal. It will prompt you to enter your capital, risk percentage, and strategy choice manually.
    python market_scanner.py

### Option 3: Fully Automated Execution (--auto)
Bypass all manual inputs and run the scan instantly using the default settings saved in your config.json file. This is ideal for scheduling automated daily scans (e.g., via Windows Task Scheduler at 3:15 PM).
    python market_scanner.py --auto

---

## ⚠️ Disclaimer

*This software is for educational and quantitative research purposes only. It does not constitute financial advice. Algorithmic trading carries inherent risks, and past performance of technical indicators does not guarantee future returns. Always paper-trade and verify setups before deploying real capital.*