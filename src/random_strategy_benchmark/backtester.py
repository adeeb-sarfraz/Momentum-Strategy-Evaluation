import pandas as pd
import numpy as np


def calculate_return(price):

    returns = [np.nan]

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

    position = df["position"].fillna(0)
    previous_position = position.shift(1).fillna(0)

    trade_indicator = (position != previous_position).astype(int)
    trade_count = trade_indicator.sum()


    # Transaction Costs

    df["transaction_cost"] = trade_indicator * transaction_cost
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
    
    valid_return = performance_return.dropna()
    compounded_equity = (1 + valid_return).cumprod()
    
    df.loc[compounded_equity.index, "equity"] = compounded_equity

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

    df["running_peak"] = df["equity"].cummax()
    
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

def backtester_v2(returns_array, signal, transaction_cost):

    signal_array = np.array(signal)

    position_array = np.empty_like(signal_array)

    position_array[0] = np.nan
    position_array[1:] = signal_array[:-1]

    strategy_return_array = returns_array * position_array

    # Time Invested

    days_invested = (position_array == 1).sum()
    valid_days = (~np.isnan(position_array)).sum()
    time_invested = days_invested / valid_days


    # Trade Counts

    position_filled_array = np.where(np.isnan(position_array), 0, position_array)

    previous_position_array = np.empty_like(position_array)

    previous_position_array[1:] = position_filled_array[:-1]
    previous_position_array[0] = 0

    trade_indicator = (position_filled_array != previous_position_array)
    trade_count = trade_indicator.sum()


    # Transaction Costs

    transaction_cost_array = trade_indicator * transaction_cost
    net_strategy_return_array = strategy_return_array - transaction_cost_array


    # Equity

    valid_list = ~np.isnan(net_strategy_return_array)

    if not valid_list.any():
        raise ValueError("No valid strategy returns were generated.")

    first_valid = np.argmax(valid_list)

    initial_equity = 1
    start_index = first_valid - 1

    equity_array = np.empty_like(net_strategy_return_array)

    equity_array[:start_index] = np.nan
    equity_array[start_index] = initial_equity

    valid_returns = net_strategy_return_array[first_valid:]

    compounded_equity = np.cumprod(1 + valid_returns)

    equity_array[first_valid:] = compounded_equity

    final_equity = equity_array[-1]

    total_return = (final_equity / initial_equity) - 1


    # Volatility + Sharpe Ratio

    risk_free_rate = 0

    daily_volatility = np.nanstd(net_strategy_return_array, ddof=1)
    mean_daily_return = np.nanmean(net_strategy_return_array)

    sharpe_daily = (mean_daily_return - risk_free_rate)/daily_volatility

    annual_volatility = np.sqrt(252) * daily_volatility
    sharpe_ratio = np.sqrt(252) * sharpe_daily


    # Drawdown

    running_peak_array = np.maximum.accumulate(equity_array[start_index:])

    drawdown_array = equity_array[start_index:] / running_peak_array - 1
    max_drawdown = np.min(drawdown_array)


    # CAGR + Calmar Ratio

    growth_multiple = final_equity / initial_equity
    years = valid_days / 252
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

    return results
        