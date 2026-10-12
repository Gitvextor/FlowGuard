import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from app.ai.classifier import ActivityClassifier
from app.controller.controller import IntegratedController
from app.core import ActivityState, ClassificationResult, ContextSnapshot
from app.notifications import NotificationCooldown
from app.storage import SessionStore


class FakeMonitor:
    def start(self, task): pass
    def stop(self, timeout=5.0): pass


class FakeNotifier:
    def __init__(self): self.tasks = []
    def notify_distraction(self, task): self.tasks.append(task); return True


class SequenceClassifier(ActivityClassifier):
    def __init__(self, results): super().__init__(mock=True); self.results = iter(results)
    def classify(self, context): self.last_error = None; return next(self.results)


def result(state, confidence=0.9):
    return ClassificationResult(state, confidence, "test reason", "test relation")


class DStageIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)

    def snapshot(self, title="Bilibili entertainment"):
        return ContextSnapshot(datetime.now().astimezone(), "Finish lab", "browser.exe", title, b"memory only")

    def controller(self, results, notifier=None, callback=None):
        controller = IntegratedController(classifier=SequenceClassifier(results),
            store=SessionStore(Path(self.temp.name)), notifier=notifier, on_result=callback)
        controller.monitor = FakeMonitor(); return controller

    def test_two_distractions_persist_and_generate_grounded_anchor(self):
        received, notifier = [], FakeNotifier()
        controller = self.controller([result(ActivityState.DISTRACTION), result(ActivityState.DISTRACTION)], notifier, lambda *x: received.append(x))
        controller.start("Finish lab"); generation = controller._generation
        controller._process_snapshot(self.snapshot(), generation)
        controller._process_snapshot(self.snapshot("YouTube entertainment"), generation)
        self.assertEqual(2, len(controller.store.get_recent_events(10)))
        self.assertIsNotNone(received[-1][3]); self.assertEqual(["Finish lab", "Finish lab"], notifier.tasks)
        controller.shutdown()

    def test_zero_confidence_is_not_persisted_or_notified(self):
        notifier = FakeNotifier(); controller = self.controller([result(ActivityState.MAIN_TASK, 0.0)], notifier)
        controller.start("Finish lab"); controller._process_snapshot(self.snapshot(), controller._generation)
        self.assertEqual([], controller.store.get_recent_events()); self.assertEqual([], notifier.tasks)
        controller.shutdown()

    def test_pause_invalidates_late_background_result(self):
        controller = self.controller([result(ActivityState.DISTRACTION)])
        controller.start("Finish lab"); old_generation = controller._generation; controller.pause()
        controller._process_snapshot(self.snapshot(), old_generation); self.assertFalse(controller.running)

    def test_notification_cooldown_is_sixty_second_capable(self):
        now = [100.0]; cooldown = NotificationCooldown(60.0, clock=lambda: now[0])
        self.assertTrue(cooldown.allow()); now[0] += 59; self.assertFalse(cooldown.allow())
        now[0] += 1; self.assertTrue(cooldown.allow())


if __name__ == "__main__": unittest.main()
