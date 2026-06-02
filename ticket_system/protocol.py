"""Shared message protocol used by clients, servers, and coordinators."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional


class MessageProtocol:
    """Defines a standardized message format for all nodes."""

    def __init__(self, protocol_version: str = "1.0") -> None:
        self.protocol_version = protocol_version

    def encode_request(self, action: str, payload: Dict[str, Any], request_id: Optional[str] = None) -> str:
        """Encode a request into a JSON string."""
        message = {
            "type": "request",
            "action": action,
            "payload": payload,
            "protocol_version": self.protocol_version,
            "request_id": request_id,
        }
        return json.dumps(message)

    def decode_request(self, raw: str) -> Dict[str, Any]:
        """Decode a JSON request string into a dictionary."""
        return json.loads(raw)

    def build_success_response(self, data: Dict[str, Any], request_id: Optional[str] = None) -> str:
        """Build a success response message."""
        message = {
            "type": "response",
            "status": "ok",
            "data": data,
            "protocol_version": self.protocol_version,
            "request_id": request_id,
        }
        return json.dumps(message)

    def build_error_response(self, code: str, message: str, request_id: Optional[str] = None) -> str:
        """Build an error response message."""
        payload = {
            "type": "response",
            "status": "error",
            "code": code,
            "message": message,
            "protocol_version": self.protocol_version,
            "request_id": request_id,
        }
        return json.dumps(payload)
