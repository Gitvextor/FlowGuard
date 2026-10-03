"""Lightweight polling loop for event-triggered FlowGuard context capture."""

from __future__ import annotations

import threading
from collections.abc import Callable

from app.core import ContextSnapshot

from .event_detector import EventDetector
from .windows_context import ForegroundWindowInfo, WindowsContextProvider


SnapshotCallback = Callable[[ContextSnapshot], None]
ErrorCallback = Callable[[Exception], None]


class ContextMonitor:
    """Poll metadata cheaply and capture only after a stable context change."""

    def __init__(
        self,
        provider: WindowsContextProvider,
        detector: EventDetector | None = None,
        *,
        poll_interval_seconds: float = 1.0,
        on_snapshot: SnapshotCallback | None = None,
        on_error: ErrorCallback | None = None,
    ) -> None:
        if poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be positive")
        self.provider = provider
        self.detector = detector or EventDetector()
        self.poll_interval_seconds = float(poll_interval_seconds)
        self.on_snapshot = on_snapshot
        self.on_error = on_error
        self.last_window: ForegroundWindowInfo | None = None
        self.last_triggered = False
        self.last_error: Exception | None = None
        self._task: str | None = None
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def set_task(self, task: str) -> None:
        if not task.strip():
            raise ValueError("task must not be empty")
        self._task = task.strip()

    def poll_once(self, task: str | None = None) -> ContextSnapshot | None:
        """Run one metadata check and possibly return a captured snapshot."""

        if task is not None:
            self.set_task(task)
        if self._task is None:
            raise RuntimeError("Set a task before polling context.")

        self.last_triggered = False
        self.last_error = None
        try:
            info = self.provider.get_foreground_window()
            self.last_window = info
            excluded = info.is_self or not info.available
            self.last_triggered = self.detector.observe(
                info.app_name,
                info.window_title,
                excluded=excluded,
            )
            if not self.last_triggered:
                return None

            snapshot = self.provider.capture(self._task, window_info=info)
        except Exception as exc:
            self.last_error = exc
            if self.last_triggered:
                self.detector.rearm_current()
                self.last_triggered = False
            self._report_error(exc)
            return None

        if self.on_snapshot is not None:
            try:
                self.on_snapshot(snapshot)
            except Exception as exc:
                self.last_error = exc
                self._report_error(exc)
        return snapshot

    def start(self, task: str) -> None:
        """Start a daemon polling thread for one task session."""

        if self.running:
            raise RuntimeError("Context monitor is already running.")
        self.set_task(task)
        self.detector.reset()
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="FlowGuardContextMonitor",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float | None = 5.0) -> None:
        """Stop polling without blocking indefinitely."""

        self._stop_event.set()
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=timeout)
        if thread is None or not thread.is_alive():
            self._thread = None

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self.poll_once()
            self._stop_event.wait(self.poll_interval_seconds)

    def _report_error(self, error: Exception) -> None:
        if self.on_error is None:
            return
        try:
            self.on_error(error)
        except Exception:
            pass
