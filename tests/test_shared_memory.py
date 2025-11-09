import multiprocessing as mp
import time
from shared_memory_utils import SharedPriceBook

def test_shared_book_read_write():
    symbols = ("AAPL","MSFT")
    name = "test_book"
    lock = mp.Lock()
    book = SharedPriceBook(symbols, name=name, create=True)
    book.update("AAPL", 150.0, lock=lock)
    assert abs(book.read("AAPL", lock=lock) - 150.0) < 1e-9
    book.close()
    book.unlink()
