"""Client node (skeleton)."""

from __future__ import annotations

from typing import Callable, Optional, Tuple

from .protocol import MessageProtocol


class Client:
    """Client program that requests tickets."""

    def __init__(
        self,
        client_id: str,
        coordinator_address: Tuple[str, int],
        logger: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.client_id = client_id
        self.coordinator_address = coordinator_address
        self.protocol = MessageProtocol()
        self.logger = logger

    def log(self, message: str) -> None:
        """Emit verbose OS-level logs (placeholder)."""
        if self.logger:
            self.logger(message)

    def connect_to_system(self) -> None:
        """Connect to the load balancer/coordinator (placeholder)."""
        raise NotImplementedError

    def request_ticket(self, quantity: int, transaction_id: Optional[str] = None) -> None:
        """Submit a ticket request (placeholder)."""
        raise NotImplementedError
