"""Ticket server node (skeleton)."""

from __future__ import annotations

import queue
import threading
from typing import Any, Callable, Iterable, List, Optional, Tuple

from .inventory import InventoryManager
from .protocol import MessageProtocol


class ThreadPool:
    """Explicit worker pool to demonstrate process/thread management."""

    def __init__(self, max_workers: int, logger: Optional[Callable[[str], None]] = None) -> None:
        self.max_workers = max_workers
        self.logger = logger
        self.task_queue: "queue.Queue[Tuple[Callable[..., Any], Tuple[Any, ...], dict]]" = queue.Queue()
        self.threads: List[threading.Thread] = []

    def start(self) -> None:
        """Start worker threads (placeholder)."""
        raise NotImplementedError

    def submit(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Submit a task to the worker pool (placeholder)."""
        raise NotImplementedError

    def shutdown(self, wait: bool = True) -> None:
        """Stop workers and clean up resources (placeholder)."""
        raise NotImplementedError


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
        max_workers: int = 8,
        worker_pool: Optional[ThreadPool] = None,
        logger: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.server_id = server_id
        self.host = host
        self.port = port
        self.is_leader = is_leader
        self.peers = list(peers or [])
        self.inventory = inventory or InventoryManager(total_tickets=0)
        self.protocol = protocol or MessageProtocol()
        self.max_workers = max_workers
        self.worker_pool = worker_pool or ThreadPool(max_workers=max_workers, logger=logger)
        self.logger = logger

    def log(self, message: str) -> None:
        """Emit verbose OS-level logs (placeholder)."""
        if self.logger:
            self.logger(message)

    def start_listening(self) -> None:
        """Start accepting client connections (placeholder)."""
        raise NotImplementedError

    def accept_connections(self) -> None:
        """Accept sockets and dispatch to workers (placeholder)."""
        raise NotImplementedError

    def dispatch_to_worker(self, client_socket, client_address) -> None:
        """Dispatch a client socket to a worker thread (placeholder)."""
        raise NotImplementedError

    def handle_client_connection(self, client_socket, client_address) -> None:
        """Handle a single client connection (placeholder)."""
        raise NotImplementedError

    def sync_with_peers(self) -> None:
        """Sync state with peer nodes (placeholder)."""
        raise NotImplementedError

    def shutdown(self) -> None:
        """Shutdown listener and worker pool (placeholder)."""
        raise NotImplementedError
