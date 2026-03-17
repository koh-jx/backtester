from typing import List
import logging
import datetime
import pandas as pd
from functools import wraps

from portfolio.const_cols import DATE, TICKER, COUNTRY, PRICE, DIVIDEND_AMT
from utils import utils_cal

logger = logging.getLogger(__name__)


FOREX_MAP = {
    'Singapore': "SGDUSD=X"
}


def convert_to_usd(cols_to_convert: List = None, keep_fx_rate_col=False):
    """Requires DATE, and either TICKER or COUNTRY"""

    MONETARY_COLS = [
        PRICE, 'High', 'Low', 'Open', DIVIDEND_AMT,
        'ebitda', 'enterpriseValue', 'marketCap',
        'forwardEps', 'trailingEps',
        'dividendRate',
        'fiftyDayAverage', 'twoHundredDayAverage'
    ]
    def _outer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            original_result = func(*args, **kwargs)
            result = original_result.copy()

            if not isinstance(result, pd.DataFrame):
                return result
            
            if (cols_to_convert is None or len(cols_to_convert) == 0):
                relevant_cols = [x for x in result.columns if x in MONETARY_COLS]
                if len(relevant_cols) == 0:
                    return result
                
                logger.info(f"Converting to USD the following columns: {relevant_cols} if not already US names")
            else:
                relevant_cols = cols_to_convert
            
            if DATE not in result.columns:
                return result
            
            from data_retrieval import forex
            original_length = len(result)
            fx = forex.retrieve_exchange_rates(['Singapore'], result[DATE].min(), result[DATE].max())

            if COUNTRY in result.columns and any (result.loc[result[COUNTRY] == 'Singapore']):
                pass
            elif TICKER in result.columns and any(result[TICKER].str.endswith('.SI')):
                print(result.loc[result[TICKER].str.endswith('.SI')])
                result.loc[result[TICKER].str.endswith('.SI'), COUNTRY] = 'Singapore'
            else:
                # only has US data
                if keep_fx_rate_col:
                    result['FXRate'] = 1
                return result
            
            logger.info('Merging FX data...')
            result = result.merge(fx[[DATE, COUNTRY, 'FXRate']], on=[DATE, COUNTRY], how='left')
            assert len(result) == original_length, '\n'+fx.loc[fx.duplicated(subset=[DATE, COUNTRY])].head(50).to_string()

            assert all(result['FXRate'].isna() | (result[COUNTRY] != 'United States')), result[COUNTRY].value_counts()
            result['FXRate'] = result['FXRate'].fillna(1)  # US Data

            result = result.copy()
            for col in relevant_cols:
                if col not in result:
                    logger.warning(f"{col} which was supposed to be converted to USD is not found in result!\n{result.columns}")
                result[col] = result[col] * result['FXRate']

            if not keep_fx_rate_col:
                result = result.drop(columns=['FXRate'])

            if COUNTRY not in original_result.columns:
                result = result.drop(columns=[COUNTRY])

            logger.info(f"Converted {relevant_cols} to USD")
            return result

        # Return the new wrapper function
        return wrapper
    return _outer



def retrieve_exchange_rates(countries: List[str], start_date: datetime, end_date: datetime, buffer=5):
    import yfinance as yf

    if len(countries) == 0:
        return pd.DataFrame(columns=[DATE, 'FX'])
    
    all_fx = []
    for country in countries:
        exchange = FOREX_MAP[country]
        fx = yf.download(exchange, start=utils_cal.add_bdays(start_date, -buffer), end=utils_cal.add_bdays(end_date, buffer)) 
        fx = fx[['Close']].rename(columns={'Close': 'FXRate'})
        fx = fx.stack(level=1).reset_index()
        fx = fx.rename(columns={'Ticker': 'Exchange'})
        fx['Country'] = fx['Exchange'].map({v: k for k, v in FOREX_MAP.items()})
        all_fx.append(fx)

    result = pd.concat(all_fx, ignore_index=True)
    result = result.drop_duplicates(subset=['Date', 'Exchange'])
    return result