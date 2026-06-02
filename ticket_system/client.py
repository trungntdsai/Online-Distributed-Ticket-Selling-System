"""Client node (skeleton)."""

from __future__ import annotations

from typing import Tuple

from .protocol import MessageProtocol


class Client:
    """Client program that requests tickets."""

    def __init__(self, client_id: str, coordinator_address: Tuple[str, int]) -> None:
        self.client_id = client_id
        self.coordinator_address = coordinator_address
        self.protocol = MessageProtocol()

    def connect_to_system(self) -> None:
        """Connect to the load balancer/coordinator (placeholder)."""
        raise NotImplementedError

    def request_ticket(self, quantity: int) -> None:
        """Submit a ticket request (placeholder)."""
        raise NotImplementedError
