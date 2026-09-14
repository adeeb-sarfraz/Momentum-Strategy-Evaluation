import pandas as pd
import numpy as np


def calculate_return(price):

    returns = [None]

    for i in range(1,len(price)):
        daily_return = (price.iloc[i] - price.iloc[i-1])/price.iloc[i-1]
        returns.append(daily_return)

    return returns


def backtester(returns, signal, transaction_cost):

    df = pd.DataFrame({
        "return": returns,
        "signal": signal
    })

    df["position"] = df["signal"].shift(1)
    df["strategy_return"] = df["return"] * df["position"]


    # Time Invested

    days_invested = (df["position"] == 1).sum()
    valid_days = df["position"].count()
    time_invested = days_invested / valid_days


    # Trade Counts

    position = df["position"].fillna(0).tolist()
    trade_indicator = [0]
    
    for i in range(1, len(position)):
        if position[i] != position[i-1]:
            trade_indicator.append(1)
        else:
            trade_indicator.append(0)
    
    df["trade"] = trade_indicator
    trade_count = df["trade"].sum()


    # Transaction Costs

    df["transaction_cost"] = df["trade"] * transaction_cost
    df["net_strategy_return"] = df["strategy_return"] - df["transaction_cost"]


    # Equity

    performance_return = df["net_strategy_return"]

    first_valid = performance_return.first_valid_index()

    if first_valid is None:
        raise ValueError("No valid strategy returns were generated.")

    initial_equity = 1.0

    df["equity"] = np.nan
    start_index = first_valid - 1

    df.loc[start_index, "equity"] = initial_equity
    
    for i in range(first_valid, len(df)):

        previous_equity = float(df.loc[i - 1, "equity"])
        current_return = float(performance_return.iloc[i])

        df.loc[i, "equity"] = (previous_equity * (1 + current_return))

    final_equity = float(df["equity"].dropna().iloc[-1])

    total_return = (final_equity / initial_equity) - 1


    # Volatility + Sharpe Ratio

    risk_free_rate = 0
    
    daily_volatility = performance_return.std()
    mean_daily_return = performance_return.mean()
    sharpe_daily = (mean_daily_return - risk_free_rate)/daily_volatility
    
    annual_volatility = np.sqrt(252) * daily_volatility
    sharpe_ratio = np.sqrt(252) * sharpe_daily


    # Drawdown

    df["running_peak"] = np.nan

    df.loc[start_index, "running_peak"] = initial_equity
    
    for i in range(1, len(df["equity"])):
        df.loc[i, "running_peak"] = max(df.loc[i, "equity"], df.loc[i-1, "running_peak"])
    
    df["drawdown"] = df["equity"] / df["running_peak"] - 1
    max_drawdown = df["drawdown"].min()


    # CAGR + Calmar Ratio

    growth_multiple = final_equity / initial_equity
    years = performance_return.count() / 252
    cagr = growth_multiple ** (1 / years) - 1
    calmar_ratio = cagr / abs(max_drawdown)


    results = {
        "total_return": total_return,
        "cagr": cagr,
        "annual_volatility": annual_volatility,
        "annual_sharpe": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "calmar": calmar_ratio,
        "time_invested": time_invested,
        "trades": trade_count
    }

    return df, results
    