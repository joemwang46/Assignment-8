import socket
import time
import threading
import collections
from shared_memory_utils import recv_delimited, loads, send_delimited, dumps, SharedPriceBook

HOST = "127.0.0.1"
NEWS_PORT = 5002
ORDER_PORT = 5003

def run_strategy(
    symbols,
    shm_name,
    lock,
    symbol="AAPL",
    short_w=10,
    long_w=30,
    bullish=60,
    bearish=40,
    qty=10,
):
    book = SharedPriceBook(symbols, name=shm_name, create=False)

    buf = collections.deque(maxlen=max(short_w, long_w))
    position = None 

    sentiment = {"val": 50}

    def news_loop():
        buffer = bytearray()
        while True:
            try:
                with socket.create_connection((HOST, NEWS_PORT), timeout=5) as s:
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    buffer.clear()
                    for frame in recv_delimited(s, buffer):
                        msg = loads(frame)
                        if msg.get("type") == "news":
                            sentiment["val"] = int(msg["sentiment"])
            except OSError:
                time.sleep(0.5)

    threading.Thread(target=news_loop, daemon=True).start()

    def connect_order_sock():
        while True:
            try:
                sock = socket.create_connection((HOST, ORDER_PORT), timeout=5)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                return sock
            except OSError:
                time.sleep(0.5)

    order_sock = connect_order_sock()

    def ma(seq, w):
        if len(seq) < w:
            return None
        s = 0.0
        items = list(seq)[-w:]
        for v in items:
            s += v
        return s / w

    while True:
        px = book.read(symbol, lock=lock)
        if px == px:
            buf.append(px)
            m_s = ma(buf, short_w)
            m_l = ma(buf, long_w)

            price_sig = None
            if m_s is not None and m_l is not None:
                price_sig = "BUY" if m_s > m_l else "SELL"

            n = sentiment["val"]
            news_sig = "BUY" if n > bullish else ("SELL" if n < bearish else "NEUTRAL")

            final = None
            if price_sig == "BUY" and news_sig == "BUY":
                final = "BUY"
            elif price_sig == "SELL" and news_sig == "SELL":
                final = "SELL"

            if final == "BUY" and position != "long":
                order = {"id": int(time.time()*1000), "side":"BUY", "symbol":symbol, "qty":qty, "price":px, "t":time.time()}
                try:
                    send_delimited(order_sock, dumps(order))
                    position = "long"
                except OSError:
                    order_sock.close()
                    order_sock = connect_order_sock()

            elif final == "SELL" and position != "short":
                order = {"id": int(time.time()*1000), "side":"SELL", "symbol":symbol, "qty":qty, "price":px, "t":time.time()}
                try:
                    send_delimited(order_sock, dumps(order))
                    position = "short"
                except OSError:
                    order_sock.close()
                    order_sock = connect_order_sock()

        time.sleep(0.02)
