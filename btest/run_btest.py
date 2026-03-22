from data_retrieval import data_retrieval

from portfolio.const_cols import PNL, RETURNS, TICKER, DATE, WEIGHT, DOLLARS, PRICE, NB_SHARES, DIVIDEND_AMT
import pandas as pd
from typing import Union, List, Dict
import datetime

from utils import utils_cal, utils_csv


def run_backtest(portfolio_df: pd.DataFrame, start_date: str, end_date: str,
                 buffer=5, export_to_csv=True, ret_data: pd.DataFrame=None) -> pd.DataFrame:

    # Extend start date ahead by 1 bday so we get the pricing data even after we shift(1).
    actual_start_date = start_date
    start_date = utils_cal.add_bdays(start_date, -1)
    
    all_tickers = list(set(portfolio_df[TICKER]))
    price_and_ret_data = data_retrieval.preprocess_rets(all_tickers, start_date, end_date, buffer) if ret_data is None else ret_data

    data_with_returns = portfolio_df.merge(price_and_ret_data, on=TICKER, how='left')  # TODO Will need to merge by Date as well (after adding date info to portf_gen)
    data_with_returns = data_with_returns.sort_values(by=[TICKER, DATE])
    data_with_returns[RETURNS] = data_with_returns[RETURNS].fillna(0)

    # Calculate cumulative returns up to current date
    data_with_returns['CumReturns'] = data_with_returns.groupby(TICKER)[RETURNS]\
        .transform(lambda x: (1 + x).cumprod())

    # Calculate Dollars at SOD (i.e. cumulative return up to previous day * initial dollars)
    data_with_returns['SODDollars'] = data_with_returns.groupby(TICKER)['Dollars']\
        .transform('first') * data_with_returns['CumReturns'].shift(1)
    
    # CumReturns shifted by 1 means first day will be NaN, so fill that with initial dollars
    data_with_returns['SODDollars'] = data_with_returns['SODDollars'].fillna(data_with_returns['Dollars'])  

    data_with_returns[PNL] = data_with_returns['SODDollars'] * data_with_returns[RETURNS]
    data_with_returns['EODDollars'] = data_with_returns['SODDollars'] + data_with_returns[PNL]

    data_with_returns['PrevClose'] = data_with_returns.groupby(TICKER)[PRICE].shift(1)
    data_with_returns[NB_SHARES] = data_with_returns['SODDollars'] / data_with_returns['PrevClose']
    data_with_returns['DividendPayout'] = data_with_returns[DIVIDEND_AMT] * data_with_returns[NB_SHARES]

    data_with_returns[PNL] += data_with_returns['DividendPayout']

    # (Optional sanity: should equal initial * CumReturns)
    data_with_returns['EOD_check'] = (
        data_with_returns.groupby(TICKER)['Dollars'].transform('first')
        * data_with_returns['CumReturns']
    )

    # --- Final output ---
    data_with_returns = data_with_returns.loc[data_with_returns[DATE].between(actual_start_date, end_date)]
    result = data_with_returns[
        [DATE, TICKER, PRICE, DOLLARS, RETURNS, NB_SHARES, DIVIDEND_AMT, 'DividendPayout', PNL, 'CumReturns', 'SODDollars', 'EODDollars', 'EOD_check']
    ]

    if export_to_csv:
        utils_csv.export_and_open_csv(result, 'backtest_output.csv')

    return result
