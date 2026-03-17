"""From given price data, calculate returns, and adjust returns for corporate actions if necessary."""

import pandas as pd

def add_returns(price_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate returns from price data ClosePrice. 
    If price_data is auto_adjust=True, then the ClosePrice is already adjusted for corporate actions, so we can just calculate simple returns. If not, then we need to adjust the returns for corporate actions (e.g. dividends, splits) using the Adjusted Close price."""
    assert {'Date', 'Ticker', 'Close'}.issubset(price_data.columns), price_data.columns

    price_col = 'Adj Close' if 'Adj Close' in price_data.columns else 'Close'
    price_data = price_data.sort_values(['Ticker', 'Date'])
    returns = price_data.groupby('Ticker')[price_col].pct_change()
    price_data['Returns'] = returns
    return price_data