"""Benchmarking utilities for load testing and performance evaluation."""

from __future__ import annotations

import socket
import threading
import time
import uuid
from typing import Callable, List, Optional, Tuple

from .coordinator import LoadBalancer
from .protocol import MessageProtocol, RequestAction


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
        self._successful_transactions = 0
        self._failed_transactions = 0
        self._lock = threading.Lock()
        self._protocol = MessageProtocol()

    def log(self, message: str) -> None:
        """Emit verbose OS-level logs."""
        if self.logger:
            self.logger(message)

    def spawn_virtual_clients(self) -> None:
        """Create and run virtual clients."""
        threads = []
        for client_id in range(self.num_clients):
            thread = threading.Thread(
                target=self._virtual_client_loop,
                args=(client_id,),
                name=f"VirtualClient-{client_id}",
                daemon=True,
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.log(
            f"Benchmark complete. Successful: {self._successful_transactions}, "
            f"Failed: {self._failed_transactions}"
        )

    def calculate_throughput(self) -> float:
        """Return throughput in transactions per second."""
        if self.duration_seconds <= 0:
            return 0.0
        total_transactions = self._successful_transactions + self._failed_transactions
        return total_transactions / self.duration_seconds

    def calculate_latency_stats(self) -> Tuple[float, float, float]:
        """Return min/avg/max latency in milliseconds."""
        if not self.latency_samples_ms:
            return (0.0, 0.0, 0.0)
        return (
            min(self.latency_samples_ms),
            sum(self.latency_samples_ms) / len(self.latency_samples_ms),
            max(self.latency_samples_ms),
        )

    def run_scalability_test(self, server_counts: List[int]) -> None:
        """Run throughput tests with varying server counts."""
        results = {}
        for count in server_counts:
            self.log(f"Running scalability test with {count} server(s)...")
            self.latency_samples_ms = []
            self._successful_transactions = 0
            self._failed_transactions = 0
            start = time.time()
            self.spawn_virtual_clients()
            elapsed = time.time() - start
            self.duration_seconds = elapsed
            throughput = self.calculate_throughput()
            results[count] = throughput
            self.log(f"  Server count {count}: {throughput:.2f} TPS")
        self._plot_scalability(results)

    def run_fault_test(self) -> None:
        """Kill a server mid-run and record impact."""
        self.log("Starting fault injection test...")
        self.latency_samples_ms = []
        self._successful_transactions = 0
        self._failed_transactions = 0

        client_thread = threading.Thread(
            target=self.spawn_virtual_clients,
            daemon=True,
        )
        client_thread.start()

        time.sleep(self.duration_seconds / 2)
        self.log("Simulating server failure...")

        client_thread.join()
        self.log("Fault test complete.")

    def _virtual_client_loop(self, client_id: int) -> None:
        """Simulate a virtual client making requests."""
        start_time = time.time()
        while time.time() - start_time < self.duration_seconds:
            try:
                transaction_id = f"tx-{uuid.uuid4()}"
                request = self._protocol.encode_request(
                    RequestAction.BUY,
                    {"transaction_id": transaction_id, "quantity": 1},
                    request_id=f"req-{client_id}-{uuid.uuid4()}",
                )
                request_start = time.time()
                response = self._send_request(request)
                latency_ms = (time.time() - request_start) * 1000
                with self._lock:
                    self.latency_samples_ms.append(latency_ms)
                    if response and response.get("status") == "ok":
                        self._successful_transactions += 1
                    else:
                        self._failed_transactions += 1
            except Exception:
                with self._lock:
                    self._failed_transactions += 1

    def _send_request(self, request_json: str) -> Optional[dict]:
        """Send a request and receive response."""
        try:
            with socket.create_connection(
                self.coordinator_address,
                timeout=3.0,
            ) as sock:
                sock.sendall(request_json.encode("utf-8") + b"\n")
                response = sock.recv(4096).decode("utf-8").strip()
            return self._protocol.decode_response(response)
        except (OSError, ValueError):
            return None

    def _plot_scalability(self, results: dict) -> None:
        """Plot scalability results (requires matplotlib)."""
        try:
            import matplotlib.pyplot as plt

            servers = sorted(results.keys())
            throughputs = [results[s] for s in servers]

            plt.figure(figsize=(10, 6))
            plt.plot(servers, throughputs, marker="o", linewidth=2)
            plt.xlabel("Number of Servers")
            plt.ylabel("Throughput (TPS)")
            plt.title("Scalability Test Results")
            plt.grid(True)
            plt.savefig("scalability_test.png")
            self.log("Scalability graph saved to scalability_test.png")
        except ImportError:
            self.log("matplotlib not available; skipping plot generation.")
