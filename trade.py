import numpy as np
import pyupbit
import datetime
import time
import matplotlib.pyplot as plt
from joblib import load
from keras.models import load_model

# upbit api key
# 본인의 값으로 변경한다
access = "Bk1xNmQmJ9QcrdZg8bs3LzwSYyzOVb5NH3Kk89z6"
secret = "iWCrQsQawfr3pQxz7UBBAhYOAtPOe9rZJUxSodTw"

upbit = pyupbit.Upbit(access, secret)
fee = 0.0005  # 수수료
least_price = 1000  # 최저 거래 금액

# 현재 자산 불러오는 함수
def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b["currency"] == ticker:
            if b["balance"] is not None:
                return float(b["balance"])
            else:
                return 0
    return 0


# 현재 시점에서 과거 1380분 시가, 종가, 고가, 저가, 거래량 불러오는 함수
def get_price_data(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=1380)
    now_open_price = df["open"].iloc[-1]
    # 과거 데이터 데이터프레임, 현재 시가 반환
    return df[["open"]].T, now_open_price


# 현재 시점에서 과거 15분 시가, 종가, 고가, 저가, 거래량 불러오는 함수
def get_15_price_data(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=15)
    # 15분 데이터 데이터프레임,
    return df[["open"]].T


# 현재가 불러오는 함수
def get_current_price(ticker):
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


# 예측 함수
def predict(ticket):
    # 과거 데이터, 현재 시가
    x_test, now_open_price = get_price_data(ticket)
    model = load_model("lstm.h5")
    # pred = model.predict(x_test / now_open_price)  # 예측
    pred = model.predict(x_test)  # 예측
    # max_open_price = round(np.max(pred) * now_open_price, 2)  # 예상 최대 시가
    max_open_price = round(np.max(pred), 2)  # 예상 최대 시가
    max_minute = np.int(np.argmax(pred)) + 1  # 예상 최대 시점
    print("현재 시가: ", now_open_price, "예측 최고 시가: ", max_open_price)
    return pred, now_open_price, max_open_price, max_minute


# 매수 함수
def buy(ticket, coin):
    currency = ticket.split("-")[0]
    check = False
    buy_price = get_current_price(ticket)  # 현재가(매수 금액)
    print("매수 금액: ", buy_price)
    now_time = datetime.datetime.now()  # 매수 시간
    my_money = get_balance(currency)  # 내 원화 잔고
    pred, now_open_price, max_open_price, max_minute = predict(ticket)
    after_trade_my_money = ""
    message = ""
    end_time = ""
    # 예상 최대 시가가 현재 시가 보다 크고, 현재 원화 잔고가 1000(최저 거래 금액)보다 크면 전부 산다
    if (max_open_price > now_open_price) and (my_money > least_price):
        # if True:
        end_time = now_time + datetime.timedelta(minutes=max_minute + 1)  # 매도 시간
        print(
            "몇 분 후?: ",
            max_minute,
            "매수 시점 시간: ",
            now_time,
            "매도 시간: ",
            end_time,
        )
        upbit.buy_market_order(ticket, my_money * (1 - fee))
        # 거래 했으면 True 반환
        check = True
        after_trade_my_money = upbit.get_balance(currency)
        print("매수 후 남은 금액: ", after_trade_my_money)
    elif max_open_price <= now_open_price:
        print("내려갈 것이라 예상됨, 거래 안함")
        message = "내려갈 것이라 예상됨, 거래 안함"
        # time.sleep(60 * 15)
        # return autoTrade()
    else:
        print("현재 잔고가 최저 거래 금액보다 작음")
        message = "현재 잔고가 최저 거래 금액보다 작음"
    #  거래 여부, 예상 최고가 시간, 매수 전 내 자산, 매수시 코인 금액, 매수 후 내 자산
    return (
        check,
        max_minute,
        my_money,
        buy_price,
        after_trade_my_money,
        message,
        end_time,
        pred,
    )


# 매도 함수
def sell(ticket, coin):
    sell_price = ""
    after_trade_my_money = ""
    message = ""
    currency = ticket.split("-")[0]
    # 현재 코인 잔고
    coin_count = get_balance(coin)
    # 코인이 거래할 수 있는 최소 개수 보다 많으면
    if coin_count > 0.0001:
        # 매도 시 코인 가격
        sell_price = get_current_price(ticket)
        print("매도 금액: ", sell_price)
        upbit.sell_market_order(ticket, coin_count * (1 - fee))
        # 결과 반영까지 3초 쉰다
        time.sleep(3)
        # 매도 후 내 자산
        after_trade_my_money = get_balance(currency)
    else:
        print("코인 개수 부족")
        message = "코인 개수 부족"
    print(sell_price, after_trade_my_money, message)
    return sell_price, after_trade_my_money, message
