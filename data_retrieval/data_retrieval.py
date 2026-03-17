"""
Data retrieval using Yahoo API
Columns required for backtesting:
    - Date
    - Volume
    - Adjusted Close
    - Country
    - Currency (if needed, probably just default to USD)
"""
from typing import List, Union
import datetime
import pandas as pd
from portfolio.const_cols import TICKER, DATE, PRICE, ADJ_PRICE, COUNTRY, DIVIDEND_AMT
import logging

logger = logging.getLogger(__name__)


def retrieve_price_data_from_yfin(tickers: List[str], 
                            start_date: Union[str, datetime.datetime], 
                            end_date: Union[str, datetime.datetime],
                            chunk_size=50, auto_adjust=True) -> pd.DataFrame:
    """
    Retrieve historical data for the given tickers and date range using Yahoo Finance API.
    @param tickers: List of stock tickers to retrieve data for.
    @param start_date: Start date for data retrieval.
    @param end_date: End date for data retrieval. (For yfinance this is exclusive.)
    @param chunk_size: Number of tickers to retrieve in each API call

    @return: DataFrawme
    """

    import yfinance as yf
    
    all_data = []
    for i in range(0, len(tickers), chunk_size):
        chunk_tickers = tickers[i:i + chunk_size]
        chunk_tickers_str = ' '.join(chunk_tickers)
        data = yf.download(chunk_tickers_str, start=start_date, end=end_date, multi_level_index=False, auto_adjust=auto_adjust)
        assert data is not None, f"Failed to retrieve data for tickers: {chunk_tickers_str} between {start_date} and {end_date}" 
        
        # Data is still a multiindex with tickers as second level; get ticker to its own column and drop the multiindex
        if len(tickers) > 1:
            data = data.stack(level=1).reset_index()
            data = data.rename(columns={'level_1': TICKER})
        elif len(tickers) == 1:
            data = data.reset_index()
            data[TICKER] = tickers[0]
        else:
            raise NotImplementedError(f"Empty ticker list provided!")
        

        assert {DATE, TICKER, PRICE, 'High', 'Low', 'Open', 'Volume'}.issubset(data.columns), \
            f"Missing required columns in data for tickers: {chunk_tickers_str} between {start_date} and {end_date}"
        
        if not auto_adjust:
            assert ADJ_PRICE in data.columns, f"Adj Close column is required when auto_adjust=False for tickers: {chunk_tickers_str} between {start_date} and {end_date}"

        logger.debug(f"Retrieved data for tickers: {chunk_tickers_str} between {start_date} and {end_date}, shape: {data.shape}")

        all_data.append(data)

    if len(all_data) > 0:
        data = pd.concat(all_data, ignore_index=True)

    data[DATE] = pd.to_datetime(data[DATE])
    data[TICKER] = data[TICKER].str.upper()
    return data


def retrieve_dividend_info_from_yfin(tickers: List[str]) -> pd.DataFrame:
    """Retrieves dividend information for the given tickers using Yahoo Finance API.
    @return DataFrame with columns=['Date', 'DividendYield']"""
    ...
    
    import yfinance as yf

    all_info = []
    for ticker in tickers:
        info = yf.Ticker(ticker).dividends
        assert info is not None, f"Failed to retrieve info for ticker: {ticker}"
        if info.empty:
            return

        info = info.reset_index()
        info[TICKER] = ticker
        all_info.append(info)

    all_info = pd.concat(all_info) if len(all_info) >= 1 else pd.DataFrame(columns=[DATE, DIVIDEND_AMT])
    all_info[DATE] = pd.to_datetime(pd.to_datetime(all_info[DATE]).dt.date)
    return all_info


def retrieve_ticker_info_from_yfin(tickers: List[str], relevant_cols=None) -> pd.DataFrame:
    """
    Retrieve ticker information for the given tickers using Yahoo Finance API.
    Relevant columns include:
    - symbol
    - country/region
    - currency
    - longBusinessSummary + etc. information possibly used for analysis
    @param tickers: List of stock tickers to retrieve information for.
    @param relevant_cols: List of columns to include in the returned DataFrame.

    @return: DataFrame with ticker information.
    """

    if relevant_cols is None:
        relevant_cols = ['symbol', COUNTRY, 'currency', 'longBusinessSummary', 'longName', 'sector', 'industry', 'industryKey',
                         'ebitda', 'enterpriseValue', 'forwardPE', 'forwardEps', 'priceToBook',
                         'trailingPE', 'trailingEps', 'dividendYield', 'dividendRate', 'beta',
                         'returnOnAssets', 'returnOnEquity', 'grossMargins', 'operatingMargins',
                         'lastSplitDate', 'lastSplitFactor', 'marketCap',
                         'fiftyDayAverage', 'twoHundredDayAverage']
        

    import yfinance as yf
    
    all_info = []
    for ticker in tickers:
        info = yf.Ticker(ticker).info
        assert info is not None, f"Failed to retrieve info for ticker: {ticker}"
        import pprint
        logger.debug(f"Retrieved info for {ticker}: \n{pprint.pformat(info)}")
        all_info.append(info)
    

    cols_not_found = set(relevant_cols) - set(all_info[0].keys())
    if len(cols_not_found) > 0:
        logger.warning(f"Columns not found in ticker info: {cols_not_found}.")
        logger.debug(f"Available columns: {all_info[0].keys()}")
    elif len(all_info) == len(cols_not_found):
        logger.error(f"None of the relevant columns were found in ticker info. Available columns: {all_info[0].keys()}")
        raise ValueError("None of the relevant columns were found in ticker info.")
    
    res =  pd.DataFrame(all_info)[[col for col in relevant_cols if col in all_info[0]]]
    return res


def retrieve_data_from_yfin(tickers: List[str], 
                            start_date: Union[str, datetime.datetime], 
                            end_date: Union[str, datetime.datetime],
                            chunk_size=50,
                            auto_adjust=True) -> pd.DataFrame:
    """
    Retrieve both price data and ticker information for the given tickers and date range using Yahoo Finance API.
    @param tickers: List of stock tickers to retrieve data for.
    @param start_date: Start date for data retrieval.
    @param end_date: End date for data retrieval. (For yfinance this is exclusive.)
    @param chunk_size: Number of tickers to retrieve in each API call
    @param auto_adjust: Whether to automatically adjust prices for corporate actions.

    @return: DataFrame with both price data and ticker information.
    """
    price_data = retrieve_price_data_from_yfin(tickers, start_date, end_date, chunk_size, auto_adjust=auto_adjust)
    ticker_info = retrieve_ticker_info_from_yfin(tickers)
    div_data = retrieve_dividend_info_from_yfin(tickers)
    
    if any(ticker_info['symbol'].duplicated()):
        logger.warning("Duplicate symbols found in ticker info. This may lead to issues when merging with price data."
                       f"(first 20 duplicates shown below)\n" \
                       f"{ticker_info[ticker_info['symbol'].duplicated(keep=False)].head(20)}")

    logger.info(f"Price data shape: {price_data.shape}")
    logger.info(f"Ticker info shape: {ticker_info.shape}")
    logger.info(f"Dividend data shape: {div_data.shape}")

    # Merge price data with ticker info on 'Ticker' and 'symbol'
    merged_data = price_data.merge(ticker_info, left_on=TICKER, right_on='symbol', how='left')
    merged_data = price_data.merge(div_data, how='left', on=[TICKER, DATE])
    merged_data[DIVIDEND_AMT] = merged_data[DIVIDEND_AMT].fillna(0)

    logger.info(f"Merged data shape: {merged_data.shape}")
    return merged_data
