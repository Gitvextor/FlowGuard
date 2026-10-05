import unittest
from datetime import datetime, timezone, timedelta

from app.ai.resume_anchor import (
    UNKNOWN_PROBLEM,
    ResumeAnchorGenerator,
    should_generate_resume_anchor,
)
from app.core import ActivityState, HistoryEvent


def event(state, app, title, summary=None, minute=0):
    return HistoryEvent(
        timestamp=datetime(2026, 10, 5, tzinfo=timezone.utc) + timedelta(minutes=minute),
        app_name=app,
        window_title=title,
        state=state,
        summary=summary or f'{app} — "{title}" [{state.value}]',
    )


class ResumeAnchorTests(unittest.TestCase):
    def test_anchor_uses_latest_productive_record_and_does_not_invent_problem(self):
        history = [
            event(ActivityState.MAIN_TASK, "Code.exe", "main.py", minute=1),
            event(ActivityState.NECESSARY_DETOUR, "Edge", "Python KeyError - Stack Overflow", minute=2),
            event(ActivityState.MAIN_TASK, "Code.exe", "scheduler.py", minute=3),
            event(ActivityState.DISTRACTION, "Bilibili", "Funny videos", minute=4),
        ]
        anchor = ResumeAnchorGenerator().generate("Complete Python assignment", history)
        self.assertEqual(anchor.last_position, history[2].summary)
        self.assertEqual(anchor.current_problem, UNKNOWN_PROBLEM)
        self.assertIn("Code.exe", anchor.next_step)
        self.assertIn("scheduler.py", anchor.next_step)
        self.assertIn("Complete Python assignment", anchor.next_step)
        self.assertNotIn("line", anchor.last_position.casefold())

    def test_missing_productive_history_uses_explicit_unknown_and_generic_next_step(self):
        anchor = ResumeAnchorGenerator().generate(
            "Complete Python assignment",
            [event(ActivityState.DISTRACTION, "Bilibili", "Funny videos")],
        )
        self.assertEqual(anchor.last_position, "No recent MAIN_TASK context is recorded.")
        self.assertEqual(anchor.current_problem, UNKNOWN_PROBLEM)
        self.assertIn("Complete Python assignment", anchor.next_step)

    def test_resume_anchor_considers_only_most_recent_five_records(self):
        history = [event(ActivityState.MAIN_TASK, "OldApp", "old.txt", minute=0)] + [
            event(ActivityState.DISTRACTION, "Bilibili", f"video {i}", minute=i + 1)
            for i in range(6)
        ]
        anchor = ResumeAnchorGenerator().generate("Write report", history)
        self.assertEqual(anchor.last_position, "No recent MAIN_TASK context is recorded.")

    def test_one_or_two_consecutive_distractions_confirm_interruption(self):
        productive = event(ActivityState.MAIN_TASK, "Code.exe", "main.py")
        detour = event(ActivityState.NECESSARY_DETOUR, "Edge", "Docs")
        first = event(ActivityState.DISTRACTION, "Bilibili", "Video")
        second = event(ActivityState.DISTRACTION, "Bilibili", "Another video")
        self.assertFalse(should_generate_resume_anchor([productive, first]))
        self.assertTrue(should_generate_resume_anchor([productive, first, second]))
        self.assertTrue(should_generate_resume_anchor([first], consecutive_distractions=1))
        self.assertFalse(should_generate_resume_anchor([first, detour]))

    def test_rejects_zero_or_negative_distraction_threshold(self):
        for value in (0, -1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                should_generate_resume_anchor([], consecutive_distractions=value)


if __name__ == "__main__":
    unittest.main()
