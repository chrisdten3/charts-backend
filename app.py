from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from efCalc import get_portfolio_allocations
from efCalc import get_history
from efCalc import get_stock_data

app = Flask(__name__)
CORS(app)

@app.route("/api/portfolio", methods=["GET"])
def get_portfolio():
    tickers = request.args.get("tickers")
    tickers = tickers.split(",")
    #tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    max_sharpe_portfolio, min_vol_portfolio = get_portfolio_allocations(tickers)

    return jsonify({
        "max_sharpe_portfolio": max_sharpe_portfolio,
        "min_vol_portfolio": min_vol_portfolio
    })

@app.route("/api/history", methods=["GET"])
def get_stock_history():
    ticker = request.args.get("ticker")
    history = get_history(ticker)

    return history

@app.route("/api/stock", methods=["GET"])
def get_stock():
    ticker = request.args.get("ticker")
    info = get_stock_data(ticker)

    return info


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
