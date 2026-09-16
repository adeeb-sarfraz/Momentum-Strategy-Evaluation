import pandas as pd
import numpy as np

from src.backtester import backtester


def generate_momentum_signal(prices, lookback):
    momentum_signal = [np.nan] * lookback

    for i in range(lookback, len(prices)):
        roc = prices.iloc[i] / prices.iloc[i - lookback] - 1

        if roc > 0:
            momentum_signal.append(1)
        else:
            momentum_signal.append(0)

    return momentum_signal


def run_momentum_strategy(prices, returns, lookback, transaction_cost):
    
    momentum_signal = generate_momentum_signal(prices, lookback)

    momentum_df, momentum_results = backtester(returns, momentum_signal, transaction_cost)

    return momentum_df, momentum_results