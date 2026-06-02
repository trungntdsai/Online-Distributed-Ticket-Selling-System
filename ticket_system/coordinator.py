"""Load balancer and health checker (skeleton)."""

from __future__ import annotations

from typing import List, Optional, Tuple


class LoadBalancer:
    """Routes incoming requests to active servers."""

    def __init__(self, active_servers: Optional[List[Tuple[str, int]]] = None) -> None:
        self.active_servers = active_servers or []
        self._round_robin_index = 0

    def route_request(self, request: dict) -> Tuple[str, int]:
        """Select a server for the given request (placeholder)."""
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

    def __init__(self, ping_interval: float = 1.0) -> None:
        self.ping_interval = ping_interval

    def send_heartbeat(self, address: Tuple[str, int]) -> bool:
        """Ping a server node (placeholder)."""
        raise NotImplementedError

    def mark_server_dead(self, address: Tuple[str, int]) -> None:
        """Handle a failed server (placeholder)."""
        raise NotImplementedError
