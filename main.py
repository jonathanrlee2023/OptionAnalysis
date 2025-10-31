import os
from dotenv import load_dotenv
import schwabdev
from earnings import get_earnings_options_data
from plotData import plot_data


if __name__ == "__main__":
    load_dotenv()  # loads variables from .env into environment
    plot_data()
    # appKey = os.getenv("appKey")
    # appSecret = os.getenv("appSecret")
    # client = schwabdev.Client(app_key=appKey, app_secret=appSecret)
    # get_earnings_options_data(client=client)