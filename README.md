Backtesting environment for simple trading strategies using python.

Long-only strategies US + SG only

# Features
- Price data retrieval from API 
- PnL calculation + csv output
- Add weights/Dollar amounts to portfolio
    - CumReturn Dollar adjustment

# TODO:
- Dividend handling
- Conversion of prices into USD in data_retrieval (if not already USD)
- Strategy class or something 
    - Enable buying or selling (unwinding long position)
    - then create basic strategy + configs: 
    - DCA, momentum, mean reversion, etc.
- Matplotlib visualization of backtest results (add use of jupyter)
- Caching data locally to prevent repeated API calls
- Strategy implementation
- Portfolio optimization (factor-based + hedging)
