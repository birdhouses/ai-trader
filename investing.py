import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from modules.capital_com_api import CapitalComAPI
from modules.predictors import AutoGluonTrainer

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
API_KEY = os.getenv('CAPITAL_COM_API_KEY')
IDENTIFIER = os.getenv('CAPITAL_COM_IDENTIFIER')
PASSWORD = os.getenv('CAPITAL_COM_API_PASSWORD')

# Initialize the CapitalComAPI client
api_client = CapitalComAPI(
    api_key=API_KEY,
    identifier=IDENTIFIER,
    password=PASSWORD,
    demo=False  # Set to False for live trading
)

# Initialize session state for storing data
if 'data' not in st.session_state:
    st.session_state.data = None

st.title("AI Investing Application")

# Use tabs to organize the UI
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Market Data",
    "Model Training & Prediction",
    "Account Info",
    "Positions & Orders",
    "Place Order",
    "Transaction History"
])

# ----------------- Market Data Tab -----------------
with tab1:
    st.header("Market Data")

    epic = st.text_input("Enter Market EPIC (e.g., GOLD, AAPL)", "US100")
    resolution = st.selectbox("Select Time Resolution", [
        "MINUTE", "MINUTE_5", "MINUTE_15", "MINUTE_30", "HOUR", "DAY", "WEEK"
    ])
    num_data_points = st.number_input(
        "Number of Data Points", min_value=1, max_value=10000, value=30)

    if st.button("Fetch Historical Data"):
        with st.spinner("Fetching historical data..."):
            historical_prices = api_client.get_historical_prices(
                epic=epic, resolution=resolution, max=num_data_points)

            if 'prices' not in historical_prices or not historical_prices['prices']:
                st.error("No data found for the given stock and interval.")
            else:
                st.success("Data fetched successfully!")
                data = pd.DataFrame([
                    {
                        "item_id": epic,  # Each row has the same 'item_id'
                        "timestamp": pd.to_datetime(price['snapshotTimeUTC']),
                        "target": price['closePrice']['bid']
                    }
                    for price in historical_prices['prices']
                ])
                st.session_state.data = data  # Store data in session state
                st.write(data)

                # Plot the data
                st.line_chart(data.set_index('timestamp')['target'])

# -------- Model Training & Prediction Tab ----------
with tab2:
    st.header("Model Training & Prediction")
    prediction_length = st.number_input(
        "Prediction Length", min_value=1, max_value=50, value=10)
    train_model_button = st.button("Train Model")

    if train_model_button:
        if st.session_state.data is None:
            st.error(
                "No data available for training. Please fetch historical data first.")
        else:
            data = st.session_state.data
            trainer = AutoGluonTrainer(
                epic=epic,
                resolution=resolution,
                data_points=num_data_points,
                prediction_length=prediction_length
            )
            with st.spinner(f"Training AutoGluon model for {epic} with {resolution} interval..."):
                predictor = trainer.train_model(data, "target")
                st.success(
                    f"Model trained and saved to {trainer.model_path}")

    if st.button("Make Prediction"):
        if st.session_state.data is None:
            st.error(
                "No data available for predictions. Please fetch historical data first.")
        else:
            data = st.session_state.data
            trainer = AutoGluonTrainer(
                epic=epic,
                resolution=resolution,
                data_points=num_data_points,
                prediction_length=prediction_length
            )
            future_predictions = trainer.make_predictions(data)
            st.write("Future Predictions:")
            st.write(future_predictions)

            # Plot predictions
            st.line_chart(future_predictions['mean'])

# ---------------- Account Info Tab -----------------
with tab3:
    st.header("Account Information")
    if st.button("Get Account Details"):
        with st.spinner("Fetching account details..."):
            accounts = api_client.get_accounts()
            st.write(accounts)

    if st.button("Get Account Preferences"):
        with st.spinner("Fetching account preferences..."):
            preferences = api_client.get_account_preferences()
            st.write(preferences)

# ----------- Positions & Orders Tab ----------------
with tab4:
    st.header("Open Positions & Orders")
    if st.button("Get Open Positions"):
        with st.spinner("Fetching open positions..."):
            positions = api_client.get_open_positions()
            st.write(positions)

    if st.button("Get Open Orders"):
        with st.spinner("Fetching open orders..."):
            orders = api_client.get_open_orders()
            st.write(orders)

    # Option to close a position
    st.subheader("Close a Position")
    deal_id_to_close = st.text_input("Enter Deal ID to Close")
    if st.button("Close Position"):
        if deal_id_to_close:
            with st.spinner(f"Closing position {deal_id_to_close}..."):
                response = api_client.close_position(deal_id_to_close)
                st.write(response)
        else:
            st.error("Please enter a Deal ID to close.")

# --------------- Place Order Tab -------------------
with tab5:
    st.header("Place a New Order")
    order_type = st.selectbox("Order Type", ["Market Order", "Working Order"])
    direction = st.selectbox("Direction", ["BUY", "SELL"])
    size = st.number_input("Size", min_value=0.0, value=1.0)
    guaranteed_stop = st.checkbox("Guaranteed Stop", value=False)
    stop_level = st.number_input("Stop Level (optional)", value=0.0)
    profit_level = st.number_input("Profit Level (optional)", value=0.0)

    if order_type == "Market Order":
        if st.button("Place Market Order"):
            with st.spinner("Placing market order..."):
                response = api_client.create_position(
                    epic=epic,
                    direction=direction,
                    size=size,
                    guaranteed_stop=guaranteed_stop,
                    stop_level=stop_level if stop_level > 0 else None,
                    profit_level=profit_level if profit_level > 0 else None
                )
                st.write(response)
    else:
        level = st.number_input("Order Level", value=0.0)
        good_till_date = st.date_input("Good Till Date (optional)", value=None)
        if st.button("Place Working Order"):
            with st.spinner("Placing working order..."):
                response = api_client.create_working_order(
                    epic=epic,
                    direction=direction,
                    size=size,
                    level=level,
                    order_type='LIMIT',
                    guaranteed_stop=guaranteed_stop,
                    stop_level=stop_level if stop_level > 0 else None,
                    profit_level=profit_level if profit_level > 0 else None,
                    good_till_date=good_till_date.isoformat() if good_till_date else None
                )
                st.write(response)

# ----------- Transaction History Tab ---------------
with tab6:
    st.header("Transaction History")
    from_date = st.date_input("From Date")
    to_date = st.date_input("To Date")
    transaction_type = st.selectbox("Transaction Type (optional)", [
        "ALL", "DEPOSIT", "WITHDRAWAL", "TRADE", "FEE", "OTHER"])

    if st.button("Get Transaction History"):
        with st.spinner("Fetching transaction history..."):
            response = api_client.get_transaction_history(
                from_date=from_date.isoformat(),
                to_date=to_date.isoformat(),
                transaction_type=None if transaction_type == "ALL" else transaction_type
            )
            st.write(response)
