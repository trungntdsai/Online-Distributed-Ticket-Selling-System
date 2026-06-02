"""Load balancer and health checker (skeleton)."""

from __future__ import annotations

from typing import Callable, List, Optional, Tuple


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
        """Select a server for the given request (placeholder)."""
        raise NotImplementedError

    def select_next_server(self) -> Tuple[str, int]:
        """Round-robin server selection (placeholder)."""
        raise NotImplementedError

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
    ) -> None:
        self.ping_interval = ping_interval
        self.timeout_seconds = timeout_seconds
        self.logger = logger

    def log(self, message: str) -> None:
        """Emit verbose OS-level logs (placeholder)."""
        if self.logger:
            self.logger(message)

    def send_heartbeat(self, address: Tuple[str, int]) -> bool:
        """Ping a server node (placeholder)."""
        raise NotImplementedError

    def mark_server_dead(self, address: Tuple[str, int]) -> None:
        """Handle a failed server (placeholder)."""
        raise NotImplementedError

    def start_monitoring(self, addresses: List[Tuple[str, int]]) -> None:
        """Start heartbeat monitoring loop (placeholder)."""
        raise NotImplementedError

    def stop_monitoring(self) -> None:
        """Stop heartbeat monitoring loop (placeholder)."""
        raise NotImplementedError
