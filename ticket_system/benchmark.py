"""Benchmarking utilities (skeleton)."""

from __future__ import annotations

from typing import Tuple


class BenchmarkRunner:
    """Run load tests and calculate performance metrics."""

    def __init__(
        self,
        coordinator_address: Tuple[str, int],
        num_clients: int = 100,
        duration_seconds: float = 10.0,
    ) -> None:
        self.coordinator_address = coordinator_address
        self.num_clients = num_clients
        self.duration_seconds = duration_seconds

    def spawn_virtual_clients(self) -> None:
        """Create and run virtual clients (placeholder)."""
        raise NotImplementedError

    def calculate_throughput(self) -> float:
        """Return throughput in transactions per second (placeholder)."""
        raise NotImplementedError

    def plot_results(self, output_path: str) -> None:
        """Plot benchmark results (placeholder)."""
        raise NotImplementedError
