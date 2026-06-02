"""Ticket server node (skeleton)."""

from __future__ import annotations

from typing import Iterable, Optional, Tuple

from .inventory import InventoryManager
from .protocol import MessageProtocol


class TicketServer:
    """Server process that handles client requests and syncs with peers."""

    def __init__(
        self,
        server_id: str,
        host: str,
        port: int,
        is_leader: bool = False,
        peers: Optional[Iterable[Tuple[str, int]]] = None,
        inventory: Optional[InventoryManager] = None,
        protocol: Optional[MessageProtocol] = None,
    ) -> None:
        self.server_id = server_id
        self.host = host
        self.port = port
        self.is_leader = is_leader
        self.peers = list(peers or [])
        self.inventory = inventory or InventoryManager(total_tickets=0)
        self.protocol = protocol or MessageProtocol()

    def start_listening(self) -> None:
        """Start accepting client connections (placeholder)."""
        raise NotImplementedError

    def handle_client_connection(self, client_socket, client_address) -> None:
        """Handle a single client connection (placeholder)."""
        raise NotImplementedError

    def sync_with_peers(self) -> None:
        """Sync state with peer nodes (placeholder)."""
        raise NotImplementedError
