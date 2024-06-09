import yfinance as yf
import pandas as pd  
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.optimize as sco

np.random.seed(777)

def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    today_open = stock.history(period="1d")['Open'][0]

    news = stock.news
    top_3_news = sorted(news, key=lambda x: x['providerPublishTime'], reverse=True)[:3]

    output = {
        "symbol": symbol,
        "today_open": today_open,
        "news": top_3_news
    }

    return json.dumps(output)

def get_history(symbol):
    name = yf.Ticker(symbol)
    ticker = name.history(period="1y")

    ticker.index = pd.to_datetime(ticker.index)

    ticker['Date'] = ticker.index

    if not {'Date', 'Open', 'High', 'Low', 'Close'}.issubset(ticker.columns):
        raise ValueError("DataFrame must contain 'Date', 'Open', 'High', 'Low', 'Close' columns")
    

    series_data = []

    for index,row in ticker.iterrows():
        timestamp = int(row['Date'].timestamp() * 1000)
        open_price = row['Open']
        high_price = row['High']
        low_price = row['Low']
        close_price = row['Close']
        
        series_data.append([timestamp, open_price, high_price, low_price, close_price])
    
    output = {
        "series": [{
            "data": series_data
        }]
    }
    
    return json.dumps(output)


def get_portfolio_allocations(tickers, period="1y", num_portfolios=25000, risk_free_rate=0.0515):
    # Grab data for multiple tickers
    data = yf.download(tickers, period=period)["Close"]
    returns = data.pct_change()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
        returns = np.dot(mean_returns, weights) * 252
        std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        return std, returns

    weights_record = np.random.random((num_portfolios, len(tickers)))
    weights_record /= weights_record.sum(axis=1)[:, np.newaxis]

    portfolio_std_devs = np.zeros(num_portfolios)
    portfolio_returns = np.zeros(num_portfolios)

    for i in range(num_portfolios):
        portfolio_std_devs[i], portfolio_returns[i] = portfolio_annualised_performance(
            weights_record[i], mean_returns, cov_matrix
        )

    sharpe_ratios = (portfolio_returns - risk_free_rate) / portfolio_std_devs

    max_sharpe_idx = np.argmax(sharpe_ratios)
    min_vol_idx = np.argmin(portfolio_std_devs)

    max_sharpe_allocation = {data.columns[i]: round(weight * 100, 2) for i, weight in enumerate(weights_record[max_sharpe_idx])}
    min_vol_allocation = {data.columns[i]: round(weight * 100, 2) for i, weight in enumerate(weights_record[min_vol_idx])}

    max_sharpe_portfolio = {
        "Annualised Return": round(portfolio_returns[max_sharpe_idx], 2),
        "Annualised Volatility": round(portfolio_std_devs[max_sharpe_idx], 2),
        "Allocation": max_sharpe_allocation
    }

    min_vol_portfolio = {
        "Annualised Return": round(portfolio_returns[min_vol_idx], 2),
        "Annualised Volatility": round(portfolio_std_devs[min_vol_idx], 2),
        "Allocation": min_vol_allocation
    }

    return max_sharpe_portfolio, min_vol_portfolio

