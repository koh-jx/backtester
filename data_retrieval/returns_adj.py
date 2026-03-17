"""From given price data, calculate returns, and adjust returns for corporate actions if necessary."""

import pandas as pd
from portfolio.const_cols import DATE, TICKER, PRICE, ADJ_PRICE, RETURNS

def add_returns(price_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate returns from price data ClosePrice. 
    If price_data is auto_adjust=True, then the ClosePrice is already adjusted for corporate actions, so we can just calculate simple returns. If not, then we need to adjust the returns for corporate actions (e.g. dividends, splits) using the Adjusted Close price."""
    assert {DATE, TICKER, PRICE}.issubset(price_data.columns), price_data.columns

    price_col = ADJ_PRICE if ADJ_PRICE in price_data.columns else PRICE
    price_data = price_data.sort_values([TICKER, DATE])
    returns = price_data.groupby(TICKER)[price_col].pct_change()
    price_data[RETURNS] = returns
    return price_data