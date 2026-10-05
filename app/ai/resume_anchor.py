"""Evidence-bounded interruption detection and Resume Anchor generation."""

from __future__ import annotations

from app.core import ActivityState, HistoryEvent, ResumeAnchor


UNKNOWN_POSITION = "No recent MAIN_TASK context is recorded."
UNKNOWN_PROBLEM = "The exact unresolved issue is unclear from recent context."


def should_generate_resume_anchor(
    history: list[HistoryEvent],
    *,
    consecutive_distractions: int = 2,
) -> bool:
    """Return true for one/two simple, consecutive distraction observations."""

    if consecutive_distractions < 1:
        raise ValueError("consecutive_distractions must be at least 1")
    if len(history) < consecutive_distractions:
        return False
    return all(
        event.state is ActivityState.DISTRACTION
        for event in history[-consecutive_distractions:]
    )


class ResumeAnchorGenerator:
    """Generate a deterministic anchor from recorded history only.

    The shared A-stage LLM client is vision-only and the stable generator protocol
    receives no screenshot. Avoid inventing or substituting an image for this task;
    these short anchors can be safely derived from the recorded evidence directly.
    """

    def generate(self, task: str, history: list[HistoryEvent]) -> ResumeAnchor:
        safe_history = list(history[-5:])
        return self._grounded_anchor(task, safe_history)

    @staticmethod
    def _grounded_anchor(task: str, history: list[HistoryEvent]) -> ResumeAnchor:
        declared_task = " ".join(task.split()) or "the declared task"
        productive = next(
            (event for event in reversed(history) if event.state is ActivityState.MAIN_TASK),
            None,
        )
        if productive is None:
            last_position = UNKNOWN_POSITION
            next_step = f"Review {declared_task} and choose the next task-relevant action."
        else:
            # This string is copied from the event record built from an observed snapshot.
            last_position = productive.summary
            app = " ".join(productive.app_name.split()) or "the recorded task workspace"
            title = " ".join(productive.window_title.split())
            if title:
                next_step = f'Return to {app} ("{title}") and continue: {declared_task}.'
            else:
                next_step = f"Return to {app} and continue: {declared_task}."
        return ResumeAnchor(last_position, UNKNOWN_PROBLEM, next_step)
