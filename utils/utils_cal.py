import datetime
import logging
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay

logger = logging.getLogger(__name__)


def add_bdays(start_date: datetime.datetime, days: int, holidays: list=None) -> datetime.datetime:
    if holidays is None:
        holidays = []
    
    try:
        ts = start_date + CustomBusinessDay(n=days, holidays=holidays)
        return ts.to_pydatetime()
    except Exception as e:
        logger.error(f"Error adding business days: {e}")
        raise e
    
def add_bdays_now(days: int, holidays: list=None) -> datetime.datetime:
    return add_bdays(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), days, holidays)


def bdate_range(start_date: datetime.datetime, end_date: datetime.datetime, holidays: list=None):
    if holidays is None:
        holidays = []
    
    try:
        bdays = pd.bdate_range(start=start_date, end=end_date, freq=CustomBusinessDay(holidays=holidays))
        return bdays.to_pydatetime().tolist()
    except Exception as e:
        logger.error(f"Error generating business date range: {e}")
        raise e


if __name__ == "__main__":
    # Example usage
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    print(f"Today: {today}")
    print(f"5 business days from now: {add_bdays_now(5)}")