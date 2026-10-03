"""Debounced foreground-context change detection."""

from __future__ import annotations

import time
from collections.abc import Callable


ContextKey = tuple[str, str]


class EventDetector:
    """Emit once after an App/title pair remains stable for the debounce period."""

    def __init__(
        self,
        debounce_seconds: float = 1.5,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if debounce_seconds < 0:
            raise ValueError("debounce_seconds must be non-negative")
        self.debounce_seconds = float(debounce_seconds)
        self._clock = clock
        self._candidate: ContextKey | None = None
        self._candidate_since: float | None = None
        self._committed: ContextKey | None = None

    @property
    def current_context(self) -> ContextKey | None:
        return self._committed

    def observe(
        self,
        app_name: str,
        window_title: str,
        *,
        observed_at: float | None = None,
        excluded: bool = False,
    ) -> bool:
        """Return ``True`` once for each newly stable, non-excluded context."""

        now = self._clock() if observed_at is None else float(observed_at)
        key = self._normalize_key(app_name, window_title)

        if excluded or not any(key):
            self._clear_candidate()
            return False

        if key == self._committed:
            self._clear_candidate()
            return False

        if key != self._candidate:
            self._candidate = key
            self._candidate_since = now
            if self.debounce_seconds == 0:
                return self._commit_candidate()
            return False

        if self._candidate_since is None or now < self._candidate_since:
            self._candidate_since = now
            return False

        if now - self._candidate_since < self.debounce_seconds:
            return False
        return self._commit_candidate()

    def reset(self) -> None:
        """Forget both the pending and last-emitted contexts for a new session."""

        self._committed = None
        self._clear_candidate()

    def rearm_current(self) -> None:
        """Allow a failed capture for the current context to be retried."""

        self.reset()

    def _commit_candidate(self) -> bool:
        self._committed = self._candidate
        self._clear_candidate()
        return True

    def _clear_candidate(self) -> None:
        self._candidate = None
        self._candidate_since = None

    @staticmethod
    def _normalize_key(app_name: str, window_title: str) -> ContextKey:
        normalize = lambda value: " ".join((value or "").split()).casefold()
        return normalize(app_name), normalize(window_title)
