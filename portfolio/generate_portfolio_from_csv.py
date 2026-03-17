import pandas as pd
from typing import Union, List, Dict


def get_portfolio(source_portfolio: Union[List[str], str, Dict]):
    # TODO (Currently just taking tickers, but can be extended to weights/dollar amounts, etc.)
    if isinstance(source_portfolio, str):
        # Read portfolio from CSV 
        portfolio_df = pd.read_csv(source_portfolio)
    elif isinstance(source_portfolio, dict):
        portfolio_df = pd.DataFrame(source_portfolio)
    else:
        portfolio_df = pd.DataFrame({'Ticker': source_portfolio})

    assert 'Ticker' in portfolio_df.columns, portfolio_df.columns
    portfolio_df['Ticker'] = portfolio_df['Ticker'].str.upper()  # Ensure tickers are uppercase