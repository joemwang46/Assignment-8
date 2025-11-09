import json
import numpy as np
from multiprocessing.shared_memory import SharedMemory

MESSAGE_DELIMITER = b"*"
ENCODING = "utf-8"

def dumps(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":")).encode(ENCODING)

def loads(b: bytes):
    return json.loads(b.decode(ENCODING))

def send_delimited(sock, payload_bytes: bytes):
    sock.sendall(payload_bytes + MESSAGE_DELIMITER)

def recv_delimited(sock, buffer: bytearray):
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            return
        buffer.extend(chunk)
        while True:
            i = buffer.find(MESSAGE_DELIMITER)
            if i == -1:
                break
            frame = bytes(buffer[:i])
            del buffer[:i+1]
            yield frame

class SharedPriceBook:
    def __init__(self, symbols, name=None, create=False):
        self.symbols = [s.encode("ascii") for s in symbols]
        self.dtype = np.dtype([("symbol", "S12"), ("price", "f8")])
        self.n = len(symbols)
        self.nbytes = self.n * self.dtype.itemsize

        if create:
            self.shm = SharedMemory(create=True, size=self.nbytes, name=name)
            self.arr = np.ndarray((self.n,), dtype=self.dtype, buffer=self.shm.buf)
            for i, s in enumerate(self.symbols):
                self.arr[i] = (s, np.nan)
            self.name = self.shm.name
        else:
            self.shm = SharedMemory(name=name)
            self.arr = np.ndarray((self.n,), dtype=self.dtype, buffer=self.shm.buf)
            self.name = name

        self.index = {s: i for i, s in enumerate(self.symbols)}

    def update(self, symbol: str, price: float, lock=None):
        i = self.index.get(symbol.encode("ascii"))
        if i is None:
            return
        if lock:
            with lock:
                self.arr[i]["price"] = price
        else:
            self.arr[i]["price"] = price

    def read(self, symbol: str, lock=None):
        i = self.index.get(symbol.encode("ascii"))
        if i is None:
            return float("nan")
        if lock:
            with lock:
                return float(self.arr[i]["price"])
        return float(self.arr[i]["price"])

    def snapshot(self, lock=None) -> dict:
        if lock:
            with lock:
                return {row["symbol"].decode("ascii"): float(row["price"]) for row in self.arr}
        return {row["symbol"].decode("ascii"): float(row["price"]) for row in self.arr}

    def close(self):
        self.shm.close()

    def unlink(self):
        self.shm.unlink()
