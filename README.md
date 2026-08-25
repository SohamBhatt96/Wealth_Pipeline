# 📈 Wealth Pipeline

An automated, locally-hosted algorithmic trading pipeline designed to scan the Indian stock market for high-probability setups using technical indicators (EMA, RSI, Volume). 

This engine is completely decoupled, featuring a PostgreSQL database for trade logging, a scheduled background worker for daily automated scans, and a Streamlit web dashboard for interactive manual scanning.

## ⚙️ Core Features
* **Automated Daily Scanning:** Configured via Windows Task Scheduler to execute silently in the background at 3:45 PM.
* **Risk Management:** Dynamically calculates position sizing based on strict risk percentages and account capital constraints.
* **Database Integration:** Permanently logs all valid trade setups (Ticker, Entry, Stop Loss, Target Price, Shares) to a local PostgreSQL instance.
* **Interactive Web GUI:** Streamlit frontend allows for manual universe selection, on-the-fly parameter adjustments, and live database viewing.
* **Desktop Notifications:** Utilizes the `plyer` library to push native Windows alerts when a valid setup is detected during background execution.

## 🛠️ Technology Stack
* **Backend:** Python 3, `yfinance`, `pandas`
* **Frontend:** `streamlit`, `rich` (CLI fallback)
* **Database:** PostgreSQL, `sqlalchemy`, `psycopg2`
* **Version Control:** Git & GitHub

## 🚀 Quick Start (Local Setup)

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/SohamBhatt96/Wealth_Pipeline.git](https://github.com/SohamBhatt96/Wealth_Pipeline.git)
   cd Wealth_Pipeline
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Database:**
   * Create a PostgreSQL database named `wealth_db`.
   * Create a `.env` file in the root directory and add your credentials:
     ```text
     DB_PASSWORD=your_secure_password
     ```
   * *Note: The database tables and schema will auto-generate on the first run via SQLAlchemy.*

4. **Launch the Dashboard:**
   ```bash
   python -m streamlit run dashboard.py
   ```