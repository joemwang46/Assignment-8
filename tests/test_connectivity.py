import socket
import time
import threading
from gateway import run_gateway
from order_manager import run_ordermanager

def test_gateway_accepts_connections():
    t = threading.Thread(target=run_gateway, kwargs={"symbols":("AAPL",), "tick_hz":5}, daemon=True)
    t.start()
    time.sleep(0.2)
    with socket.create_connection(("127.0.0.1", 5001), timeout=2) as s:
        assert s is not None

def test_ordermanager_receives_order(capsys):
    t = threading.Thread(target=run_ordermanager, daemon=True)
    t.start()
    time.sleep(0.2)
    with socket.create_connection(("127.0.0.1", 5003), timeout=2) as s:
        s.sendall(b'{"id":1,"side":"BUY","symbol":"AAPL","qty":1,"price":123.4,"t":0}*')
    time.sleep(0.2)
    out = capsys.readouterr().out
    assert "BUY 1 AAPL" in out
