from multiprocessing import Process, Lock
from gateway import run_gateway
from orderbook import run_orderbook
from strategy import run_strategy
from order_manager import run_ordermanager
import time

SYMBOLS = ("AAPL","MSFT","SPY")
SHM_NAME = "pricebook_demo"
BULLISH = 60
BEARISH = 40

if __name__ == "__main__":
    lock = Lock()

    gateway = Process(target=run_gateway, kwargs={"symbols": SYMBOLS})
    orderbook = Process(target=run_orderbook, kwargs={"symbols": SYMBOLS, "shm_name": SHM_NAME, "lock": lock})
    ordermanager = Process(target=run_ordermanager)
    strategy = Process(target=run_strategy, kwargs={"symbols": SYMBOLS, "shm_name": SHM_NAME, "lock": lock, "symbol": "AAPL"})

    gateway.start()
    orderbook.start()
    time.sleep(1)
    strategy.start()
    ordermanager.start()

    for p in [gateway, orderbook, strategy, ordermanager]:
        p.join()
