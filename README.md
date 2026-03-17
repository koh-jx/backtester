Backtesting environment for simple trading strategies using python.

Long-only strategies US + SG only

# TODO:
- Price data retrieval from API + caching data locally to prevent repeated API calls
- Portfolio generation and PnL calculation + csv outpu
    - Currently can use a simple CSV input for tickers, then retrieve pricing data from cache if tickers exist, otherwise retrieve from API and cache locally for future use
- Strategy implementation
- Portfolio optimization (factor-based + hedging)
- Dividend handling