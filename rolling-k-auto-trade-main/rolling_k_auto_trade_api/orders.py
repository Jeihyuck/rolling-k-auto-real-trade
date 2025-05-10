# rolling_k_auto_trade_api/orders.py (순환참조 해결 포함)
from fastapi import APIRouter, HTTPException
from rolling_k_auto_trade_api.models import BuyOrderRequest, SellOrderRequest
import json
import os
from datetime import datetime
import pandas as pd
import requests

router = APIRouter()
TRADE_STATE = {}

LOG_DIR = "./rolling_k_auto_trade_api/logs"
os.makedirs(LOG_DIR, exist_ok=True)

print("✅ orders.py loaded")


# ✅ 환경 설정: 모의/실거래 분기
IS_PRACTICE = os.getenv("KIS_ENV", "practice") == "practice"
KIS_BASE_URL = "https://openapivts.koreainvestment.com:29443" if IS_PRACTICE else "https://openapi.koreainvestment.com:9443"
APP_KEY = os.getenv("KIS_APP_KEY", "YOUR_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET", "YOUR_APP_SECRET")
ACCESS_TOKEN = os.getenv("KIS_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")
ACCOUNT = os.getenv("KIS_ACCOUNT", "YOUR_ACCOUNT_NUMBER")
CANO = ACCOUNT[:8]
ACNT_PRDT_CD = ACCOUNT[8:]

def log_order(data: dict, order_type: str):
    log_file = os.path.join(LOG_DIR, f"{order_type}_orders.log")
    with open(log_file, "a") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

@router.post("/order/buy")
def buy_stock(order: BuyOrderRequest):
    order_data = order.dict()
    order_data["timestamp"] = datetime.now().isoformat()
    log_order(order_data, "buy")
    TRADE_STATE[order.code] = order_data
    return {"message": "Buy order logged", "data": order_data}

@router.post("/order/sell")
def sell_stock(order: SellOrderRequest):
    order_data = order.dict()
    order_data["timestamp"] = datetime.now().isoformat()
    log_order(order_data, "sell")
    TRADE_STATE.pop(order.code, None)
    return {"message": "Sell order logged", "data": order_data}

@router.get("/order/status")
def get_order_status():
    return {"open_positions": TRADE_STATE, "count": len(TRADE_STATE)}

def kis_get_price(code):
    url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100",
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": code,
    }
    res = requests.get(url, headers=headers, params=params, verify=False)
    if res.status_code == 200:
        return float(res.json()['output']['stck_prpr'])
    return 0

def kis_send_order(code, qty, order_type):
    url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/trading/order-cash"
    tr_id = "VTTC0802U" if order_type == "buy" else "VTTC0801U"
    if not IS_PRACTICE:
        tr_id = "TTTC0802U" if order_type == "buy" else "TTTC0801U"

    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P"
    }
    body = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "00",
        "ORD_QTY": str(qty),
        "ORD_UNPR": "0"
    }
    res = requests.post(url, headers=headers, json=body, verify=False)
    return res.json()

@router.post("/auto-trade/run")
def run_auto_trade():
    # ✅ 순환 참조 방지를 위해 함수 내부에서 import
    from rolling_k_auto_trade_api.strategies import run_rebalance_for_date, get_target_price, check_sell_conditions

    today = pd.Timestamp.today().replace(day=1)
    date_str = today.strftime('%Y-%m-%d')
    rebalance_data = run_rebalance_for_date(date_str)

    results = []

    for stock in rebalance_data.get("stocks", []):
        code = stock.get("code")
        weight = stock.get("weight", 0)
        target_price = get_target_price(code)
        current_price = kis_get_price(code)

        if current_price > target_price:
            result = kis_send_order(code, int(weight), order_type="buy")
            results.append({"code": code, "action": "buy", "price": current_price, "result": result})

        if check_sell_conditions(code):
            result = kis_send_order(code, int(weight), order_type="sell")
            results.append({"code": code, "action": "sell", "price": current_price, "result": result})

    return {"message": "KIS auto trade completed.", "mode": "practice" if IS_PRACTICE else "real", "details": results}
