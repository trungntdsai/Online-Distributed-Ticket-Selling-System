"""Comprehensive tester for protocol, inventory, networking, replication, and benchmarking."""

import socket
import time
from typing import Dict, Tuple

from ticket_system.benchmark import BenchmarkRunner
from ticket_system.coordinator import HealthChecker, LoadBalancer
from ticket_system.inventory import InventoryManager
from ticket_system.protocol import MessageProtocol, RequestAction
from ticket_system.server import TicketServer


def _send_request(
    address: Tuple[str, int],
    protocol: MessageProtocol,
    request_json: str,
) -> Dict[str, object]:
    with socket.create_connection(address, timeout=3) as sock:
        sock.sendall(request_json.encode("utf-8") + b"\n")
        response = sock.recv(4096).decode("utf-8").strip()
    return protocol.decode_response(response)


def run_component_tests() -> None:
    """Test protocol schemas and inventory locking."""
    protocol = MessageProtocol()
    request_id = "req-001"
    raw_request = protocol.encode_request(
        RequestAction.RESERVE,
        {"transaction_id": "tx-1", "quantity": 2},
        request_id=request_id,
    )
    decoded_request = protocol.decode_request(raw_request)
    assert decoded_request["action"] == RequestAction.RESERVE.value
    assert decoded_request["request_id"] == request_id

    raw_response = protocol.build_success_response(
        {"tickets_remaining": 8}, request_id=request_id
    )
    decoded_response = protocol.decode_response(raw_response)
    assert decoded_response["status"] == "ok"
    assert decoded_response["request_id"] == request_id

    inventory = InventoryManager(total_tickets=5)
    assert inventory.reserve_ticket("tx-1", 3) is True
    assert inventory.reserve_ticket("tx-2", 3) is False
    inventory.commit_purchase("tx-1")
    assert inventory.total_tickets == 2

    assert inventory.reserve_ticket("tx-3", 2) is True
    inventory.rollback_purchase("tx-3")
    assert inventory.total_tickets == 2

    print("✓ Protocol and InventoryManager tests passed.")


def run_networking_tests() -> None:
    """Test TicketServer networking and LoadBalancer routing."""
    server_inventory = InventoryManager(total_tickets=4)
    server = TicketServer(
        server_id="server-1",
        host="127.0.0.1",
        port=0,
        inventory=server_inventory,
    )
    server.start_listening()
    time.sleep(0.2)
    server_address = server.server_address

    load_balancer = LoadBalancer(active_servers=[server_address])
    assert load_balancer.route_request({}) == server_address

    health_checker = HealthChecker(timeout_seconds=1.0)
    assert health_checker.send_heartbeat(server_address) is True

    protocol = MessageProtocol()
    reserve_request = protocol.encode_request(
        RequestAction.RESERVE,
        {"transaction_id": "tx-100", "quantity": 2},
        request_id="req-100",
    )
    reserve_response = _send_request(server_address, protocol, reserve_request)
    assert reserve_response["status"] == "ok"

    commit_request = protocol.encode_request(
        RequestAction.COMMIT,
        {"transaction_id": "tx-100"},
        request_id="req-101",
    )
    commit_response = _send_request(server_address, protocol, commit_request)
    assert commit_response["status"] == "ok"

    buy_request = protocol.encode_request(
        RequestAction.BUY,
        {"transaction_id": "tx-200", "quantity": 2},
        request_id="req-102",
    )
    buy_response = _send_request(server_address, protocol, buy_request)
    assert buy_response["status"] == "ok"

    server.shutdown()
    print("✓ Networking tests passed.")


def run_replication_tests() -> None:
    """Test leader-follower replication."""
    protocol = MessageProtocol()

    leader_inventory = InventoryManager(total_tickets=10)
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

    follower_inventory = InventoryManager(total_tickets=10)
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

    buy_request = protocol.encode_request(
        RequestAction.BUY,
        {"transaction_id": "tx-300", "quantity": 3},
        request_id="req-300",
    )
    buy_response = _send_request(leader_address, protocol, buy_request)
    assert buy_response["status"] == "ok"

    leader.sync_with_peers()

    log_entries = leader._replication_log.get_entries()
    assert len(log_entries) >= 1

    leader.shutdown()
    follower.shutdown()
    print("✓ Replication tests passed.")


def run_benchmark_quick() -> None:
    """Quick benchmark test with minimal load."""
    server_inventory = InventoryManager(total_tickets=1000)
    server = TicketServer(
        server_id="bench-server",
        host="127.0.0.1",
        port=0,
        inventory=server_inventory,
    )
    server.start_listening()
    time.sleep(0.2)
    server_address = server.server_address

    benchmark = BenchmarkRunner(
        coordinator_address=server_address,
        num_clients=10,
        duration_seconds=2.0,
    )

    benchmark.spawn_virtual_clients()

    throughput = benchmark.calculate_throughput()
    min_lat, avg_lat, max_lat = benchmark.calculate_latency_stats()

    print(
        f"✓ Benchmark results: {throughput:.2f} TPS, "
        f"Latency: {min_lat:.2f}ms (min) / {avg_lat:.2f}ms (avg) / {max_lat:.2f}ms (max)"
    )

    server.shutdown()


if __name__ == "__main__":
    run_component_tests()
    run_networking_tests()
    run_replication_tests()
    run_benchmark_quick()
    print("\n✅ All tests passed!")

