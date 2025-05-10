# rolling_k_auto_trade_api/main.py - FastAPI Entry Point for Auto Trading System
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rolling_k_auto_trade_api.strategies import (
    run_rebalance_for_date,
    auto_trade_on_rebalance,
    check_sell_conditions,
    generate_performance_report
)
from rolling_k_auto_trade_api.models import BuyOrderRequest, SellOrderRequest
from rolling_k_auto_trade_api.orders import router as orders_router
import pandas as pd
from datetime import datetime

app = FastAPI(title="Rolling-K Auto Trade API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include auto-trade and order APIs
app.include_router(orders_router)

@app.get("/")
def root():
    return {"message": "Rolling-K Auto Trade API is running."}

@app.get("/rebalance/latest")
def get_rebalance_latest():
    try:
        today = pd.to_datetime(datetime.today().replace(day=1))
        date_str = today.strftime('%Y-%m-%d')
        return run_rebalance_for_date(date_str)
    except Exception as e:
        return {"error": str(e)}

@app.get("/rebalance/run/{date}")
def run_rebalance(date: str):
    return run_rebalance_for_date(date)

@app.post("/order/buy")
def buy_stocks(request: BuyOrderRequest):
    return execute_buy_order(request)

@app.post("/order/sell")
def sell_stocks(request: SellOrderRequest):
    return execute_sell_order(request)

@app.get("/sell/check")
def check_sell():
    return check_sell_conditions()

@app.get("/dashboard")
def dashboard():
    return generate_performance_report()
