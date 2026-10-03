import unittest
from unittest.mock import Mock, patch

from app.context.windows_context import (
    SelfWindowExcludedError,
    WindowsContextProvider,
)
from app.core import ContextSnapshot


class WindowsContextProviderTests(unittest.TestCase):
    def setUp(self):
        self.screenshot = Mock()
        self.screenshot.capture_primary_screen.return_value = b"\xff\xd8demo"

    def _provider(self, own_pid=999):
        return WindowsContextProvider(self.screenshot, own_pid=own_pid)

    @patch("app.context.windows_context.psutil")
    @patch("app.context.windows_context.win32process")
    @patch("app.context.windows_context.win32gui")
    def test_reads_foreground_app_title_and_process(self, gui, process, psutil):
        gui.GetForegroundWindow.return_value = 101
        gui.GetWindowText.return_value = "scheduler.py - Visual Studio Code"
        process.GetWindowThreadProcessId.return_value = (7, 202)
        psutil.Process.return_value.name.return_value = "Code.exe"

        info = self._provider().get_foreground_window()

        self.assertTrue(info.available)
        self.assertEqual(info.hwnd, 101)
        self.assertEqual(info.pid, 202)
        self.assertEqual(info.app_name, "Code.exe")
        self.assertEqual(info.window_title, "scheduler.py - Visual Studio Code")
        self.assertFalse(info.is_self)

    @patch("app.context.windows_context.psutil")
    @patch("app.context.windows_context.win32process")
    @patch("app.context.windows_context.win32gui")
    def test_only_exact_pid_is_self_not_every_python_process(self, gui, process, psutil):
        gui.GetForegroundWindow.return_value = 55
        gui.GetWindowText.return_value = "student_script.py"
        process.GetWindowThreadProcessId.return_value = (1, 444)
        psutil.Process.return_value.name.return_value = "python.exe"

        info = self._provider(own_pid=999).get_foreground_window()

        self.assertEqual(info.app_name, "python.exe")
        self.assertFalse(info.is_self)

    @patch("app.context.windows_context.psutil")
    @patch("app.context.windows_context.win32process")
    @patch("app.context.windows_context.win32gui")
    def test_own_pid_is_excluded_and_never_screenshotted(self, gui, process, psutil):
        gui.GetForegroundWindow.return_value = 66
        gui.GetWindowText.return_value = "FlowGuard"
        process.GetWindowThreadProcessId.return_value = (1, 999)
        psutil.Process.return_value.name.return_value = "python.exe"
        provider = self._provider(own_pid=999)
        info = provider.get_foreground_window()

        self.assertTrue(info.is_self)
        with self.assertRaises(SelfWindowExcludedError):
            provider.capture("Finish assignment", window_info=info)
        self.screenshot.capture_primary_screen.assert_not_called()

    @patch("app.context.windows_context.win32gui")
    def test_missing_foreground_window_is_safe(self, gui):
        gui.GetForegroundWindow.return_value = 0

        info = self._provider().get_foreground_window()

        self.assertFalse(info.available)
        self.assertEqual(info.app_name, "Unknown")
        self.assertEqual(info.window_title, "")

    @patch("app.context.windows_context.win32gui")
    def test_win32_error_is_returned_as_data(self, gui):
        gui.GetForegroundWindow.side_effect = RuntimeError("desktop unavailable")

        info = self._provider().get_foreground_window()

        self.assertFalse(info.available)
        self.assertIn("desktop unavailable", info.error)

    def test_capture_uses_shared_model_and_existing_screenshot_provider(self):
        provider = self._provider()
        info = Mock(
            is_self=False,
            app_name="msedge.exe",
            window_title="Priority scheduling - Search",
        )

        snapshot = provider.capture("Finish scheduling lab", window_info=info)

        self.assertIsInstance(snapshot, ContextSnapshot)
        self.assertEqual(snapshot.app_name, "msedge.exe")
        self.assertEqual(snapshot.screenshot, b"\xff\xd8demo")
        self.screenshot.capture_primary_screen.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
