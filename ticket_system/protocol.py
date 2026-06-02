"""Shared message protocol used by clients, servers, and coordinators."""

from __future__ import annotations

import json
from typing import Any, Dict


class MessageProtocol:
    """Defines a standardized message format for all nodes."""

    def encode_request(self, action: str, payload: Dict[str, Any]) -> str:
        """Encode a request into a JSON string."""
        message = {"type": "request", "action": action, "payload": payload}
        return json.dumps(message)

    def decode_request(self, raw: str) -> Dict[str, Any]:
        """Decode a JSON request string into a dictionary."""
        return json.loads(raw)

    def build_success_response(self, data: Dict[str, Any]) -> str:
        """Build a success response message."""
        message = {"type": "response", "status": "ok", "data": data}
        return json.dumps(message)

    def build_error_response(self, code: str, message: str) -> str:
        """Build an error response message."""
        payload = {"type": "response", "status": "error", "code": code, "message": message}
        return json.dumps(payload)
