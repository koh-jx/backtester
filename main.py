
if __name__ == "__main__":
    ticker = 'AAPL'
    import yfinance as yf
    aapl = yf.Ticker(ticker).dividends
    print(aapl.reset_index())
