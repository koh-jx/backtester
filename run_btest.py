from data_retrieval import data_retrieval
from data_retrieval import returns_adj
from portfolio import generate_portfolio_from_csv as portf_gen
from portfolio.const_cols import PNL, RETURNS, TICKER, DATE, WEIGHT, DOLLARS
import pandas as pd
from typing import Union, List, Dict
import datetime
import logging

from utils import utils_cal, utils_csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def preprocess(data: pd.DataFrame, start_date: str, end_date: str, buffer=5) -> pd.DataFrame:
    # Retrieve price data for the tickers and date range
    all_tickers = list(set(data[TICKER]))
    retrieval_start_date = utils_cal.add_bdays(start_date, -buffer)
    retrieval_end_date = utils_cal.add_bdays(end_date, buffer)
    data = data_retrieval.retrieve_data_from_yfin(all_tickers, retrieval_start_date, retrieval_end_date)

    data_with_returns = returns_adj.add_returns(data)

    data_with_returns = data_with_returns.loc[data_with_returns[DATE].between(start_date, end_date)]
    return data_with_returns


def run_backtest(source_portfolio: Union[List[str], str, Dict], start_date: str, end_date: str, buffer=5, export_to_csv=True) -> pd.DataFrame:
    
    portfolio_df = portf_gen.get_portfolio(source_portfolio)
    price_and_ret_data = preprocess(portfolio_df, start_date, end_date, buffer)

    data_with_returns = portfolio_df.merge(price_and_ret_data, on=TICKER, how='left')
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

    # (Optional sanity: should equal initial * CumReturns)
    data_with_returns['EOD_check'] = (
        data_with_returns.groupby(TICKER)['Dollars'].transform('first')
        * data_with_returns['CumReturns']
    )

    # --- Final output ---
    result = data_with_returns[
        [DATE, TICKER, DOLLARS, RETURNS, PNL, 'CumReturns', 'SODDollars', 'EODDollars', 'EOD_check']
    ]

    if export_to_csv:
        utils_csv.export_and_open_csv(result, 'backtest_output.csv')

    return result


if __name__ == "__main__":
    tickers = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN']
    weights = [0.5, 0.1, 0.2, 0.1, 0.1]
    portfolio = {TICKER: tickers, WEIGHT: weights}
    start_date = datetime.datetime(2026, 1, 1)
    end_date = datetime.datetime(2026, 3, 15)
    run_backtest(portfolio, start_date, end_date, export_to_csv=True)