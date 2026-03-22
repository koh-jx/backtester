Backtesting environment for simple trading strategies using python.

Long-only strategies US + SG only

# Features
- Price data retrieval from API 
- PnL calculation + csv output
- Add weights/Dollar amounts to portfolio
    - CumReturn Dollar adjustment
- Dividend handling
- Conversion of prices into USD in data_retrieval (if not already USD)

# TODO:
- Strategy class or something 
    - Enable buying or selling (unwinding long position)
    - then create basic strategy + configs: 
    - DCA, momentum, mean reversion, etc.
- Matplotlib visualization of backtest results (add use of jupyter)
- Caching data locally to prevent repeated API calls
- Strategy implementation
- Portfolio optimization (factor-based + hedging)
- Dividend handling 
    - Number of shares on SOD pay date (using EOD FX) is factored in (which is wrong but not critical). Should be number of shares on ex-date, then pay out that amount * FX on pay date (not sure SOD or EOD)


# KIV:
- Lot size handling for SG stocks (actually doesn't really matter since backtesting is on Dollar amounts)