# AI Investing Application
![image](https://github.com/user-attachments/assets/7fa374f4-602e-4832-a797-f6b79589dad7)

An AI-driven investing application that leverages real-time market data and machine learning models to simulate investments, predict future market trends, and visualize potential profits using leverage. This application integrates with the Capital.com API to fetch real-time and historical market data and uses AutoGluon for time series prediction.

## Features

- **Real-Time Market Data**: Fetch historical and real-time market data using the Capital.com API.
- **AutoGluon Time Series Prediction**: Train and deploy time series models to predict future market trends.
- **Investment Simulation**: Simulate investment growth with leverage, including options for monthly investments and stop-loss settings.
- **Interactive Interface**: User-friendly Streamlit interface for easy interaction and visualization.
- **Customizable Parameters**: Adjust initial capital, monthly investment, leverage, stop-loss percentage, and more.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Clone the Repository

```bash
git clone https://github.com/birdhouses/ai-trader.git
cd ai-trader
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set Up Environment Variables

Create a `.env` file in the root directory of the project to store your API credentials. Do **NOT** share this file or upload it to any public repository.

```bash
touch .env
```

Add the following lines to the `.env` file:

```
CAPITAL_COM_API_KEY=your_capital_com_api_key
CAPITAL_COM_IDENTIFIER=your_capital_com_identifier
CAPITAL_COM_API_PASSWORD=your_capital_com_password
```

**Note**: Replace `your_capital_com_api_key`, `your_capital_com_identifier`, and `your_capital_com_password` with your actual Capital.com API credentials.

### Obtain Capital.com API Credentials

To use this application, you need to have a Capital.com account and obtain API credentials.

1. Sign up for an account at [Capital.com](https://capital.com/).
2. Navigate to the API section in your account settings.
3. Generate a new API key and note down your identifier and password.

## Usage

### Running the Application

To run the Streamlit application, execute the following command:

```bash
streamlit run investing.py
```

This will launch the application in your default web browser.

### Application Workflow

1. **Input Investment Parameters**: Set your initial capital, monthly investment amount, leverage, stop-loss percentage, and the number of months to simulate.
2. **Fetch Historical Data**: Enter the EPIC code of the market you're interested in (e.g., `US100`, `GOLD`, `AAPL`), select the time resolution, and specify the number of data points.
3. **Train the Model**: Click on "Fetch Historical Data" to retrieve data and then "Train Model" to train the AutoGluon time series predictor.
4. **Make Predictions**: Once the model is trained, click on "Make Prediction" to generate future market predictions.
5. **Visualize Results**: View the predicted values and simulate investment growth based on your parameters.

## Project Structure

```
├── modules
│   ├── capital_com_api.py     # Capital.com API client wrapper
│   └── predictors.py          # AutoGluon time series predictor
├── models                     # Directory to store trained models
├── investing.py               # Main Streamlit application
├── requirements.txt           # Python dependencies
├── .env.example               # Example environment variables file
├── .gitignore                 # Git ignore file
└── README.md                  # Project documentation
```

## Dependencies

- **Streamlit**: For building the interactive web application.
- **Pandas**: Data manipulation and analysis.
- **NumPy**: Numerical computing.
- **Matplotlib**: Data visualization.
- **AutoGluon**: Automated machine learning toolkit for time series prediction.
- **Requests**: For making HTTP requests to the Capital.com API.
- **Python-dotenv**: For loading environment variables from a `.env` file.

Install all dependencies using:

```bash
pip install -r requirements.txt
```

## Important Notes

- **API Credentials Security**: Ensure that your `.env` file is included in your `.gitignore` file to prevent accidental upload of sensitive API credentials to any public repository.
- **Demo vs. Live Trading**: The application is set to use live trading data (`demo=False`). If you wish to use demo data, set `demo=True` when initializing the `CapitalComAPI` client.
- **Leverage and Risk**: Using leverage amplifies both gains and losses. Be cautious when simulating investments with high leverage and understand the associated risks.
- **Data Privacy**: Be mindful of any personal or sensitive data. Do not share logs or outputs that may contain sensitive information.

## Acknowledgments

- [Capital.com API](https://capital.com/api) for providing access to market data.
- [AutoGluon](https://auto.gluon.ai/) for automated machine learning tools.
- [Streamlit](https://streamlit.io/) for the interactive web application framework.

## Contact

For any questions or issues, please open an issue on the repository.
