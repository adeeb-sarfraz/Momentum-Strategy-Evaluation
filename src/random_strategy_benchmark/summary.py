import matplotlib.pyplot as plt
import pandas as pd


def summary(simulation_df, momentum_results, strategy):

    x = 0
    
    simulation_sharpe_ratio = simulation_df["annual_sharpe"]

    for i in range(len(simulation_sharpe_ratio)):
        if simulation_sharpe_ratio[i] >= momentum_results["annual_sharpe"]:
            x += 1

    p_value = ((x + 1)/(len(simulation_sharpe_ratio) + 1))

    summary_stats = {
        "strategy": strategy,
        "mean_sharpe": simulation_df["annual_sharpe"].mean(),
        "median_sharpe": simulation_df["annual_sharpe"].median(),
        "max_sharpe": simulation_df["annual_sharpe"].max(),
        "p_value": p_value,
        "avg_trades": simulation_df["trades"].mean(),
        "avg_time_invested": simulation_df["time_invested"].mean(),
        "number_of_simulations": len(simulation_df)
    }

    strategy_name = strategy.replace("_", " ").title()

    for key, value in summary_stats.items():
        if key != "strategy":
            print(f"{key.replace('_', ' ').title()}: {value:.5f}".rstrip("0").rstrip("."))


    pd.DataFrame([summary_stats]).to_csv(
        f"../../data/{strategy}_summary.csv",index=False
    )


    plt.figure(figsize=(8, 5))

    plt.hist(
        simulation_df["annual_sharpe"],
        bins=40,
        color="black",
        alpha=0.75,
        edgecolor="white"
    )

    plt.axvline(
        momentum_results["annual_sharpe"],
        color="red",
        linestyle="--",
        linewidth=2,
        label="Momentum Sharpe"
    )

    plt.xlabel("Sharpe Ratio")
    plt.ylabel("Frequency")
    plt.title(f"Distribution of {strategy_name} Sharpe Ratios")

    plt.legend()

    plt.grid(axis="y", alpha=0.2)

    plt.tight_layout()
    plt.show()

    return summary_stats

    