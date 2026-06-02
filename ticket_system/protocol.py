"""Shared message protocol used by clients, servers, and coordinators."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class RequestAction(str, Enum):
    BUY = "BUY"
    RESERVE = "RESERVE"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"
    PING = "PING"
    REPLICATE = "REPLICATE"
    PREPARE = "PREPARE"


class ResponseStatus(str, Enum):
    OK = "ok"
    ERROR = "error"


@dataclass(frozen=True)
class PayloadSchema:
    required: Dict[str, type]
    optional: Dict[str, type]


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


class MessageProtocol:
    """Defines a standardized message format for all nodes."""

    REQUEST_SCHEMAS: Dict[RequestAction, PayloadSchema] = {
        RequestAction.BUY: PayloadSchema(
            required={"transaction_id": str, "quantity": int},
            optional={},
        ),
        RequestAction.RESERVE: PayloadSchema(
            required={"transaction_id": str, "quantity": int},
            optional={},
        ),
        RequestAction.COMMIT: PayloadSchema(
            required={"transaction_id": str},
            optional={},
        ),
        RequestAction.ROLLBACK: PayloadSchema(
            required={"transaction_id": str},
            optional={"reason": str},
        ),
        RequestAction.PING: PayloadSchema(
            required={},
            optional={},
        ),
        RequestAction.REPLICATE: PayloadSchema(
            required={"log_entry": dict},
            optional={},
        ),
        RequestAction.PREPARE: PayloadSchema(
            required={"transaction_id": str, "quantity": int},
            optional={},
        ),
    }

    def __init__(self, protocol_version: str = "1.0", allow_extra_fields: bool = True) -> None:
        self.protocol_version = protocol_version
        self.allow_extra_fields = allow_extra_fields

    def encode_request(
        self,
        action: RequestAction,
        payload: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> str:
        """Encode a request into a JSON string."""
        message = self.build_request(action, payload, request_id=request_id)
        return json.dumps(message)

    def decode_request(self, raw: str) -> Dict[str, Any]:
        """Decode a JSON request string into a dictionary."""
        message = json.loads(raw)
        self.validate_request_message(message)
        return message

    def decode_response(self, raw: str) -> Dict[str, Any]:
        """Decode a JSON response string into a dictionary."""
        message = json.loads(raw)
        self.validate_response_message(message)
        return message

    def build_request(
        self,
        action: RequestAction,
        payload: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build a structured request message."""
        self.validate_payload(action, payload)
        if request_id is not None and not isinstance(request_id, str):
            raise TypeError("request_id must be a string when provided.")
        return {
            "type": "request",
            "action": action.value,
            "payload": payload,
            "protocol_version": self.protocol_version,
            "request_id": request_id,
        }

    def build_success_response(self, data: Dict[str, Any], request_id: Optional[str] = None) -> str:
        """Build a success response message."""
        message = {
            "type": "response",
            "status": ResponseStatus.OK.value,
            "data": data,
            "protocol_version": self.protocol_version,
            "request_id": request_id,
        }
        self.validate_response_message(message)
        return json.dumps(message)

    def build_error_response(self, code: str, message: str, request_id: Optional[str] = None) -> str:
        """Build an error response message."""
        payload = {
            "type": "response",
            "status": ResponseStatus.ERROR.value,
            "code": code,
            "message": message,
            "protocol_version": self.protocol_version,
            "request_id": request_id,
        }
        self.validate_response_message(payload)
        return json.dumps(payload)

    def validate_payload(self, action: RequestAction, payload: Dict[str, Any]) -> None:
        """Validate payload fields and types for a specific action."""
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary.")

        schema = self.REQUEST_SCHEMAS.get(action)
        if not schema:
            raise ValueError(f"Unsupported action: {action}")

        for key, expected_type in schema.required.items():
            if key not in payload:
                raise ValueError(f"Missing required payload field: {key}")
            self._validate_field_type(key, payload[key], expected_type)

        for key, expected_type in schema.optional.items():
            if key in payload:
                self._validate_field_type(key, payload[key], expected_type)

        if not self.allow_extra_fields:
            allowed = set(schema.required.keys()) | set(schema.optional.keys())
            extra = set(payload.keys()) - allowed
            if extra:
                raise ValueError(f"Unexpected payload fields: {sorted(extra)}")

        if "quantity" in payload:
            if not _is_int(payload["quantity"]) or payload["quantity"] <= 0:
                raise ValueError("quantity must be a positive integer.")

    def validate_request_message(self, message: Dict[str, Any]) -> None:
        """Validate a full request message structure."""
        if message.get("type") != "request":
            raise ValueError("Message type must be 'request'.")
        action = message.get("action")
        if not isinstance(action, str):
            raise ValueError("Request action must be a string.")
        try:
            action_enum = RequestAction(action)
        except ValueError as exc:
            raise ValueError(f"Unknown request action: {action}") from exc

        payload = message.get("payload")
        self.validate_payload(action_enum, payload)

        request_id = message.get("request_id")
        if request_id is not None and not isinstance(request_id, str):
            raise TypeError("request_id must be a string when provided.")

        protocol_version = message.get("protocol_version")
        if not isinstance(protocol_version, str):
            raise ValueError("protocol_version must be a string.")

    def validate_response_message(self, message: Dict[str, Any]) -> None:
        """Validate a full response message structure."""
        if message.get("type") != "response":
            raise ValueError("Message type must be 'response'.")

        status = message.get("status")
        if status not in (ResponseStatus.OK.value, ResponseStatus.ERROR.value):
            raise ValueError("Response status must be 'ok' or 'error'.")

        if status == ResponseStatus.OK.value:
            if "data" not in message or not isinstance(message["data"], dict):
                raise ValueError("Success responses must include a data dictionary.")
        else:
            if not isinstance(message.get("code"), str):
                raise ValueError("Error responses must include a string code.")
            if not isinstance(message.get("message"), str):
                raise ValueError("Error responses must include a string message.")

        request_id = message.get("request_id")
        if request_id is not None and not isinstance(request_id, str):
            raise TypeError("request_id must be a string when provided.")

        protocol_version = message.get("protocol_version")
        if not isinstance(protocol_version, str):
            raise ValueError("protocol_version must be a string.")

    def _validate_field_type(self, key: str, value: Any, expected_type: type) -> None:
        if expected_type is int:
            if not _is_int(value):
                raise TypeError(f"Field '{key}' must be an int.")
            return
        if not isinstance(value, expected_type):
            raise TypeError(f"Field '{key}' must be {expected_type.__name__}.")
