"""Ticket server node (skeleton)."""

from __future__ import annotations

import json
import queue
import socket
import threading
from typing import Any, Callable, Iterable, List, Optional, Tuple

from .inventory import InventoryManager
from .protocol import MessageProtocol, RequestAction


class ThreadPool:
    """Explicit worker pool to demonstrate process/thread management."""

    def __init__(self, max_workers: int, logger: Optional[Callable[[str], None]] = None) -> None:
        self.max_workers = max_workers
        self.logger = logger
        self.task_queue: "queue.Queue[Tuple[Callable[..., Any], Tuple[Any, ...], dict]]" = queue.Queue()
        self.threads: List[threading.Thread] = []
        self._running = False

    def start(self) -> None:
        """Start worker threads."""
        if self._running:
            return
        self._running = True
        for index in range(self.max_workers):
            thread = threading.Thread(
                target=self._worker_loop,
                name=f"Worker-{index + 1}",
                daemon=True,
            )
            self.threads.append(thread)
            thread.start()
        self._log(f"ThreadPool started with {self.max_workers} worker(s).")

    def submit(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Submit a task to the worker pool."""
        if not self._running:
            raise RuntimeError("ThreadPool is not running.")
        self.task_queue.put((func, args, kwargs))

    def shutdown(self, wait: bool = True) -> None:
        """Stop workers and clean up resources."""
        if not self._running:
            return
        self._running = False
        for _ in self.threads:
            self.task_queue.put(None)
        if wait:
            for thread in self.threads:
                thread.join()
        self.threads.clear()
        self._log("ThreadPool shut down.")

    def _worker_loop(self) -> None:
        while True:
            task = self.task_queue.get()
            if task is None:
                self.task_queue.task_done()
                break
            func, args, kwargs = task
            try:
                func(*args, **kwargs)
            finally:
                self.task_queue.task_done()

    def _log(self, message: str) -> None:
        if self.logger:
            self.logger(message)


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
        self._server_socket: Optional[socket.socket] = None
        self._accept_thread: Optional[threading.Thread] = None
        self._running = False
        self._client_timeout_seconds = 5.0

    @property
    def server_address(self) -> Tuple[str, int]:
        if not self._server_socket:
            return (self.host, self.port)
        bound_host, bound_port = self._server_socket.getsockname()[:2]
        return (bound_host, bound_port)

    def log(self, message: str) -> None:
        """Emit verbose OS-level logs (placeholder)."""
        if self.logger:
            self.logger(message)

    def start_listening(self) -> None:
        """Start accepting client connections."""
        if self._running:
            return
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen()
        self._server_socket.settimeout(1.0)
        self._running = True
        self.worker_pool.start()
        self._accept_thread = threading.Thread(
            target=self.accept_connections,
            name=f"Acceptor-{self.server_id}",
            daemon=True,
        )
        self._accept_thread.start()
        bound_host, bound_port = self.server_address
        self.log(f"[{self.server_id}] Listening on {bound_host}:{bound_port}.")

    def accept_connections(self) -> None:
        """Accept sockets and dispatch to workers."""
        if not self._server_socket:
            raise RuntimeError("Server socket is not initialized.")
        while self._running:
            try:
                client_socket, client_address = self._server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            self.log(
                f"[{self.server_id}] Client connection accepted from {client_address}."
            )
            self.dispatch_to_worker(client_socket, client_address)

    def dispatch_to_worker(self, client_socket, client_address) -> None:
        """Dispatch a client socket to a worker thread."""
        try:
            self.worker_pool.submit(self.handle_client_connection, client_socket, client_address)
            self.log(
                f"[{self.server_id}] Dispatched {client_address} to worker thread."
            )
        except RuntimeError:
            client_socket.close()
            self.log(f"[{self.server_id}] Worker pool unavailable; closed socket.")

    def handle_client_connection(self, client_socket, client_address) -> None:
        """Handle a single client connection."""
        client_socket.settimeout(self._client_timeout_seconds)
        with client_socket:
            stream = client_socket.makefile("rwb")
            for raw_line in stream:
                if not raw_line:
                    break
                raw_text = raw_line.decode("utf-8").strip()
                if not raw_text:
                    continue
                response_payload = self._handle_raw_request(raw_text)
                stream.write(response_payload.encode("utf-8") + b"\n")
                stream.flush()
            self.log(f"[{self.server_id}] Connection closed for {client_address}.")

    def sync_with_peers(self) -> None:
        """Sync state with peer nodes (placeholder)."""
        raise NotImplementedError

    def shutdown(self) -> None:
        """Shutdown listener and worker pool."""
        self._running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            finally:
                self._server_socket = None
        if self._accept_thread:
            self._accept_thread.join(timeout=2.0)
            self._accept_thread = None
        self.worker_pool.shutdown(wait=True)
        self.log(f"[{self.server_id}] Server shutdown complete.")

    def _handle_raw_request(self, raw_text: str) -> str:
        request_id = None
        try:
            message = self.protocol.decode_request(raw_text)
            request_id = message.get("request_id")
            return self._handle_request(message)
        except json.JSONDecodeError:
            return self.protocol.build_error_response(
                "INVALID_JSON",
                "Request is not valid JSON.",
                request_id=None,
            )
        except (ValueError, TypeError) as exc:
            return self.protocol.build_error_response(
                "BAD_REQUEST",
                str(exc),
                request_id=request_id,
            )
        except Exception as exc:
            return self.protocol.build_error_response(
                "SERVER_ERROR",
                f"Unhandled error: {exc}",
                request_id=request_id,
            )

    def _handle_request(self, message: dict) -> str:
        action = RequestAction(message["action"])
        payload = message["payload"]
        request_id = message.get("request_id")

        if action == RequestAction.PING:
            return self.protocol.build_success_response(
                {"server_id": self.server_id, "status": "alive"},
                request_id=request_id,
            )

        if action == RequestAction.RESERVE:
            transaction_id = payload["transaction_id"]
            quantity = payload["quantity"]
            reserved = self.inventory.reserve_ticket(transaction_id, quantity)
            if not reserved:
                return self.protocol.build_error_response(
                    "INSUFFICIENT_TICKETS",
                    "Not enough tickets available.",
                    request_id=request_id,
                )
            return self.protocol.build_success_response(
                {
                    "transaction_id": transaction_id,
                    "reserved": quantity,
                    "tickets_remaining": self.inventory.get_available_tickets(),
                },
                request_id=request_id,
            )

        if action == RequestAction.COMMIT:
            transaction_id = payload["transaction_id"]
            self.inventory.commit_purchase(transaction_id)
            return self.protocol.build_success_response(
                {
                    "transaction_id": transaction_id,
                    "tickets_remaining": self.inventory.get_available_tickets(),
                },
                request_id=request_id,
            )

        if action == RequestAction.ROLLBACK:
            transaction_id = payload["transaction_id"]
            self.inventory.rollback_purchase(transaction_id)
            return self.protocol.build_success_response(
                {"transaction_id": transaction_id, "rolled_back": True},
                request_id=request_id,
            )

        if action == RequestAction.BUY:
            transaction_id = payload["transaction_id"]
            quantity = payload["quantity"]
            reserved = self.inventory.reserve_ticket(transaction_id, quantity)
            if not reserved:
                return self.protocol.build_error_response(
                    "INSUFFICIENT_TICKETS",
                    "Not enough tickets available.",
                    request_id=request_id,
                )
            try:
                self.inventory.commit_purchase(transaction_id)
            except Exception as exc:
                self.inventory.rollback_purchase(transaction_id)
                return self.protocol.build_error_response(
                    "COMMIT_FAILED",
                    f"Commit failed: {exc}",
                    request_id=request_id,
                )
            return self.protocol.build_success_response(
                {
                    "transaction_id": transaction_id,
                    "purchased": quantity,
                    "tickets_remaining": self.inventory.get_available_tickets(),
                },
                request_id=request_id,
            )

        return self.protocol.build_error_response(
            "UNKNOWN_ACTION",
            f"Unsupported action: {action.value}",
            request_id=request_id,
        )
