import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

if __name__ == "__main__":
    # ticker = 'AAPL'
    # import yfinance as yf
    # aapl = yf.Ticker(ticker).info['country']
    # print(aapl)

    # import datetime
    # from data_retrieval import forex
    # print(forex.retrieve_exchange_rates(['Singapore'], datetime.datetime(2026, 1, 1), datetime.datetime(2026, 1, 30)))

    import datetime
    from data_retrieval import data_retrieval
    print(data_retrieval.retrieve_price_data_from_yfin(['AAPL'], datetime.datetime(2026, 1, 1), datetime.datetime(2026, 1, 30)))