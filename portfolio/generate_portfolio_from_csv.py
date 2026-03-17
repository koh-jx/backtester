import pandas as pd
from typing import Union, List, Dict
import logging
from portfolio.const_cols import TICKER, DOLLARS, WEIGHT

logger = logging.getLogger(__name__)


def get_portfolio(source_portfolio: Union[List[str], str, Dict], default_total_dollar_amount=10000):
    """
    Generates the portfolio given one of the following source_portfolio types:
    1) string path to csv
        - Reads csv and converts to dataframe
    2) List of Ticker strings
        - Uses tickers as provided
    3) Dict
        - Directly converts dict to dataframe (where keys are column names and values are lists of column values)

    If Dollar column is present in the resultant dataframe, then we will use the dollar amounts as is.
      If not, but Weight column is present, then we will allocate the default_total_dollar_amount according to the weights. 
      If neither Dollar nor Weight column is present, then we will just allocate equal dollar amounts to each ticker where total=default_total_dollar_amount.

    @param source_portfolio: List of tickers, or string path to csv, or dict with column names as keys and list of column values as values
    @default_total_dollar_amount: Total dollar amount if Weight column is present. For list of strings, equals weights allocated to each ticker.
    @return DataFrame of Tickers with Dollars
    """

    if isinstance(source_portfolio, list):
        portfolio_df = pd.DataFrame({TICKER: source_portfolio})
        logger.info("Creating equally-weighted portfolio")
        portfolio_df[DOLLARS] = default_total_dollar_amount / len(source_portfolio)

    else: 
        if isinstance(source_portfolio, str):
            # Read portfolio from CSV 
            portfolio_df = pd.read_csv(source_portfolio)
        elif isinstance(source_portfolio, dict):
            portfolio_df = pd.DataFrame(source_portfolio)
        else:
            raise ValueError(f"Unsupported source_portfolio type: {type(source_portfolio)}. "
                            f"Must be one of List[str], str (csv path), or Dict. Seeing {source_portfolio}")

        # Handle Dollars and Weight columns if any is provided
        if DOLLARS in portfolio_df.columns:
            logger.info("Dollar column found; using Dollars found as-is")
            assert not any(portfolio_df[DOLLARS].isnull()), '\n'+portfolio_df[[TICKER, DOLLARS]].to_string()
            portfolio_df = portfolio_df.drop(columns=[WEIGHT], errors='coerce')

        elif WEIGHT in portfolio_df.columns:
            logger.info(f"Weight column found; using Weighted positions across ${default_total_dollar_amount}")
            portfolio_df[DOLLARS] = portfolio_df[WEIGHT] * default_total_dollar_amount
        else:
            logger.info("Neither Weight nor Dollars column found; creating equally-weighted portfolio")
            portfolio_df[DOLLARS] = default_total_dollar_amount / len(portfolio_df)

    assert TICKER in portfolio_df.columns, portfolio_df.columns
    portfolio_df[TICKER] = portfolio_df[TICKER].str.upper()  # Ensure tickers are uppercase
    return portfolio_df
