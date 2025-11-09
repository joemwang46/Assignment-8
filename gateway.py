import socket
import threading
import time
import random
from shared_memory_utils import dumps, send_delimited

HOST = "127.0.0.1"
PRICE_PORT = 5001
NEWS_PORT = 5002

class BroadcastServer:
    def __init__(self, host, port):
        self.addr = (host, port)
        self.clients = set()
        self.lock = threading.Lock()
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._accept_loop, daemon=True).start()
        return self

    def _accept_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(self.addr)
            srv.listen()
            while self.running:
                try:
                    conn, _ = srv.accept()
                    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    with self.lock:
                        self.clients.add(conn)
                except OSError:
                    break

    def broadcast(self, payload: bytes):
        dead = []
        with self.lock:
            for c in list(self.clients):
                try:
                    send_delimited(c, payload)
                except OSError:
                    dead.append(c)
            for d in dead:
                try: d.close()
                except: pass
                self.clients.discard(d)

    def stop(self):
        self.running = False
        with self.lock:
            for c in list(self.clients):
                try: c.close()
                except: pass
            self.clients.clear()

def run_gateway(symbols=("AAPL","MSFT","SPY"), tick_hz=20, seed=42, max_ticks=1000):
    random.seed(seed)
    price_srv = BroadcastServer(HOST, PRICE_PORT).start()
    news_srv  = BroadcastServer(HOST, NEWS_PORT).start()

    prices = {s: 100.0 + 5*random.random() for s in symbols}
    tick = 0
    try:
        while tick < max_ticks:
            tick += 1

            for s in symbols:
                prices[s] += random.gauss(0, 0.06)

            price_msg = dumps({"type":"prices","t":time.time(),"data":prices,"tick":tick})
            price_srv.broadcast(price_msg)

            if random.random() < 0.6:
                sentiment = int(random.uniform(0, 100))
                news_msg = dumps({"type":"news","t":time.time(),"sentiment":sentiment,"tick":tick})
                news_srv.broadcast(news_msg)

            time.sleep(1.0/tick_hz)
    except KeyboardInterrupt:
        pass
    finally:
        print(f"Gateway finished after {tick} ticks.")
        price_srv.stop()
        news_srv.stop()
