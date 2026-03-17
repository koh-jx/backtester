from data_retrieval import data_retrieval
from data_retrieval import returns_adj
from portfolio import generate_portfolio_from_csv as portf_gen
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
    all_tickers = list(set(data['Ticker']))
    retrieval_start_date = utils_cal.add_bdays(start_date, -buffer)
    retrieval_end_date = utils_cal.add_bdays(end_date, buffer)
    data = data_retrieval.retrieve_data_from_yfin(all_tickers, retrieval_start_date, retrieval_end_date)

    data_with_returns = returns_adj.add_returns(data)

    data_with_returns = data_with_returns.loc[data_with_returns['Date'].between(start_date, end_date)]
    return data_with_returns


def run_backtest(source_portfolio: Union[List[str], str, Dict], start_date: str, end_date: str, buffer=5, export_to_csv=True) -> pd.DataFrame:
    
    portfolio_df = portf_gen.get_portfolio(source_portfolio)
    data_with_returns = preprocess(portfolio_df, start_date, end_date, buffer)
    
    
    data_with_returns['Dollars'] = 1  # TODO
    data_with_returns['PnL'] = data_with_returns['Returns']

    result = data_with_returns[['Date', 'Ticker', 'Dollars', 'Returns', 'PnL']]

    if export_to_csv:
        utils_csv.export_and_open_csv(result, 'backtest_output.csv')
        
    return result


if __name__ == "__main__":
    tickers = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN']
    start_date = datetime.datetime(2026, 1, 1)
    end_date = datetime.datetime(2026, 3, 15)
    run_backtest(tickers, start_date, end_date)