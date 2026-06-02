"""Demonstration of the distributed ticket selling system."""

import time

from ticket_system.benchmark import BenchmarkRunner
from ticket_system.coordinator import HealthChecker, LoadBalancer
from ticket_system.inventory import InventoryManager
from ticket_system.protocol import MessageProtocol, RequestAction
from ticket_system.server import TicketServer


def demo_basic_transaction():
    """Demonstrate a basic ticket purchase transaction."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Transaction (Single Server)")
    print("=" * 60)

    protocol = MessageProtocol()

    inventory = InventoryManager(total_tickets=100)
    server = TicketServer(
        server_id="demo-server-1",
        host="127.0.0.1",
        port=0,
        inventory=inventory,
    )
    server.start_listening()
    time.sleep(0.2)
    server_address = server.server_address
    print(f"Server started at {server_address}")

    buy_request = protocol.encode_request(
        RequestAction.BUY,
        {"transaction_id": "demo-tx-1", "quantity": 5},
        request_id="demo-req-1",
    )
    print(f"\nSending request: BUY 5 tickets")

    import socket

    with socket.create_connection(server_address, timeout=3) as sock:
        sock.sendall(buy_request.encode("utf-8") + b"\n")
        response = sock.recv(4096).decode("utf-8").strip()
    
    response_obj = protocol.decode_response(response)
    print(f"Response: {response_obj['status']}")
    print(f"Tickets remaining: {response_obj['data']['tickets_remaining']}")

    server.shutdown()
    print("Server shutdown.\n")


def demo_load_balancer():
    """Demonstrate load balancing across multiple servers."""
    print("\n" + "=" * 60)
    print("DEMO 2: Load Balancer (Round-Robin)")
    print("=" * 60)

    servers = []
    addresses = []

    for i in range(3):
        inventory = InventoryManager(total_tickets=100)
        server = TicketServer(
            server_id=f"lb-server-{i+1}",
            host="127.0.0.1",
            port=0,
            inventory=inventory,
        )
        server.start_listening()
        time.sleep(0.1)
        servers.append(server)
        addresses.append(server.server_address)
        print(f"Server {i+1} started at {server.server_address}")

    load_balancer = LoadBalancer(active_servers=addresses)
    print("\nLoad Balancer active servers:", addresses)

    for req_num in range(5):
        selected = load_balancer.route_request({})
        print(f"Request {req_num+1}: Routed to {selected}")

    for server in servers:
        server.shutdown()
    print("Servers shutdown.\n")


def demo_heartbeat():
    """Demonstrate health checking."""
    print("\n" + "=" * 60)
    print("DEMO 3: Health Checker (Heartbeats)")
    print("=" * 60)

    inventory = InventoryManager(total_tickets=100)
    server = TicketServer(
        server_id="health-server",
        host="127.0.0.1",
        port=0,
        inventory=inventory,
    )
    server.start_listening()
    time.sleep(0.2)
    server_address = server.server_address
    print(f"Server started at {server_address}")

    health_checker = HealthChecker(ping_interval=0.5, timeout_seconds=2.0)
    print("HealthChecker probing...")

    for i in range(3):
        alive = health_checker.send_heartbeat(server_address)
        print(f"Ping {i+1}: Server alive = {alive}")
        time.sleep(0.5)

    server.shutdown()
    print("Server shutdown.\n")


def demo_replication():
    """Demonstrate leader-follower replication."""
    print("\n" + "=" * 60)
    print("DEMO 4: Leader-Follower Replication")
    print("=" * 60)

    protocol = MessageProtocol()

    leader_inventory = InventoryManager(total_tickets=100)
    leader = TicketServer(
        server_id="leader",
        host="127.0.0.1",
        port=0,
        is_leader=True,
        inventory=leader_inventory,
    )
    leader.start_listening()
    time.sleep(0.2)
    leader_address = leader.server_address
    print(f"Leader started at {leader_address}")

    follower_inventory = InventoryManager(total_tickets=100)
    follower = TicketServer(
        server_id="follower",
        host="127.0.0.1",
        port=0,
        is_leader=False,
        peers=[leader_address],
        inventory=follower_inventory,
    )
    follower.start_listening()
    time.sleep(0.2)
    print(f"Follower started at {follower.server_address}")

    import socket

    buy_request = protocol.encode_request(
        RequestAction.BUY,
        {"transaction_id": "rep-tx-1", "quantity": 10},
        request_id="rep-req-1",
    )
    print("\nLeader processes BUY request...")
    with socket.create_connection(leader_address, timeout=3) as sock:
        sock.sendall(buy_request.encode("utf-8") + b"\n")
        response = sock.recv(4096).decode("utf-8").strip()
    
    response_obj = protocol.decode_response(response)
    print(f"Leader response: {response_obj['status']}")

    leader.sync_with_peers()
    print("Leader syncing replication log to followers...")

    log_entries = leader._replication_log.get_entries()
    print(f"Replication log has {len(log_entries)} entries:")
    for entry in log_entries:
        print(f"  - {entry}")

    leader.shutdown()
    follower.shutdown()
    print("Servers shutdown.\n")


def demo_benchmark():
    """Demonstrate benchmarking."""
    print("\n" + "=" * 60)
    print("DEMO 5: Performance Benchmarking")
    print("=" * 60)

    inventory = InventoryManager(total_tickets=10000)
    server = TicketServer(
        server_id="bench-server",
        host="127.0.0.1",
        port=0,
        inventory=inventory,
    )
    server.start_listening()
    time.sleep(0.2)
    server_address = server.server_address
    print(f"Server started at {server_address}")

    print("\nRunning benchmark with 50 virtual clients for 3 seconds...")
    benchmark = BenchmarkRunner(
        coordinator_address=server_address,
        num_clients=50,
        duration_seconds=3.0,
    )
    benchmark.spawn_virtual_clients()

    throughput = benchmark.calculate_throughput()
    min_lat, avg_lat, max_lat = benchmark.calculate_latency_stats()
    success = benchmark._successful_transactions
    failed = benchmark._failed_transactions

    print(f"\nBenchmark Results:")
    print(f"  Throughput: {throughput:.2f} transactions/second")
    print(f"  Successful: {success}, Failed: {failed}")
    print(f"  Latency (min/avg/max): {min_lat:.2f}ms / {avg_lat:.2f}ms / {max_lat:.2f}ms")

    server.shutdown()
    print("Server shutdown.\n")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "DISTRIBUTED TICKET SELLING SYSTEM DEMO" + " " * 10 + "║")
    print("╚" + "═" * 58 + "╝")

    demo_basic_transaction()
    demo_load_balancer()
    demo_heartbeat()
    demo_replication()
    demo_benchmark()

    print("=" * 60)
    print("All demos completed!")
    print("=" * 60 + "\n")
