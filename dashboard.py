import streamlit as st
import pandas as pd
import json
from database_manager import engine
from market_scanner import execute_scan

# ==========================================
# 🔧 CONFIGURATION & STRATEGY RULES
# ==========================================
st.set_page_config(page_title="Wealth Pipeline", page_icon="📈", layout="wide")

# Updated rules reflecting Rupee Turnover (₹5 Cr) and realistic Pullback/Momentum thresholds
STRATEGY_RULES = {
    "conservative": "📈 **Trend:** Price > 200 EMA \n\n📉 **Pullback:** RSI < 42 \n\n⚡ **Momentum:** ADX > 18 \n\n🌊 **Liquidity:** Turnover > ₹5 Cr",
    "balanced": "📈 **Trend:** Price > 50 EMA \n\n📉 **Pullback:** RSI < 48 \n\n⚡ **Momentum:** ADX > 20 \n\n🌊 **Liquidity:** Turnover > ₹5 Cr",
    "aggressive": "📈 **Trend:** Price > 20 EMA \n\n📉 **Pullback:** RSI < 55 \n\n⚡ **Momentum:** ADX > 22 \n\n🌊 **Liquidity:** Turnover > ₹5 Cr"
}

st.title("📈 Wealth Pipeline Dashboard")
st.markdown("Automated Algorithmic Trading Engine")
st.divider()

try:
    with open('universes.json', 'r') as file:
        universes = json.load(file)
except FileNotFoundError:
    st.error("universes.json not found! Run universe_updater.py first.")
    st.stop()

# ==========================================
# ⚙️ SIDEBAR: SCAN PARAMETERS
# ==========================================
with st.sidebar:
    st.header("⚙️ Scan Parameters")
    with st.form("manual_scan_form"):
        capital = st.number_input("Account Capital (₹)", value=100000.0, step=10000.0)
        risk = st.number_input("Risk Per Trade (%)", value=1.0, step=0.1)
        reward = st.number_input("Reward Ratio (Take Profit)", value=2.0, step=0.5)
        
        strategy = st.selectbox("Strategy Profile", ["conservative", "balanced", "aggressive"])
        
        # Display the specific rules for the selected strategy in the sidebar
        st.info(f"**Engine Rules:**\n\n{STRATEGY_RULES[strategy]}")
        
        index_choice = st.selectbox("Select Stock Universe", list(universes.keys()))
        
        run_scan = st.form_submit_button("🚀 Run Live Scan")

# Handle the Form Submission
if run_scan:
    with st.spinner(f"🚀 Scanning {index_choice} using {strategy.upper()} strategy..."):
        try:
            tickers = universes[index_choice]
            execute_scan(capital, risk, reward, strategy, tickers)
            st.success(f"✅ Scan complete! Any setups matching the {strategy.upper()} rules were logged.")
            
            # Professional subtle notification instead of balloons
            st.toast("Database updated successfully.", icon="🏦") 
            
        except Exception as e:
            st.error(f"❌ Scan failed: {e}")

# ==========================================
# 📊 MAIN DASHBOARD: LIVE METRICS & DATABASE
# ==========================================
st.subheader("🏦 Saved Trade Setups (PostgreSQL)")
try:
    query = 'SELECT * FROM public.trade_history ORDER BY "Date" DESC;'
    df = pd.read_sql(query, engine)
    
    if df.empty:
        st.warning("The database is currently empty. Waiting for setups...")
    else:
        st.markdown("### 🔍 Filter Results")
        
        if 'strategy' in df.columns:
            strategies_in_db = ["All"] + list(df['strategy'].dropna().unique())
            selected_filter = st.selectbox("Filter view by Strategy:", strategies_in_db)
            
            if selected_filter != "All":
                display_df = df[df['strategy'] == selected_filter]
                # Display the rules for the filtered strategy above the table
                st.info(f"**Displaying {selected_filter.upper()} Setups.** Mathematical Criteria: {STRATEGY_RULES.get(selected_filter.lower(), 'Custom')}")
            else:
                display_df = df
        else:
            display_df = df

        # --- Portfolio Metrics ---
        st.markdown("### 💼 Portfolio Metrics")
        col1, col2, col3 = st.columns(3)
        
        total_cap = display_df['Capital_Risked'].sum() if 'Capital_Risked' in display_df.columns else 0
        active_count = len(display_df)
        
        avg_atr = display_df['atr'].dropna().mean() if 'atr' in display_df.columns else 0
        if pd.isna(avg_atr): 
            avg_atr = 0

        col1.metric("Capital Allocated", f"₹ {total_cap:,.2f}")
        col2.metric("Qualified Setups", active_count)
        col3.metric("Average System Volatility (ATR)", f"₹ {avg_atr:,.2f}")
        
        st.divider()

        # --- Formatting and Display ---
        ui_df = display_df.copy()
        currency_cols = ['Entry_Price', 'Stop_Loss', 'Target_Price', 'Capital_Risked', 'atr']
        for col in currency_cols:
            if col in ui_df.columns:
                ui_df[col] = pd.to_numeric(ui_df[col], errors='coerce')
                ui_df[col] = ui_df[col].apply(lambda x: f"₹ {x:,.2f}" if pd.notnull(x) else "None")
                
        if 'strategy' in ui_df.columns:
            ui_df['strategy'] = ui_df['strategy'].str.upper()

        st.dataframe(ui_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Database Error: {e}")