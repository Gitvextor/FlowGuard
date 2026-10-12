"""Windows notification adapter with an independently testable cooldown."""

from __future__ import annotations

import time
from collections.abc import Callable


class NotificationCooldown:
    def __init__(self, seconds: float = 60.0, *, clock: Callable[[], float] = time.monotonic) -> None:
        if seconds < 0:
            raise ValueError("seconds must not be negative")
        self.seconds = float(seconds)
        self.clock = clock
        self._last_sent: float | None = None

    def allow(self) -> bool:
        now = self.clock()
        if self._last_sent is not None and now - self._last_sent < self.seconds:
            return False
        self._last_sent = now
        return True


class WindowsNotifier:
    """Show a native tray notification through Qt when one is available."""

    def __init__(self, tray_icon=None, *, cooldown_seconds: float = 60.0) -> None:
        self.tray_icon = tray_icon
        self.cooldown = NotificationCooldown(cooldown_seconds)

    def notify_distraction(self, task: str) -> bool:
        if self.tray_icon is None or not self.cooldown.allow():
            return False
        self.tray_icon.showMessage(
            "FlowGuard", f'你似乎已经离开当前任务：\n“{task}”',
            self.tray_icon.MessageIcon.Warning, 5000,
        )
        return True
