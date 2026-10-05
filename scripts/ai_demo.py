"""Offline C-stage demo for the classifier and evidence-based resume anchor."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ai.classifier import ActivityClassifier
from app.ai.resume_anchor import ResumeAnchorGenerator
from app.core import ContextSnapshot


def main() -> int:
    task = "Complete Python assignment"
    cases = [
        ("Scenario 1", "Code.exe", "main.py - FlowGuard"),
        ("Scenario 2", "Microsoft Edge", "Python KeyError - Stack Overflow"),
        ("Scenario 3", "Microsoft Edge", "Funny Videos - Bilibili"),
    ]
    classifier = ActivityClassifier(mock=True)
    history = []
    expected = ("MAIN_TASK", "NECESSARY_DETOUR", "DISTRACTION")

    print("=== FlowGuard AI Acceptance Demo ===")
    for (label, app_name, title), expected_state in zip(cases, expected):
        context = ContextSnapshot(
            timestamp=datetime.now(timezone.utc),
            task=task,
            app_name=app_name,
            window_title=title,
            screenshot=b"",
        )
        result = classifier.classify(context)
        print(f"{label}:")
        print(result.state.value)
        if result.state.value != expected_state:
            print(f"Expected: {expected_state}")
            print("AI ACCEPTANCE TEST: FAIL")
            return 1
        event = classifier.to_history_event(context, result)
        if event is not None:
            history.append(event)

    anchor = ResumeAnchorGenerator().generate(task, history)
    print("Resume Anchor:")
    print(f"last_position: {anchor.last_position}")
    print(f"current_problem: {anchor.current_problem}")
    print(f"next_step: {anchor.next_step}")
    print("generated")
    print("AI ACCEPTANCE TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
