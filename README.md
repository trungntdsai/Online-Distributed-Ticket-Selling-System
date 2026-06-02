# Online Ticket Selling System (OS Project)

This repository contains a Python skeleton that matches the required class structure and OS concepts (concurrency, IPC, fault tolerance, and benchmarking). It is intentionally minimal and focuses on interfaces only.

## Refined Architecture (High-Level)
Clients send ticket requests to a LoadBalancer, which routes them to active TicketServer nodes. A leader node owns the source of truth for inventory and replicates state to follower nodes. Two-phase commit (prepare/commit/rollback) ensures ticket deductions only finalize after reservation/payment success. HealthChecker heartbeats detect failures and trigger rerouting to surviving servers.

## OS Concepts Made Explicit
| OS concept | Where it is exposed in this project |
| --- | --- |
| Process/Thread management | `TicketServer` uses an explicit `ThreadPool` to accept sockets and dispatch to worker threads. |
| Synchronization (critical section) | `InventoryManager` uses a mutex with timeout-aware acquisition and explicit release hooks. |
| Inter-Process Communication (IPC) | `MessageProtocol` defines how requests are marshaled/unmarshaled over raw sockets or RPC. |
| Deadlock avoidance & recovery | Lock timeouts and rollback hooks live in `InventoryManager` and server transaction flow. |
| Fault tolerance | `HealthChecker` heartbeats, leader/follower replication, and failover routing. |
| Performance visibility | `BenchmarkRunner` captures throughput/latency vs. server count and thread count. |

## Project Structure
```
ticket_system/
  protocol.py       # MessageProtocol (shared message format)
  inventory.py      # InventoryManager with locking (critical section)
  server.py         # TicketServer (leader/follower, peer sync, thread pool)
  coordinator.py    # LoadBalancer + HealthChecker
  client.py         # Client
  benchmark.py      # BenchmarkRunner
```

## Make OS Mechanics Visible (Deliverables)
1. Verbose console logs that show thread IDs, mutex acquisition/release, and rollback events.
2. Architecture diagram labeling IPC links as TCP sockets and the inventory as a mutex-protected critical section.
3. Benchmark graphs showing throughput vs. number of server threads (to highlight contention).

## Next Steps (Module Breakdown)
| Module | Next step to complete |
| --- | --- |
| `protocol.py` | Finalize message schemas, error codes, and versioning; document required fields for BUY/RESERVE/COMMIT/ROLLBACK. |
| `inventory.py` | Implement lock-protected reserve/commit/rollback, add lock timeouts, and rollback logic for stalled transactions. |
| `server.py` | Implement socket server, explicit thread-pool dispatch, peer sync, leader-follower replication, and 2PC handlers. |
| `coordinator.py` | Implement round-robin routing, heartbeat loop, and server removal/addition on health changes. |
| `client.py` | Implement connection logic and request flow (reserve -> commit/rollback) with request IDs. |
| `benchmark.py` | Implement virtual clients, metrics collection (throughput/latency), plotting, scalability and fault-injection tests. |

## Suggested Build Order
1. Define protocol schemas and request/response types.
2. Implement InventoryManager with correct locking behavior.
3. Implement TicketServer networking and request handling.
4. Add LoadBalancer routing and HealthChecker heartbeats.
5. Add leader-follower replication and two-phase commit.
6. Build BenchmarkRunner and produce scalability/fault-tolerance graphs.
