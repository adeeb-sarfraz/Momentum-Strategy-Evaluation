## OVERVIEW

Testing whether a 12-month SPY momentum strategy exhibits performance beyond increasinly structure-preserving random benchmarks. 

We use a time series momentum strategy. This project aims to construct progressively more constrained null models to benchmark momentum's risk-adjusted performance. 

## RESEARCH QUESTION

Is momentum's Sharpe ratio unuslaly high relative to appropriate randomly generated benchmarks. 

## MOMENTUM STRATEGY

Use the momentum rule to define the trading signal:

    $$
    s_t =
    \begin{cases}
    1, & \text{if } \frac{P_t}{P-{t-252}} -1 > 0 \\
    0, & \text{otherwise}
    \end{cases}
    $$

We choose momentum for its simplicity and economic interpretability - main focus of the project is stasticial benchmarking, rather than strategy optimization. Momentum tests a clear hypothesis, that return trends exhibit some persistence. 



## BACKTESTING METHODOLOGY

## NULL MODELS

## RESULTS

## KEY FINDINGS

## PERFORMANCE ENGINEERING

## LIMITATIONS

## REPOSITORY STRUCTURE

## REPRODUCING ANALYSIS

## OPTIONAL: FUTURE WORK