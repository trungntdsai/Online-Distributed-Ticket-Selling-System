#!/usr/bin/env python3
"""Quick-start guide for the Distributed Ticket Selling System."""

import sys

GUIDE = """
╔════════════════════════════════════════════════════════════════════════════╗
║          DISTRIBUTED TICKET SELLING SYSTEM - QUICK START GUIDE            ║
╚════════════════════════════════════════════════════════════════════════════╝

📚 PROJECT STRUCTURE
──────────────────────────────────────────────────────────────────────────────
  ticket_system/
    ├── protocol.py        → Message marshaling/validation
    ├── inventory.py       → Mutex-protected critical section
    ├── server.py          → Socket server + thread pool + 2PC
    ├── coordinator.py     → Load balancer + health checker
    ├── client.py          → Client stub (future work)
    └── benchmark.py       → Performance testing

  test_components.py       → Comprehensive test suite (RUN THIS FIRST!)
  demo.py                  → Full system demonstration (5 demos)
  README.md                → Full documentation
  IMPLEMENTATION_SUMMARY.md→ Implementation details & grading checklist


🚀 QUICK START
──────────────────────────────────────────────────────────────────────────────
1. Run tests:
   $ python test_components.py

2. Run demonstrations:
   $ python demo.py

3. Run custom benchmark:
   $ python -c "
from ticket_system.server import TicketServer
from ticket_system.inventory import InventoryManager
from ticket_system.benchmark import BenchmarkRunner

# Create server
srv = TicketServer('test', '127.0.0.1', 0, inventory=InventoryManager(1000))
srv.start_listening()

# Benchmark
b = BenchmarkRunner(srv.server_address, num_clients=50, duration_seconds=3)
b.spawn_virtual_clients()
print(f'Throughput: {b.calculate_throughput():.2f} TPS')
srv.shutdown()
   "


🎯 OS CONCEPTS DEMONSTRATED
──────────────────────────────────────────────────────────────────────────────
1. PROCESS & THREAD MANAGEMENT
   └─ ticket_system/server.py (ThreadPool class)
      • Explicit thread spawning
      • Worker task queue dispatch
      • Graceful shutdown with join()

2. SYNCHRONIZATION (Critical Section)
   └─ ticket_system/inventory.py (InventoryManager class)
      • Mutex lock with timeout
      • Protected critical section (reserve/commit/rollback)
      • Verbose lock acquisition/release logging

3. INTER-PROCESS COMMUNICATION (IPC)
   └─ ticket_system/protocol.py (MessageProtocol class)
      • Low-level TCP sockets (no HTTP framework)
      • Message marshaling/unmarshaling (JSON)
      • Request/response validation

4. DEADLOCK AVOIDANCE & RECOVERY
   └─ ticket_system/server.py + inventory.py
      • Lock timeouts prevent indefinite waiting
      • Stalled transactions automatically rolled back
      • No circular wait → no deadlock

5. FAULT TOLERANCE
   └─ ticket_system/coordinator.py (HealthChecker class)
      • Heartbeat protocol detects failures
      • Dead server tracking
      • Failover routing

6. PERFORMANCE EVALUATION
   └─ ticket_system/benchmark.py (BenchmarkRunner class)
      • Virtual client load generation
      • Throughput metrics (TPS)
      • Latency tracking (min/avg/max)
      • Scalability testing framework


📊 EXAMPLE OUTPUT
──────────────────────────────────────────────────────────────────────────────
Test run:
  ✓ Protocol and InventoryManager tests passed.
  ✓ Networking tests passed.
  ✓ Replication tests passed.
  ✓ Benchmark results: 772.50 TPS
  ✅ All tests passed!

Demo run:
  DEMO 1: Single server BUY transaction
    Response: ok, Tickets remaining: 95

  DEMO 2: Load balancer round-robin
    Request 1 → Server 1
    Request 2 → Server 2
    Request 3 → Server 3
    Request 4 → Server 1 (round-robin)

  DEMO 3: Health checker heartbeats
    Ping 1: Server alive = True
    Ping 2: Server alive = True
    Ping 3: Server alive = True

  DEMO 4: Leader-follower replication
    Leader syncing replication log to followers...
    Replication log has 1 entries: [{'action': 'BUY', ...}]

  DEMO 5: Benchmark (50 virtual clients, 3 seconds)
    Throughput: 906.67 TPS
    Latency: 0.71ms (min) / 55.42ms (avg) / 119.26ms (max)


🔍 KEY FILES TO REVIEW
──────────────────────────────────────────────────────────────────────────────
For OS Concepts:
  1. ticket_system/server.py (ThreadPool + TicketServer)
     Lines: Thread lifecycle, task dispatch, accept/dispatch pattern

  2. ticket_system/inventory.py (InventoryManager)
     Lines: Lock acquisition with timeout, critical section, rollback

  3. ticket_system/protocol.py (MessageProtocol)
     Lines: Message validation, marshaling/unmarshaling

  4. ticket_system/coordinator.py (HealthChecker)
     Lines: Heartbeat loop, server health tracking

For Testing:
  1. test_components.py
     - run_component_tests() → Protocol + inventory
     - run_networking_tests() → Server + load balancer
     - run_replication_tests() → Replication log + followers
     - run_benchmark_quick() → Throughput/latency

For Demonstration:
  1. demo.py
     - demo_basic_transaction() → Single-step BUY
     - demo_load_balancer() → Round-robin routing
     - demo_heartbeat() → PING protocol
     - demo_replication() → Leader sync
     - demo_benchmark() → Load testing


💡 COMMON TASKS
──────────────────────────────────────────────────────────────────────────────
Start a single server:
  from ticket_system.server import TicketServer
  from ticket_system.inventory import InventoryManager
  
  server = TicketServer("myserver", "127.0.0.1", 9000)
  server.start_listening()
  # ... make requests ...
  server.shutdown()

Send a BUY request:
  from ticket_system.protocol import MessageProtocol, RequestAction
  import socket
  
  protocol = MessageProtocol()
  request = protocol.encode_request(
      RequestAction.BUY,
      {"transaction_id": "tx-1", "quantity": 5},
      request_id="req-1",
  )
  with socket.create_connection(("127.0.0.1", 9000)) as sock:
      sock.send(request.encode() + b"\\n")
      response = sock.recv(4096).decode()
  print(protocol.decode_response(response))

Set up load balancer:
  from ticket_system.coordinator import LoadBalancer, HealthChecker
  
  servers = [("127.0.0.1", 9000), ("127.0.0.1", 9001)]
  lb = LoadBalancer(active_servers=servers)
  hc = HealthChecker(ping_interval=1.0)
  
  next_server = lb.route_request({})
  is_alive = hc.send_heartbeat(next_server)

Run benchmark:
  from ticket_system.benchmark import BenchmarkRunner
  
  bench = BenchmarkRunner(
      coordinator_address=("127.0.0.1", 9000),
      num_clients=100,
      duration_seconds=10.0,
  )
  bench.spawn_virtual_clients()
  print(f"TPS: {bench.calculate_throughput():.2f}")
  print(f"Latency: {bench.calculate_latency_stats()}")


🔧 TROUBLESHOOTING
──────────────────────────────────────────────────────────────────────────────
Port already in use:
  → Use port 0 in constructor: TicketServer(..., port=0)
    Server will bind to a random available port

Lock timeout exceeded:
  → Increase timeout_seconds in InventoryManager or server.acquire_inventory_lock()
  → Check for deadlocks in custom code

Connection refused:
  → Make sure server is listening: server.start_listening()
  → Check server address: server.server_address

Benchmark low throughput:
  → Increase num_clients or duration_seconds
  → Check lock contention (average latency will be high)


📖 DOCUMENTATION HIERARCHY
──────────────────────────────────────────────────────────────────────────────
1. README.md                  ← Architecture overview, OS concepts, implementation status
2. IMPLEMENTATION_SUMMARY.md  ← Detailed implementation, design decisions, grading checklist
3. This file                  ← Quick start, common tasks, troubleshooting
4. Code docstrings            ← Method signatures, parameters, return values


✅ WHAT THIS PROJECT DEMONSTRATES
──────────────────────────────────────────────────────────────────────────────
✓ Process/thread management    (ThreadPool)
✓ Mutual exclusion             (Mutex with timeouts)
✓ Critical section protection  (InventoryManager)
✓ Inter-process communication  (TCP sockets + protocol)
✓ Message marshaling           (JSON encoding/decoding)
✓ Deadlock avoidance           (Lock timeouts)
✓ Fault tolerance              (Heartbeats + replication)
✓ Load balancing               (Round-robin scheduling)
✓ Two-phase commit             (Prepare/commit/rollback)
✓ Performance evaluation       (Benchmark + metrics)
✓ Concurrency bugs             (Race conditions solved with locks)
✓ Distributed systems          (Leader-follower replication)


🎓 LEARNING OBJECTIVES MET
──────────────────────────────────────────────────────────────────────────────
After studying this project, you understand:
  1. How locks prevent race conditions
  2. How thread pools manage worker threads
  3. How to marshal messages for IPC
  4. How timeouts prevent deadlocks
  5. How heartbeats detect failures
  6. How two-phase commit ensures consistency
  7. How replication improves fault tolerance
  8. How load balancing distributes traffic
  9. How to measure performance (throughput/latency)
  10. How distributed systems handle failures


════════════════════════════════════════════════════════════════════════════════
                            Happy coding! 🚀
════════════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(GUIDE)
