import socket
import time
import threading
from shared_memory_utils import recv_delimited, loads, SharedPriceBook

HOST = "127.0.0.1"
PRICE_PORT = 5001

def run_orderbook(symbols, shm_name, lock):
    book = SharedPriceBook(symbols, name=shm_name, create=True)
    print(f"[OrderBook] shared_memory_name={book.name}", flush=True)

    def price_loop():
        buffer = bytearray()
        while True:
            try:
                with socket.create_connection((HOST, PRICE_PORT), timeout=5) as s:
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    buffer.clear()
                    for frame in recv_delimited(s, buffer):
                        msg = loads(frame)
                        if msg.get("type") == "prices":
                            for sym, px in msg["data"].items():
                                book.update(sym, float(px), lock=lock)
            except OSError:
                time.sleep(0.5)

    t = threading.Thread(target=price_loop, daemon=True)
    t.start()
    t.join()
