import os
import pandas as pd
from autogluon.timeseries import TimeSeriesPredictor, TimeSeriesDataFrame

class AutoGluonTrainer:
    def __init__(self, epic, resolution, data_points, prediction_length=10, model_dir="models"):
        """
        Initialize the AutoGluonTrainer class.

        Parameters:
        - epic (str): The stock or commodity EPIC (e.g., 'GOLD', 'AAPL').
        - resolution (str): The time interval used for the data (e.g., 'MINUTE', 'HOUR').
        - prediction_length (int): The number of future steps to predict.
        - model_dir (str): The directory to save the trained models.
        """
        self.epic = epic
        self.resolution = resolution
        self.prediction_length = prediction_length
        self.model_path = f"{model_dir}/{epic}_{resolution}_{data_points}predictor"
        self.freq = self._get_frequency(resolution)

    def _get_frequency(self, resolution):
        """Map the resolution to a pandas frequency string."""
        freq_map = {
            "MINUTE": "T",
            "MINUTE_5": "5T",
            "MINUTE_15": "15T",
            "MINUTE_30": "30T",
            "HOUR": "H",
            "DAY": "D",
            "WEEK": "W"
        }
        return freq_map.get(resolution, "T")

    def train_model(self, data, target_column):
        # Check if the model already exists
        if os.path.exists(self.model_path):
            # Load the existing model
            predictor = self.load_model()
            # Retrain or fine-tune the existing model with new data
            predictor.fit(train_data=data, tuning_data=None, time_limit=None, presets=None)
        else:
            # Train a new model if it doesn't exist
            predictor = TimeSeriesPredictor(
                prediction_length=self.prediction_length,
                freq=self.freq,
                path=self.model_path  # specify the path to save the model
            )
            predictor.fit(train_data=data)
            predictor.save()  # Save the model after training

        return predictor

    def load_model(self):
        """
        Load a previously trained AutoGluon model.

        Returns:
        - predictor (TimeSeriesPredictor): The loaded AutoGluon model.
        """
        return TimeSeriesPredictor.load(self.model_path)

    def make_predictions(self, data):
        """
        Make predictions using the trained model.

        Parameters:
        - data (pd.DataFrame): The historical data to make predictions on.

        Returns:
        - predictions (pd.DataFrame): The predicted values.
        """
        predictor = self.load_model()
        return predictor.predict(data.tail(self.prediction_length))
