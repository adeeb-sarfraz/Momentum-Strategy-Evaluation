# Random Strategy Benchmarking: Testing Momentum Against Structured Null Models

## Overview

Testing whether a 12-month SPY momentum strategy exhibits performance beyond increasingly structure-preserving random benchmarks. 

We use a time series momentum strategy. This project aims to construct progressively more constrained null models to benchmark momentum's risk-adjusted performance. SPY data used for analysis is contained within data/spy_daily.csv

## Research Question

Is momentum's Sharpe ratio unusually high relative to appropriate randomly generated benchmarks?  

## Momentum Strategy

Use the momentum rule, with lookback = 252 trading days (~12 months) to define the trading signal:

$$
s_t =
\begin{cases}
1, & \text{if } \frac{P_t}{P_{t-252}} -1 > 0 \\
0, & \text{otherwise}
\end{cases}
$$

where:
- $P_t$ = SPY price on day t
- $P_{t-252}$ = SPY price 252 trading days earlier
- $s_t$ = 1 = invested in SPY
- $s_t$ = 0 = cash

To ensure today's closing price is not used to generate a signal and retroactively earn today's return, use a one day execution lag:
```math
\text{Position}_{t+1} = s_t
```

We choose momentum for its simplicity and economic interpretability - main focus of the project is stasticial benchmarking, rather than strategy optimization. Momentum tests a clear hypothesis, that return trends exhibit some persistence. 

Why select a 12-month lookback, and not optimise lookback period? 
- Searching across many lookback periods and selecting strongest performer introduces parameter selection bias and increases risk of overfitting the historical data. 

## Backtesting Methodology

Daily returns are calculated as a % increase/decrease of the day before. For each trade that occurs in the signal (switch between an invested state/cash state), there is an assosciated transaction cost. TThis project assumes a typical transaction cost of 0.1%. 

The equity curve is initialised at 1 immediately before first valid strategy return. It is updated recursively as $E_t = E_{t-1}(1 + r_t)$, where $r_t$ is the net daily return strategy after transaction costs. Define the total return as $R_{\text{total}} = \frac{E_{\text{final}}}{E_{\text{initial}}} - 1$, which simplifies to $R_{\text{total}} = E_{\text{final}} - 1$

The annualised Sharpe ratio comes from scaling daily sharpe ratio by $\sqrt{252}$, where 252 = number of trading days in a year. Scaling factor assumes returns are approximately independent and identically distributed across trading days. Sharpe ratio is calculated under a zero risk-free-rate assumption, simplifying returns assosciated with holding cash. Importantly, every simulated strategy is calculated using the same risk-free-rate assumption, so benchmark comparisons are internally consistent. 

Backtester computes Compound Annual Growth Rate, the average yearly growth rate of an investment over the historical period. Drawdown is calculated, measuring % decline in equity from previous running peak. Maximum drawdown is the largest such decline over the peak. From this, a Calmar Ratio is computed, which quanitifies an investment's risk-adjusted return by dividing its annualised compound return by its maximum drawdown over the historical period.

The backtester returns this information about any trading signal fed into it, along with the assosciated prices and returns. 

## Null models

| Benchmark | Main Constraint | Purpose |
| --- | --- | --- |
| Elementary | 50/50 daily investedment probability| Baseline random benchmark |
| Exposure Matched | Market exposure | Controls for time invested|
| Trade-Count Matched | No. of position switches | Controls for transaction costs/turnover |
| Exposure + Trade-Count Matched | Market exposure + no. of position switches | Controls for time invested + transaction cost/turnover |
| Run Length Permutation | Run length distribution | Controls for exact collection of cash/invested runs|
| Cyclic Shifting | Ordering + local clustering | Controls for almost entire original trading pattern |

Null models start off fairly elementary, offering an unrepresentative comparison with momentum trading strategy. Matching time invested in SPY attempts to offer closer market risk equivalence between momentum & random strategies. Controlling trade-counts avoids large volume of trades in initial models, & the punishing assosciated transaction costs. Preserving run lengths while randomising temporal arrangement replicates momentum's structure closer than previous models. Cyclic shifting further preserves the exact sequence, instead shifting its starting point to random days in market history. 

## Results

Momentum strategy generated:
- Annualised Sharpe ratio: ~0.627
- Time invested: ~77.52%
- Position switches: 89

Performance was compared against 6 null models, using 100,000 Monte Carlo simulations per benchmark:

| Strategy                       |   Mean Sharpe |   Median Sharpe |   Max Sharpe |   P Value |   Avg Trades | Avg Time Invested   |   Number Of Simulations |
|:-------------------------------|--------------:|----------------:|-------------:|----------:|-------------:|:--------------------|------------------------:|
| Elementary                     |       -0.5425 |         -0.5422 |       0.092  |   1e-05   |      3229.85 | 50.00%              |                  100000 |
| Exposure Matched               |       -0.0361 |         -0.0365 |       0.3807 |   1e-05   |      2251.88 | 77.52%              |                  100000 |
| Trade Count Matched            |        0.3758 |          0.3705 |       1.0105 |   0.03649 |        89    | 50.00%              |                  100000 |
| Exposure + Trade Count Matched |        0.4694 |          0.4641 |       0.9461 |   0.04709 |        89    | 77.52%              |                  100000 |
| Run Length Permutation         |        0.4738 |          0.4601 |       0.9846 |   0.07784 |        89    | 77.52%              |                  100000 |
| Cyclic Shift                   |        0.4735 |          0.4424 |       1.1811 |   0.11017 |        90.76 | 77.52%              |                  100000 |

Empirical p-value increases substantially as momentum's structure is increasingly preserved, rising from <0.001 in initial random strategies to ~0.1102 in the cyclic shift benchmark. 

## Key findings

Extremely small p-values generated by Elementary & Exposure Matched strategies suggest simple daily-random strategies provide little structural resemblance, & weak comparisons for the 12-month momentum strategy. 

As turnover, exposure & structure are progressively preserved, momentum's evidence for unusually high risk-adjusted performance weakens dramatically. 

Indeed, Run Length Permutation & Cyclic Shift strategies fail to reject their respective null hypotheses at the 5% significance level. There is evidence to suggest momentum's risk-adjusted performance is not significantly unusual in comparison with more resemblant random strategies. 

## Performance engineering

Original backtester was heavily dependent on Pandas operations & Python for loops . Profiling identified particular operations (iterative signal generation, dataframe construction, series alignment etc.) as main performance bottlenecks. This made conducting large-scale Monte Carlo simulations tedious. 

Backtester went through a series of optimisations to dramatically decrease run time. Computation was shifted towards more efficient NumPy methods like array slicing & vectorised arithmetic, replacing iterative position-generation logic. Calculations being recomputed unnecessarily within each simulation were moved outside the backtester entirely. 

On the same machine, core backtest runtime reduced from ~3.67ms to ~0.43ms per run, roughly an 88% reduction in duration. Running 100,000 Monte Carlo simulations become considerably more practical after the update. All results and outputs of the initial versions were preserved. 

## Limitations

Analysis is limited to the SPY across its historical sample size, with a 12-month momentum rule. Results do not necessarily carry over to other assets, markets or parameter choices. 

Backtester assumes a zero risk-free-rate when calculating annualised Sharpe, simplifying returns when holding cash. In reality, interest rates typically non-zero; Sharpe is not 100% representative of real-world data. 

Daily Sharpe ratios are also annualised using a $\sqrt{252}$ scaling factor. Approximation assumes daily returns are independent over time, and their dsitribution is identical. Financial returns are rarely perfectly IID; returns exhibiting serial correlation (rather ironically linked to what this project explores in some capacity) will not accurately estimate the true annualised Sharpe ratio. 

## Repository structure


```text
random_strategy_benchmark/
├── data/
├── notebooks/
│   ├── backtester/
│   ├── random_benchmarks/
│   ├── 2.0_momentum_strategy.ipynb
│   └── 4.0_comparison_table.ipynb
├── src/
│   └── random_strategy_benchmark/
│       ├── __init__.py
│       ├── backtester.py
│       ├── strategies.py
│       └── summary.py
├── pyproject.toml
├── requirements.txt
└── README.md
```
Note that "data/" contains SPY dataset plus generated benchmark results, "backtester/" includes 5 iterations of backtester optimising, "random_benchmarks/" contains the 6 null-model notebooks used for comparison, src/random_strategy_benchmark contains Python package used by notebooks including backtesters, strategy generators and summary functions. 


## Reproducing analysis

Project was developed using Python 3.14.7. 
Install required packages with:

```bash
pip install -r requirements.txt
pip install -e .
```

## Future work

Possible extensions include testing alternative lookback periods, additional assets, & more realistic risk-free rates. 