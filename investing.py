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

# Function to simulate investment growth with leverage
def simulate_investment(initial_capital, monthly_investment, leverage, stop_loss_pct, market_returns):
    num_months = len(market_returns)
    investments = []
    profits = []
    cumulative_investment = initial_capital

    for month in range(num_months):
        market_return = market_returns[month]
        position_size = cumulative_investment * leverage
        profit = position_size * market_return
        new_capital = cumulative_investment + profit

        # Check for stop loss
        if profit / cumulative_investment <= -stop_loss_pct:
            new_capital = cumulative_investment - (cumulative_investment * stop_loss_pct)

        cumulative_investment = new_capital + monthly_investment

        investments.append(cumulative_investment)
        profits.append(profit)

    return investments, profits

# Streamlit Interface
st.title("Investment and Profit Visualizer with Leverage")

# Inputs
initial_capital = st.number_input("Initial Capital (€)", min_value=1000, step=100, value=10000)
monthly_investment = st.number_input("Monthly Investment (€)", min_value=0, step=100, value=5000)
leverage = st.slider("Leverage", min_value=1, max_value=50, value=20)
stop_loss_pct = st.slider("Stop Loss (%)", min_value=1, max_value=100, value=5) / 100
num_months = st.number_input("Number of Months to Simulate", min_value=1, step=1, value=24)

# Fetch real-time market data using Capital.com API
st.subheader("Real-Time Market Data")

epic = st.text_input("Enter Market EPIC (e.g., GOLD, AAPL)", "US100")
resolution = st.selectbox("Select Time Resolution", ["MINUTE", "MINUTE_5", "MINUTE_15", "MINUTE_30", "HOUR", "DAY", "WEEK"])
num_data_points = st.number_input("Number of Data Points", min_value=1, max_value=10000, value=30)

# Initialize session state for storing data
if 'data' not in st.session_state:
    st.session_state.data = None

# Get historical prices from Capital.com API
if st.button("Fetch Historical Data"):
    with st.spinner("Fetching historical data..."):
        historical_prices = api_client.get_historical_prices(epic=epic, resolution=resolution, max=num_data_points)

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

# Model Training and Prediction
prediction_length = st.number_input("Prediction Length", min_value=1, max_value=50, value=10)
train_model_button = st.button("Train Model")

if train_model_button:
    if st.session_state.data is None:
        st.error("No data available for training. Please fetch historical data first.")
    else:
        data = st.session_state.data
        trainer = AutoGluonTrainer(epic=epic, resolution=resolution, data_points=num_data_points, prediction_length=prediction_length)
        with st.spinner(f"Training AutoGluon model for {epic} with {resolution} interval..."):
            predictor = trainer.train_model(data, "target")
            st.success(f"Model trained and saved to {trainer.model_path}")

if st.button("Make Prediction"):
    if st.session_state.data is None:
        st.error("No data available for predictions. Please fetch historical data first.")
    else:
        data = st.session_state.data
        trainer = AutoGluonTrainer(epic=epic, resolution=resolution, data_points=num_data_points, prediction_length=prediction_length)
        future_predictions = trainer.make_predictions(data)
        st.write("Future Predictions:")
        st.write(future_predictions)
