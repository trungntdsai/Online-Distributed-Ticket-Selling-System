"""Load balancer and health checker (skeleton)."""

from __future__ import annotations

import socket
import threading
import time
from typing import Callable, List, Optional, Tuple

from .protocol import MessageProtocol, RequestAction


class LoadBalancer:
    """Routes incoming requests to active servers."""

    def __init__(
        self,
        active_servers: Optional[List[Tuple[str, int]]] = None,
        logger: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.active_servers = active_servers or []
        self._round_robin_index = 0
        self.logger = logger

    def log(self, message: str) -> None:
        """Emit verbose OS-level logs (placeholder)."""
        if self.logger:
            self.logger(message)

    def route_request(self, request: dict) -> Tuple[str, int]:
        """Select a server for the given request."""
        return self.select_next_server()

    def select_next_server(self) -> Tuple[str, int]:
        """Round-robin server selection."""
        if not self.active_servers:
            raise RuntimeError("No active servers available.")
        address = self.active_servers[self._round_robin_index % len(self.active_servers)]
        self._round_robin_index = (self._round_robin_index + 1) % len(self.active_servers)
        self.log(f"LoadBalancer selected {address}.")
        return address

    def add_server(self, address: Tuple[str, int]) -> None:
        """Add a new active server."""
        if address not in self.active_servers:
            self.active_servers.append(address)

    def remove_server(self, address: Tuple[str, int]) -> None:
        """Remove a server from the active list."""
        if address in self.active_servers:
            self.active_servers.remove(address)


class HealthChecker:
    """Sends heartbeats and tracks server health."""

    def __init__(
        self,
        ping_interval: float = 1.0,
        timeout_seconds: float = 3.0,
        logger: Optional[Callable[[str], None]] = None,
        protocol: Optional[MessageProtocol] = None,
    ) -> None:
        self.ping_interval = ping_interval
        self.timeout_seconds = timeout_seconds
        self.logger = logger
        self.protocol = protocol or MessageProtocol()
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._addresses: List[Tuple[str, int]] = []
        self._dead_servers: List[Tuple[str, int]] = []
        self._lock = threading.Lock()

    def log(self, message: str) -> None:
        """Emit verbose OS-level logs (placeholder)."""
        if self.logger:
            self.logger(message)

    def send_heartbeat(self, address: Tuple[str, int]) -> bool:
        """Ping a server node."""
        try:
            with socket.create_connection(address, timeout=self.timeout_seconds) as sock:
                message = self.protocol.encode_request(RequestAction.PING, {})
                sock.sendall(message.encode("utf-8") + b"\n")
                response = sock.recv(4096).decode("utf-8").strip()
            if not response:
                return False
            decoded = self.protocol.decode_response(response)
            return decoded.get("status") == "ok"
        except (OSError, ValueError, TypeError):
            return False

    def mark_server_dead(self, address: Tuple[str, int]) -> None:
        """Handle a failed server."""
        with self._lock:
            if address not in self._dead_servers:
                self._dead_servers.append(address)
        self.log(f"Marked server {address} as dead.")

    def start_monitoring(self, addresses: List[Tuple[str, int]]) -> None:
        """Start heartbeat monitoring loop."""
        if self._running:
            return
        self._addresses = list(addresses)
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="HealthChecker",
            daemon=True,
        )
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop heartbeat monitoring loop."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
            self._monitor_thread = None

    def _monitor_loop(self) -> None:
        while self._running:
            for address in list(self._addresses):
                alive = self.send_heartbeat(address)
                if not alive:
                    self.mark_server_dead(address)
            time.sleep(self.ping_interval)

    def get_dead_servers(self) -> List[Tuple[str, int]]:
        """Return a snapshot of servers marked as dead."""
        with self._lock:
            return list(self._dead_servers)
