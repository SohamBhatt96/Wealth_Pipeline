import streamlit as st
import pandas as pd
import json
from database_manager import engine

# Configure the web page
st.set_page_config(page_title="Wealth Pipeline", page_icon="📈", layout="wide")

st.title("📈 Wealth Pipeline Dashboard")
st.markdown("Automated Algorithmic Trading Engine")
st.divider()

# Load the universes for the dropdown menu
try:
    with open('universes.json', 'r') as file:
        universes = json.load(file)
except FileNotFoundError:
    st.error("universes.json not found! Run universe_updater.py first.")
    st.stop()

# Build the Input Form
with st.sidebar:
    st.header("⚙️ Scan Parameters")
    with st.form("manual_scan_form"):
        capital = st.number_input("Account Capital (₹)", value=100000.0, step=10000.0)
        risk = st.number_input("Risk Per Trade (%)", value=1.0, step=0.1)
        reward = st.number_input("Reward Ratio (Take Profit)", value=2.0, step=0.5)
        buffer = st.number_input("Stop Loss Buffer (%)", value=2.0, step=0.5)
        
        index_choice = st.selectbox("Select Stock Universe", list(universes.keys()))
        
        run_scan = st.form_submit_button("🚀 Run Live Scan")

# Handle the Form Submission
if run_scan:
    st.info(f"Initiating scan on {index_choice} with ₹{capital} capital...")
    # In a fully integrated app, you would import your market_scanner.py logic here
    st.success("Scan trigger wired successfully! (Connect scanner logic to execute)")

# Display the Database 
st.subheader("🏦 Saved Trade Setups (PostgreSQL)")
try:
    query = 'SELECT * FROM trade_history ORDER BY "Date" DESC;'
    df = pd.read_sql(query, engine)
    
    if df.empty:
        st.warning("The database is currently empty. Waiting for setups...")
    else:
        # Streamlit renders pandas dataframes as beautiful, sortable web tables
        st.dataframe(df, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Database Error: {e}")