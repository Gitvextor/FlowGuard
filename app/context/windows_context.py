"""Windows foreground-window metadata and in-memory context capture.

The separation between :meth:`get_foreground_window` and :meth:`capture`
lets the monitor poll cheap metadata and defer screenshots until a stable
context change has been confirmed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from app.capture import ScreenshotProvider
from app.core import ContextProvider, ContextSnapshot

try:  # Import-safe on non-Windows CI; use is rejected when dependencies are absent.
    import psutil
except ImportError:  # pragma: no cover - exercised on non-Windows environments.
    psutil = None

try:
    import win32gui
    import win32process
except ImportError:  # pragma: no cover - exercised on non-Windows environments.
    win32gui = None
    win32process = None


UNKNOWN_APP = "Unknown"
UNKNOWN_WINDOW = "Unknown Window"


def get_foreground_window_handle() -> int | None:
    """Return the foreground HWND, or ``None`` when Windows cannot provide one."""

    if win32gui is None:
        return None
    try:
        hwnd = int(win32gui.GetForegroundWindow())
        return hwnd or None
    except Exception:
        return None


def get_window_title(hwnd: int | None) -> str:
    """Return a safe title fallback for a native window handle."""

    if not hwnd or win32gui is None:
        return UNKNOWN_WINDOW
    try:
        return (win32gui.GetWindowText(hwnd) or "").strip() or UNKNOWN_WINDOW
    except Exception:
        return UNKNOWN_WINDOW


def get_window_process_id(hwnd: int | None) -> int | None:
    """Return the process ID owning ``hwnd`` without leaking Win32 errors."""

    if not hwnd or win32process is None:
        return None
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return int(pid) if pid else None
    except Exception:
        return None


def get_process_name(pid: int | None) -> str:
    """Resolve an exact PID to its executable name with a stable fallback."""

    if not pid or psutil is None:
        return UNKNOWN_APP
    try:
        return (psutil.Process(pid).name() or "").strip() or UNKNOWN_APP
    except Exception:
        return UNKNOWN_APP


@dataclass(frozen=True)
class ForegroundWindowInfo:
    """Lightweight identity for one foreground-window observation."""

    hwnd: int | None
    pid: int | None
    app_name: str
    window_title: str
    is_self: bool = False
    error: str | None = None

    @property
    def available(self) -> bool:
        has_identity = bool(
            self.window_title or (self.app_name and self.app_name != UNKNOWN_APP)
        )
        return self.hwnd is not None and has_identity

    @property
    def context_key(self) -> tuple[str, str]:
        return self.app_name, self.window_title


class SelfWindowExcludedError(RuntimeError):
    """Raised when a direct capture targets a FlowGuard-owned window."""


class WindowsContextProvider(ContextProvider):
    """Collect foreground Windows context using Win32 and ``psutil``.

    Self-window detection compares the exact process ID, registered HWNDs, and
    exact registered titles. It deliberately does not exclude all Python
    processes because another ``python.exe`` may be the user's active work.
    """

    def __init__(
        self,
        screenshot_provider: ScreenshotProvider | None = None,
        *,
        own_pid: int | None = None,
        own_window_handles: Iterable[int] = (),
        own_window_titles: Iterable[str] = (),
    ) -> None:
        self.screenshot_provider = screenshot_provider or ScreenshotProvider()
        self.own_pid = os.getpid() if own_pid is None else own_pid
        self._own_window_handles = {int(handle) for handle in own_window_handles}
        self._own_window_titles = {
            self._normalize_title(title) for title in own_window_titles if title.strip()
        }

    def register_own_window(self, hwnd: int, title: str | None = None) -> None:
        """Register a FlowGuard UI window after its native HWND is available."""

        self._own_window_handles.add(int(hwnd))
        if title and title.strip():
            self._own_window_titles.add(self._normalize_title(title))

    def unregister_own_window(self, hwnd: int) -> None:
        self._own_window_handles.discard(int(hwnd))

    def get_foreground_window(self) -> ForegroundWindowInfo:
        """Return foreground metadata without taking a screenshot.

        Empty titles, missing foreground windows, inaccessible processes, and
        Win32 errors are represented as data so the polling loop stays alive.
        """

        dependency_error = self._dependency_error()
        if dependency_error:
            return ForegroundWindowInfo(
                hwnd=None,
                pid=None,
                app_name=UNKNOWN_APP,
                window_title="",
                error=dependency_error,
            )

        try:
            hwnd = int(win32gui.GetForegroundWindow())
            if not hwnd:
                return ForegroundWindowInfo(
                    hwnd=None,
                    pid=None,
                    app_name=UNKNOWN_APP,
                    window_title="",
                )

            title = get_window_title(hwnd)
            pid = get_window_process_id(hwnd)
            app_name, process_error = self._process_name(pid)
            is_self = self._is_self_window(hwnd, pid, title)
            return ForegroundWindowInfo(
                hwnd=hwnd,
                pid=pid,
                app_name=app_name,
                window_title=title,
                is_self=is_self,
                error=process_error,
            )
        except Exception as exc:
            return ForegroundWindowInfo(
                hwnd=None,
                pid=None,
                app_name=UNKNOWN_APP,
                window_title="",
                error=f"{type(exc).__name__}: {exc}",
            )

    def capture(
        self,
        task: str,
        *,
        window_info: ForegroundWindowInfo | None = None,
    ) -> ContextSnapshot:
        """Return the shared snapshot model with screenshot bytes kept in memory."""

        info = window_info or self.get_foreground_window()
        if info.is_self:
            raise SelfWindowExcludedError(
                "FlowGuard's own window is excluded from context capture."
            )

        screenshot = self.screenshot_provider.capture_primary_screen()
        return ContextSnapshot(
            timestamp=datetime.now().astimezone(),
            task=task,
            app_name=info.app_name or UNKNOWN_APP,
            window_title=info.window_title,
            screenshot=screenshot,
        )

    def _process_name(self, pid: int | None) -> tuple[str, str | None]:
        if not pid:
            return UNKNOWN_APP, None
        try:
            return get_process_name(pid), None
        except Exception as exc:
            return UNKNOWN_APP, f"{type(exc).__name__}: {exc}"

    def _is_self_window(self, hwnd: int, pid: int | None, title: str) -> bool:
        if pid is not None and pid == self.own_pid:
            return True
        if hwnd in self._own_window_handles:
            return True
        normalized_title = self._normalize_title(title)
        return bool(normalized_title and normalized_title in self._own_window_titles)

    @staticmethod
    def _normalize_title(title: str) -> str:
        return " ".join(title.split()).casefold()

    @staticmethod
    def _dependency_error() -> str | None:
        missing = []
        if win32gui is None or win32process is None:
            missing.append("pywin32")
        if psutil is None:
            missing.append("psutil")
        if not missing:
            return None
        return f"Missing Windows context dependencies: {', '.join(missing)}"
