## Test Setup
- **Processes:** Gateway, OrderBook, Strategy, OrderManager  
- **Tick Rate:** 20 Hz  
- **Data Points:** 1000 total ticks (Gateway limited)  
- **Shared Memory:** 3 symbols × dtype `[('S12','f8')]` → ~60 bytes  
- **Interprocess Communication:** TCP sockets + delimiter-framed JSON  
- **Synchronization:** `multiprocessing.Lock` guarding shared writes

---

## Benchmark Results

| Metric | Description | Result (Example) |
|--------|--------------|------------------|
| **Average Latency** | Time from Gateway tick emission → OrderManager confirmation | **≈ 11.4 ms** |
| **Throughput** | Processed ticks per second | **≈ 19.6 ticks/sec** |
| **Memory Footprint** | Shared array size | **60 bytes** |
| **Recovery Time** | Client reconnection after Gateway restart | **≈ 0.4 s** |

---

## Measurement Method
1. Added `tick` and `t_send` fields in Gateway’s price stream.  
2. Logged timestamps at:
   - `t_recv`: when Strategy received a tick  
   - `t_order`: when Strategy sent an order  
   - `t_exec`: when OrderManager confirmed execution  
3. Computed latency = `t_exec − t_send`.  
4. Measured throughput as total ticks processed ÷ runtime.

