import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Union

from portfolio.const_cols import DATE, PNL


def plot_portfolio(
    portfolio_df: pd.DataFrame,
    y_axis_col: Union[str, List[str]] = PNL,
    x_axis_col: str = DATE,
    running_sum=True,
    run_yearly=False
):
    """
    Plots the given y_axis_col against x_axis_col for the portfolio_df.
    If y_axis_col is a list of columns, then we will plot each column on the same graph with a legend.

    @param running_sum: Whether to compute cumulative sum or take y_axis_col values as is.
    @param run_yearly: If True, reset cumulative sum at the start of each year (only if running_sum is True)
    """

    portfolio_df = portfolio_df.copy()
    portfolio_df[x_axis_col] = pd.to_datetime(portfolio_df[x_axis_col])

    portfolio_df = portfolio_df.groupby(x_axis_col)[y_axis_col].sum().reset_index()

    if isinstance(y_axis_col, str):
        y_axis_col = [y_axis_col]

    if running_sum and run_yearly:
        portfolio_df['Year'] = portfolio_df[x_axis_col].dt.year

        for col in y_axis_col:
            for year, df_year in portfolio_df.groupby('Year'):
                df_year = df_year.sort_values(by=x_axis_col).copy()
                df_year[col] = df_year[col].cumsum()

                plt.plot(
                    df_year[x_axis_col],
                    df_year[col],
                    label=f"{col} ({year})"
                )

    else:
        if running_sum:
            for col in y_axis_col:
                portfolio_df[col] = portfolio_df[col].cumsum()

        for col in y_axis_col:
            plt.plot(portfolio_df[x_axis_col], portfolio_df[col], label=col)

    plt.axhline(y=0, linestyle='--', linewidth=1)
    plt.xlabel(x_axis_col)
    plt.ylabel(', '.join(y_axis_col))
    plt.title('Portfolio Performance')
    plt.legend()
    plt.show()