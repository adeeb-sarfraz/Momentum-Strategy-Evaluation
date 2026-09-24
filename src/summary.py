import matplotlib.pyplot as plt


def summary(simulation_df, momentum_results, plot_title):

    print(f"Sharpe Average: {simulation_df['annual_sharpe'].mean():.4f}")
    print(f"Sharpe Median:  {simulation_df['annual_sharpe'].median():.4f}")
    print(f"Largest Sharpe: {simulation_df['annual_sharpe'].max():.4f}")
    print(f"Average No. of Trades: {simulation_df['trades'].mean():.4f}")
    print(f"Average Time Invested: {simulation_df['time_invested'].mean():.4f}")

    x = 0

    simulation_sharpe_ratio = simulation_df["annual_sharpe"]

    for i in range(len(simulation_sharpe_ratio)):
        if simulation_sharpe_ratio[i] >= momentum_results["annual_sharpe"]:
            x += 1

    p_value = ((x + 1)/(len(simulation_sharpe_ratio) + 1))

    print("Empirical p-value:", round(p_value, 4))

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
    plt.title(plot_title)

    plt.legend()

    plt.grid(axis="y", alpha=0.2)

    plt.tight_layout()
    plt.show()