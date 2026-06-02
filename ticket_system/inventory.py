"""Inventory manager with mutual exclusion lock."""

from __future__ import annotations

import threading
from typing import Callable, Dict, Optional


class InventoryManager:
    """Wraps ticket data in a strict mutual exclusion lock."""

    def __init__(
        self,
        total_tickets: int,
        lock_timeout_seconds: float = 5.0,
        logger: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.total_tickets = total_tickets
        self.inventory_lock = threading.Lock()
        self.lock_timeout_seconds = lock_timeout_seconds
        self.logger = logger
        self._pending_reservations: Dict[str, int] = {}

    def log(self, message: str) -> None:
        """Emit verbose OS-level logs (placeholder)."""
        if self.logger:
            self.logger(message)

    def acquire_inventory_lock(self, timeout_seconds: Optional[float] = None) -> bool:
        """Acquire the mutex with a timeout to avoid deadlocks."""
        timeout = self.lock_timeout_seconds if timeout_seconds is None else timeout_seconds
        self.log("Acquiring inventory mutex...")
        acquired = self.inventory_lock.acquire(timeout=timeout)
        if acquired:
            self.log("Inventory mutex acquired.")
        else:
            self.log("Inventory mutex acquisition timed out.")
        return acquired

    def release_inventory_lock(self) -> None:
        """Release the mutex after leaving the critical section."""
        if not self.inventory_lock.locked():
            raise RuntimeError("Inventory lock is not held; cannot release.")
        self.inventory_lock.release()
        self.log("Inventory mutex released.")

    def get_available_tickets(self) -> int:
        """Return available tickets after subtracting pending reservations."""
        if not self.acquire_inventory_lock():
            raise TimeoutError("Timed out acquiring inventory lock.")
        try:
            return self.total_tickets - sum(self._pending_reservations.values())
        finally:
            self.release_inventory_lock()

    def get_pending_reservations(self) -> Dict[str, int]:
        """Return a copy of current pending reservations."""
        if not self.acquire_inventory_lock():
            raise TimeoutError("Timed out acquiring inventory lock.")
        try:
            return dict(self._pending_reservations)
        finally:
            self.release_inventory_lock()

    def reserve_ticket(self, transaction_id: str, quantity: int) -> bool:
        """Reserve tickets in the critical section."""
        if not isinstance(transaction_id, str) or not transaction_id:
            raise ValueError("transaction_id must be a non-empty string.")
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise ValueError("quantity must be a positive integer.")

        if not self.acquire_inventory_lock():
            return False

        try:
            if transaction_id in self._pending_reservations:
                raise ValueError("transaction_id is already reserved.")
            available = self.total_tickets - sum(self._pending_reservations.values())
            if available < quantity:
                return False
            self._pending_reservations[transaction_id] = quantity
            self.log(
                f"Reserved {quantity} ticket(s) for transaction {transaction_id}."
            )
            return True
        finally:
            self.release_inventory_lock()

    def commit_purchase(self, transaction_id: str) -> None:
        """Commit a previously reserved purchase."""
        if not isinstance(transaction_id, str) or not transaction_id:
            raise ValueError("transaction_id must be a non-empty string.")
        if not self.acquire_inventory_lock():
            raise TimeoutError("Timed out acquiring inventory lock.")

        try:
            if transaction_id not in self._pending_reservations:
                raise KeyError("transaction_id not found in pending reservations.")
            quantity = self._pending_reservations.pop(transaction_id)
            if quantity > self.total_tickets:
                raise RuntimeError("Not enough tickets available to commit purchase.")
            self.total_tickets -= quantity
            self.log(
                f"Committed {quantity} ticket(s) for transaction {transaction_id}."
            )
        finally:
            self.release_inventory_lock()

    def rollback_purchase(self, transaction_id: str) -> None:
        """Rollback a failed reservation."""
        if not isinstance(transaction_id, str) or not transaction_id:
            raise ValueError("transaction_id must be a non-empty string.")
        if not self.acquire_inventory_lock():
            raise TimeoutError("Timed out acquiring inventory lock.")

        try:
            if transaction_id not in self._pending_reservations:
                raise KeyError("transaction_id not found in pending reservations.")
            quantity = self._pending_reservations.pop(transaction_id)
            self.log(
                f"Rolled back {quantity} ticket(s) for transaction {transaction_id}."
            )
        finally:
            self.release_inventory_lock()
