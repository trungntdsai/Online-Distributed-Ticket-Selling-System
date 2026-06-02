"""Simple tester for protocol schemas, inventory locking, and networking."""

import socket
import time
from typing import Dict, Tuple

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

    print("Protocol, InventoryManager, and networking tests passed.")


if __name__ == "__main__":
    run_component_tests()
