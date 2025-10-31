import pandas as pd
import matplotlib.pyplot as plt

def plot_data():
    df = pd.read_csv("STX.csv")

    # Convert the Unix timestamp to datetime (divide by 1000 since it's in milliseconds)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Set the timestamp as the index (optional but useful for time series)
    df.set_index('timestamp', inplace=True)
    metrics = ['straddlePrice', 'assetPrice', 'volatility', 'impliedMove', 'volume']

    fig, axes = plt.subplots(len(metrics), 1, figsize=(10, 10), sharex=True)

    for i, metric in enumerate(metrics):
        axes[i].plot(df.index, df[metric], label=metric, color='tab:blue')
        axes[i].set_title(metric)
        axes[i].grid(True)
        axes[i].legend(loc='upper right')

    # Label x-axis only on the last plot
    axes[-1].set_xlabel("Time")

    plt.tight_layout()
    plt.show()
