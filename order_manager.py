import socket
import threading
from shared_memory_utils import recv_delimited, loads

HOST = "127.0.0.1"
ORDER_PORT = 5003

def run_ordermanager():
    addr = (HOST, ORDER_PORT)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(addr)
        srv.listen()
        print(f"[OrderManager] listening on {addr}", flush=True)

        def handle(conn):
            buffer = bytearray()
            for frame in recv_delimited(conn, buffer):
                try:
                    order = loads(frame)
                    print(
                        f"Received Order {order['id']}: {order['side']} "
                        f"{order['qty']} {order['symbol']} @ {order['price']:.2f}",
                        flush=True,
                    )
                except Exception as e:
                    print("Bad order:", e, flush=True)
            conn.close()

        while True:
            conn, _ = srv.accept()
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            threading.Thread(target=handle, args=(conn,), daemon=True).start()
