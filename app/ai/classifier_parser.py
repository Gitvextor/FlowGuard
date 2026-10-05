"""Strict JSON and schema parser for model classification responses."""

from __future__ import annotations

import json
import math
from typing import Any

from app.core import ActivityState, ClassificationResult


class ClassificationParseError(ValueError):
    """Raised when a response is not exactly the required classification schema."""


class ClassificationParser:
    REQUIRED_KEYS = {"state", "confidence", "reason", "task_relation"}

    def parse(self, response: Any) -> ClassificationResult:
        payload = self._extract_payload(response)
        if not isinstance(payload, dict):
            raise ClassificationParseError("Response must be a JSON object.")
        if set(payload) != self.REQUIRED_KEYS:
            missing = sorted(self.REQUIRED_KEYS - set(payload))
            extra = sorted(set(payload) - self.REQUIRED_KEYS)
            detail = []
            if missing:
                detail.append(f"missing fields: {', '.join(missing)}")
            if extra:
                detail.append(f"unexpected fields: {', '.join(extra)}")
            raise ClassificationParseError("Invalid classification schema (" + "; ".join(detail) + ").")

        state_value = payload["state"]
        if not isinstance(state_value, str):
            raise ClassificationParseError("state must be a string.")
        try:
            state = ActivityState(state_value)
        except ValueError as exc:
            raise ClassificationParseError(f"Unsupported state: {state_value!r}.") from exc

        confidence = payload["confidence"]
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise ClassificationParseError("confidence must be a number.")
        if not math.isfinite(float(confidence)):
            raise ClassificationParseError("confidence must be finite.")

        reason = payload["reason"]
        task_relation = payload["task_relation"]
        if not isinstance(reason, str) or not reason.strip():
            raise ClassificationParseError("reason must be a non-empty string.")
        if not isinstance(task_relation, str):
            raise ClassificationParseError("task_relation must be a string.")

        return ClassificationResult(
            state=state,
            confidence=max(0.0, min(1.0, float(confidence))),
            reason=reason.strip(),
            task_relation=task_relation.strip(),
        )

    def _extract_payload(self, response: Any) -> Any:
        """Use raw model text when available so lenient client parsing can't mask errors."""

        if isinstance(response, str):
            return self._loads(response)
        if not isinstance(response, dict):
            raise ClassificationParseError("Response must be JSON text or an object.")
        if response.get("error"):
            raise ClassificationParseError(str(response["error"]))
        raw_response = response.get("raw_response")
        if raw_response is not None:
            if not isinstance(raw_response, str) or not raw_response.strip():
                raise ClassificationParseError("Model response is empty.")
            return self._loads(raw_response)
        if "data" in response:
            data = response["data"]
            if isinstance(data, dict) and set(data) == {"text"}:
                raise ClassificationParseError("Model response was not valid JSON.")
            return data
        return response

    @staticmethod
    def _loads(text: str) -> Any:
        if not text.strip():
            raise ClassificationParseError("Model response is empty.")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ClassificationParseError(f"Model response is not strict JSON: {exc.msg}.") from exc
