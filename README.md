# Online Ticket Selling System (OS Project)

This repository contains a Python skeleton that matches the required class structure and OS concepts (concurrency, IPC, fault tolerance, and benchmarking). It is intentionally minimal and focuses on interfaces only.

## Refined Architecture (High-Level)
Clients send ticket requests to a LoadBalancer, which routes them to active TicketServer nodes. A leader node owns the source of truth for inventory and replicates state to follower nodes. Two-phase commit (prepare/commit/rollback) ensures ticket deductions only finalize after reservation/payment success. HealthChecker heartbeats detect failures and trigger rerouting to surviving servers.

## Project Structure
```
ticket_system/
  protocol.py       # MessageProtocol (shared message format)
  inventory.py      # InventoryManager with locking (critical section)
  server.py         # TicketServer (leader/follower, peer sync)
  coordinator.py    # LoadBalancer + HealthChecker
  client.py         # Client
  benchmark.py      # BenchmarkRunner
```

## Next Steps (Module Breakdown)
| Module | Next step to complete |
| --- | --- |
| `protocol.py` | Finalize message schemas, error codes, and versioning; document required fields for BUY/RESERVE/COMMIT/ROLLBACK. |
| `inventory.py` | Implement lock-protected reserve/commit/rollback, add timeouts, and release locks on failure to avoid deadlocks. |
| `server.py` | Implement socket/RPC server, handle client requests, peer sync, leader-follower replication, and 2PC handlers. |
| `coordinator.py` | Implement round-robin routing, heartbeat loop, and server removal/addition on health changes. |
| `client.py` | Implement connection logic and request flow (reserve -> commit/rollback). |
| `benchmark.py` | Implement virtual clients, metrics collection (throughput/latency), plotting, and fault injection tests. |

## Suggested Build Order
1. Define protocol schemas and request/response types.
2. Implement InventoryManager with correct locking behavior.
3. Implement TicketServer networking and request handling.
4. Add LoadBalancer routing and HealthChecker heartbeats.
5. Add leader-follower replication and two-phase commit.
6. Build BenchmarkRunner and produce scalability/fault-tolerance graphs.
