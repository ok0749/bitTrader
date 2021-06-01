from flask import Flask, render_template, request, jsonify, Response
from trade import get_price_data, buy, sell, get_balance, get_15_price_data
import time
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/buyCoin")
def buyCoin():
    # 코인 코드
    ticket = request.args.get("ticker")
    currency, coin = ticket.split("-")
    x_test, now_open_price = get_price_data(ticket)  # 과거 1380분 데이터, 현재 시가
    (
        check,
        max_minute,
        my_money,
        buy_price,
        after_trade_my_money,
        message,
        end_time,
        pred,
    ) = buy(ticket, coin)
    return jsonify(
        {
            "check": check,
            "max_minute": max_minute,
            "my_money": my_money,
            "buy_price": buy_price,
            "after_trade_my_money": after_trade_my_money,
            "message": message,
            "end_time": end_time,
            "pred": pred.tolist(),
        }
    )


@app.route("/sellCoin")
def sellCoin():
    # 코인 코드
    ticket = request.args.get("ticker")
    max_minute = request.args.get("max_minute")
    max_minute = int(max_minute)
    currency, coin = ticket.split("-")
    # x_test, now_open_price = get_price_data(ticket)  # 과거 1380분 데이터, 현재 시가
    # check, max_minute, my_money, buy_price, after_trade_my_money = buy(ticket, coin)
    # 예상 최대 시점까지 쉰다
    time.sleep(60 * max_minute)
    sell_price, after_trade_my_money, message = sell(ticket, coin)
    return jsonify(
        {
            "sell_price": sell_price,
            "after_trade_my_money": after_trade_my_money,
            "message": message,
        }
    )


@app.route("/chart")
def chart():
    ticker = request.args.get("ticker")
    df, _ = get_price_data(ticker)
    columns = df.columns.tolist()
    values = df.values.tolist()
    return jsonify({"columns": columns, "values": values})


@app.route("/chart15")
def chart15():
    time.sleep(15 * 60)
    ticker = request.args.get("ticker")
    df = get_15_price_data(ticker)
    columns = df.columns.tolist()
    values = df.values.tolist()
    return jsonify({"columns": columns, "values": values})


if __name__ == "__main__":
    app.run(debug=True)