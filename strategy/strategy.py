import pandas as pd
from enum import Enum, auto
import datetime as dt
from typing import Optional, List, Union, Callable
from dataclasses import dataclass

from portfolio.const_cols import DATE, TICKER, DOLLARS
from utils import utils_cal


class Interval(Enum):
    DAILY = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    YEARLY = auto()


class Action(Enum):
    BUY = auto()
    SELL = auto()    


@dataclass
class IntervalConfig():
    interval: Interval
    weekday: Optional[Union[List[int], int]] = None  # 0=Mon, 6=Sun; List of ints for multiples days of the week
    monthly_offset: Optional[Union[List[int], int]] = None  # e.g. 0 = first, -1 = last day; List of ints for multiple dates in the month
    month: Optional[Union[List[int], int]] = None   # 1–12; List of ints for multiple months in the year

    def validate(self):
        if self.interval == Interval.DAILY:
            if any([self.weekday, self.monthly_offset, self.month]):
                raise ValueError("DAILY should not have any config")

        elif self.interval == Interval.WEEKLY:
            if self.weekday is None:
                raise ValueError("WEEKLY requires weekday (0=Mon)")
            if self.monthly_offset is not None:
                raise ValueError(f"WEEKLY shouldn't have a non-None monthly-offset {self.monthly_offset}")
            if self.month is not None:
                raise ValueError(f"WEEKLY shouldn't have a non-None month {self.month}")
        
        elif self.interval == Interval.MONTHLY:
            if self.monthly_offset is None:
                raise ValueError("MONTHLY requires offset")
            if self.weekday is not None:
                raise ValueError(f"MONTHLY shouldn't have a non-None weekday {self.weekday}")
            if self.month is not None:
                raise ValueError(f"MONTHLY shouldn't have a non-None month {self.month}")


        
        elif self.interval == Interval.YEARLY:
            if self.month is None or self.offset is None:
                raise ValueError("YEARLY requires month and offset")
            if self.weekday is not None:
                raise ValueError(f"YEARLY shouldn't have a non-None weekday {self.weekday}")


@dataclass
class Trade:
    ticker: str
    action: Action 
    dollars: int = 0


class Portfolio:
    def __init__(self):
        self.long_only = True
        self.ignore_sell_errors = True
        self.holdings = {}  # {ticker: dollars}

    def update(self, trade: Trade):
        """
        Update portfolio holdings based on the trade action and dollars.
        If long_only is True, we should not allow negative dollars (i.e. short positions) but we can liquidate existing longs.
        """
        if trade.ticker not in self.holdings:
            self.holdings[trade.ticker] = 0
        
        if trade.action == Action.BUY:
            self.holdings[trade.ticker] += trade.dollars
        
        elif trade.action == Action.SELL:
            if self.long_only and self.holdings[trade.ticker] - trade.dollars < 0:
                if self.ignore_sell_errors:
                    trade.dollars = 0  # Liquidate
                else:
                    raise ValueError(f"Cannot execute SELL trade for {trade.ticker} with dollars {trade.dollars} as it would result in negative holdings in a long-only portfolio.")
            self.holdings[trade.ticker] -= trade.dollars

    
    def get_portfolio_df(self) -> pd.DataFrame:
        return pd.DataFrame({
            TICKER: list(self.holdings.keys()),
            DOLLARS: list(self.holdings.values())
        })


@dataclass
class Context:
    date: dt.datetime
    portfolio: Portfolio
    data: pd.DataFrame


DecisionFn = Callable[[Context], List[Trade]]  # lambda curr_portfolio_on_trade_date, trade_date: List of Trades to make on trade date


class Strategy:
    def __init__(self, interval_config: IntervalConfig, ret_data: pd.DataFrame, decision_f: DecisionFn = None, ):
        self.interval_config: IntervalConfig = interval_config
        self.decision_f = decision_f  
        self.ret_data = ret_data  # Preprocessed returns/price for all tickers and dates (or other relevant data required for decision making)
        self.portfolio = Portfolio(long_only=True, ignore_sell_errors=True)
        

    def run(self, start_date: dt.datetime, end_date: dt.datetime) -> pd.DataFrame:
        """
        Runs given Strategy from start_date to end_date at the given interval_config with the preset Trades given the preset predicate
        :return DataFrame with columns [Date, Ticker, Quantity], where Quantity is the total Dollars in portfolio after executing Action on Date
        """

        all_portfolios = []
        for date in utils_cal.bdate_range(start_date, end_date):
            trades_for_date: List[Trade] = self.decision_f(Context(date, self.portfolio, self.ret_data))
            for trade in trades_for_date:
                self.portfolio.update(trade)

            curr_portfolio_on_trade_date = self.portfolio.get_portfolio_df()
            curr_portfolio_on_trade_date[DATE] = date
            all_portfolios.append(curr_portfolio_on_trade_date[[DATE, TICKER, DOLLARS]])
        
        return pd.concat(all_portfolios, ignore_index=True)

