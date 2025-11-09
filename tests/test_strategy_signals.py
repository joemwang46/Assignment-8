import multiprocessing as mp
import time
from gateway import run_gateway
from orderbook import run_orderbook
from strategy import run_strategy
from order_manager import run_ordermanager

SYMBOLS = ("AAPL","MSFT","SPY")
SHM_NAME = "test_strategy_book"

def test_end_to_end_orders_flow(capsys):
    lock = mp.Lock()
    procs = [
        mp.Process(target=run_gateway, kwargs={"symbols": SYMBOLS, "tick_hz": 40}, daemon=True),
        mp.Process(target=run_orderbook, kwargs={"symbols": SYMBOLS, "shm_name": SHM_NAME, "lock": lock}, daemon=True),
        mp.Process(target=run_ordermanager, daemon=True),
        mp.Process(target=run_strategy, kwargs={"symbols": SYMBOLS, "shm_name": SHM_NAME, "lock": lock, "short_w":5, "long_w":8, "bullish":55, "bearish":45, "symbol":"AAPL"}, daemon=True),
    ]
    for p in procs: p.start()
    time.sleep(3.0)
    out = capsys.readouterr().out
    for p in procs: p.terminate()
    assert "Received Order" in out
