import unittest
from datetime import datetime

from app.context import ContextMonitor, EventDetector, ForegroundWindowInfo
from app.core import ContextSnapshot


class ManualClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class EventDetectorTests(unittest.TestCase):
    def setUp(self):
        self.clock = ManualClock()
        self.detector = EventDetector(1.5, clock=self.clock)

    def observe(self, app="Code.exe", title="scheduler.py"):
        return self.detector.observe(app, title)

    def test_initial_context_triggers_only_after_stable_debounce(self):
        self.assertFalse(self.observe())
        self.clock.now = 1.49
        self.assertFalse(self.observe())
        self.clock.now = 1.5
        self.assertTrue(self.observe())
        self.clock.now = 5.0
        self.assertFalse(self.observe())

    def test_transient_change_does_not_trigger(self):
        self.observe()
        self.clock.now = 0.8
        self.assertFalse(self.observe("msedge.exe", "Search"))
        self.clock.now = 1.0
        self.assertFalse(self.observe("Code.exe", "scheduler.py"))
        self.clock.now = 2.0
        self.assertFalse(self.observe("Code.exe", "scheduler.py"))

    def test_app_or_title_change_can_trigger(self):
        self.observe()
        self.clock.now = 1.5
        self.assertTrue(self.observe())
        self.clock.now = 2.0
        self.assertFalse(self.observe("Code.exe", "tests.py"))
        self.clock.now = 3.5
        self.assertTrue(self.observe("Code.exe", "tests.py"))

    def test_excluded_window_clears_pending_candidate_not_committed_context(self):
        self.observe()
        self.clock.now = 1.5
        self.assertTrue(self.observe())
        self.clock.now = 2.0
        self.assertFalse(self.detector.observe("python.exe", "FlowGuard", excluded=True))
        self.clock.now = 3.0
        self.assertFalse(self.observe())

    def test_whitespace_and_case_do_not_create_duplicate_events(self):
        self.observe("Code.exe", "scheduler.py")
        self.clock.now = 1.5
        self.assertTrue(self.observe(" code.EXE ", " scheduler.py "))
        self.clock.now = 3.0
        self.assertFalse(self.observe("CODE.EXE", "scheduler.py"))

    def test_zero_debounce_triggers_immediately(self):
        detector = EventDetector(0, clock=self.clock)
        self.assertTrue(detector.should_trigger("Code.exe", "scheduler.py"))
        self.assertEqual(detector.last_event, "INITIAL_CONTEXT")
        self.assertFalse(detector.should_trigger("Code.exe", "scheduler.py"))
        self.assertEqual(detector.previous_app, "Code.exe")

    def test_spec_case_1_vscode_to_edge_triggers(self):
        detector = EventDetector(0, clock=self.clock)
        self.assertTrue(detector.should_trigger("Code.exe", "scheduler.py"))
        self.assertTrue(detector.should_trigger("msedge.exe", "Stack Overflow"))

    def test_spec_case_2_same_edge_different_title_triggers(self):
        detector = EventDetector(0, clock=self.clock)
        detector.should_trigger("msedge.exe", "Stack Overflow")
        self.assertTrue(
            detector.should_trigger("msedge.exe", "PyTorch Documentation")
        )

    def test_spec_case_3_same_app_and_title_does_not_trigger(self):
        detector = EventDetector(0, clock=self.clock)
        detector.should_trigger("Code.exe", "scheduler.py")
        self.assertFalse(detector.should_trigger("Code.exe", "scheduler.py"))

    def test_spec_case_4_quick_return_before_debounce_does_not_trigger(self):
        detector = EventDetector(1.5, clock=self.clock)
        detector.should_trigger("Code.exe", "scheduler.py")
        self.clock.now = 0.4
        detector.should_trigger("msedge.exe", "Search")
        self.clock.now = 0.8
        self.assertFalse(detector.should_trigger("Code.exe", "scheduler.py"))


class FakeProvider:
    def __init__(self, info):
        self.info = info
        self.capture_count = 0

    def get_foreground_window(self):
        return self.info

    def capture(self, task, *, window_info=None):
        self.capture_count += 1
        return ContextSnapshot(
            datetime.now().astimezone(),
            task,
            window_info.app_name,
            window_info.window_title,
            b"\xff\xd8demo",
        )


class ContextMonitorTests(unittest.TestCase):
    def test_monitor_captures_only_after_detector_trigger(self):
        clock = ManualClock()
        info = ForegroundWindowInfo(1, 2, "Code.exe", "scheduler.py")
        provider = FakeProvider(info)
        snapshots = []
        monitor = ContextMonitor(
            provider,
            EventDetector(1.5, clock=clock),
            on_snapshot=snapshots.append,
        )

        self.assertIsNone(monitor.poll_once("Finish scheduling lab"))
        self.assertEqual(provider.capture_count, 0)
        clock.now = 1.5
        snapshot = monitor.poll_once()

        self.assertIsNotNone(snapshot)
        self.assertEqual(provider.capture_count, 1)
        self.assertEqual(snapshots, [snapshot])
        clock.now = 5.0
        self.assertIsNone(monitor.poll_once())
        self.assertEqual(provider.capture_count, 1)

    def test_monitor_skips_self_window(self):
        clock = ManualClock()
        info = ForegroundWindowInfo(1, 9, "python.exe", "FlowGuard", is_self=True)
        provider = FakeProvider(info)
        monitor = ContextMonitor(provider, EventDetector(0, clock=clock))

        self.assertIsNone(monitor.poll_once("Finish assignment"))
        self.assertEqual(provider.capture_count, 0)
        self.assertFalse(monitor.last_triggered)


if __name__ == "__main__":
    unittest.main()
