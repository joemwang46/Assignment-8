Gateway (TCP Server)
├── Price stream (port 5001)
├── News sentiment stream (port 5002)
↓
OrderBook (Client)
└── Updates shared memory (latest prices)
Strategy (Client)
├── Reads shared memory prices
├── Listens to sentiment feed
└── Sends orders → OrderManager
OrderManager (TCP Server)
└── Logs executed trades in real time


---

## Components

| File | Description |
|------|--------------|
| `gateway.py` | Streams random-walk prices + random sentiment values. |
| `orderbook.py` | Subscribes to Gateway, maintains a shared NumPy price book. |
| `strategy.py` | Reads shared memory, applies **moving average + sentiment** signals. |
| `order_manager.py` | Receives and logs orders from Strategy clients. |
| `shared_memory_utils.py` | Defines `SharedPriceBook` helper and socket message utilities. |
| `main.py` | Orchestrates all processes (runs the entire system). |
| `tests/` | Unit tests for connectivity, shared memory, and strategy logic. |
| `performance_report.md` | Contains latency and throughput measurements. |
| `video.mp4` | Demo of the live system running independently. |

---

## How to Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip numpy pytest
python main.py
