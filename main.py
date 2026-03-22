import logging
import datetime as dt

from portfolio import generate_portfolio_from_csv as portf_gen
from btest import run_btest
from visualisation import visualisation
from portfolio.const_cols import TICKER, WEIGHT, PNL, DIVIDEND_PNL


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


if __name__ == "__main__":
    tickers = ['AAPL', 'O39.SI']
    weights = [0.5, 0.5]
    source_portfolio = {TICKER: tickers, WEIGHT: weights}

    # Create portfolio
    portfolio_df = portf_gen.get_portfolio(source_portfolio)
    start_date = dt.datetime(2020, 1, 1)
    end_date = dt.datetime(2026, 3, 15)

    # TODO run portfolio on Strategy (adding the Date column)

    # Run backtest on portfolio df
    output = run_btest.run_backtest(portfolio_df, start_date, end_date, export_to_csv=False)
    visualisation.plot_portfolio(output, y_axis_col=[PNL, DIVIDEND_PNL], run_yearly=True)



# if __name__ == "__main__":
#     # ticker = 'AAPL'
#     # import yfinance as yf
#     # aapl = yf.Ticker(ticker).info['country']
#     # print(aapl)

#     # import datetime
#     # from data_retrieval import forex
#     # print(forex.retrieve_exchange_rates(['Singapore'], datetime.datetime(2026, 1, 1), datetime.datetime(2026, 1, 30)))

#     import datetime
#     from data_retrieval import data_retrieval
#     print(data_retrieval.retrieve_price_data_from_yfin(['AAPL'], datetime.datetime(2026, 1, 1), datetime.datetime(2026, 1, 30)))