"""Benchmarking utilities (skeleton)."""

from __future__ import annotations

from typing import Callable, List, Optional, Tuple


class BenchmarkRunner:
    """Run load tests and calculate performance metrics."""

    def __init__(
        self,
        coordinator_address: Tuple[str, int],
        num_clients: int = 100,
        duration_seconds: float = 10.0,
        logger: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.coordinator_address = coordinator_address
        self.num_clients = num_clients
        self.duration_seconds = duration_seconds
        self.logger = logger
        self.latency_samples_ms: List[float] = []

    def log(self, message: str) -> None:
        """Emit verbose OS-level logs (placeholder)."""
        if self.logger:
            self.logger(message)

    def spawn_virtual_clients(self) -> None:
        """Create and run virtual clients (placeholder)."""
        raise NotImplementedError

    def calculate_throughput(self) -> float:
        """Return throughput in transactions per second (placeholder)."""
        raise NotImplementedError

    def calculate_latency_stats(self) -> Tuple[float, float, float]:
        """Return min/avg/max latency in milliseconds (placeholder)."""
        raise NotImplementedError

    def run_scalability_test(self, server_counts: List[int]) -> None:
        """Run throughput tests with varying server counts (placeholder)."""
        raise NotImplementedError

    def run_fault_test(self, kill_server_id: str) -> None:
        """Kill a server mid-run and record impact (placeholder)."""
        raise NotImplementedError

    def plot_results(self, output_path: str) -> None:
        """Plot benchmark results (placeholder)."""
        raise NotImplementedError
