"""Platform-independent FlowGuard execution skeleton."""

from collections.abc import Callable
from datetime import datetime

from app.core.interfaces import ActivityClassifier, ContextProvider, ResumeAnchorGenerator
from app.core.models import (
    ActivityState,
    ClassificationResult,
    ContextSnapshot,
    HistoryEvent,
    ResumeAnchor,
)
from app.storage.session_store import SessionStore


class FlowGuardController:
    """Run the fixed Context -> Classifier -> History -> Resume -> Callback chain."""

    def __init__(
        self,
        context_provider: ContextProvider,
        classifier: ActivityClassifier,
        history_store: SessionStore,
        resume_generator: ResumeAnchorGenerator,
        on_result: Callable[[ContextSnapshot, ClassificationResult, ResumeAnchor], None] | None = None,
    ) -> None:
        self.context_provider = context_provider
        self.classifier = classifier
        self.history_store = history_store
        self.resume_generator = resume_generator
        self.on_result = on_result
        self.task: str | None = None
        self.running = False

    def start(self, task: str) -> str:
        if self.running:
            raise RuntimeError("FlowGuard is already running.")
        self.task = task.strip()
        session_id = self.history_store.start_session(self.task)
        self.running = True
        return session_id

    def process_once(self) -> tuple[ContextSnapshot, ClassificationResult, ResumeAnchor]:
        if not self.running or not self.task:
            raise RuntimeError("Start FlowGuard before processing context.")

        context = self.context_provider.capture(self.task)
        return self.process_snapshot(context)

    def process_snapshot(
        self, context: ContextSnapshot
    ) -> tuple[ContextSnapshot, ClassificationResult, ResumeAnchor]:
        """Classify an already captured snapshot from a context monitor.

        The Windows context monitor owns polling and screenshot triggers. This
        entry point lets the UI consume its snapshots without a second capture
        loop.
        """

        if not self.running or not self.task:
            raise RuntimeError("Start FlowGuard before processing context.")

        result = self.classifier.classify(context)
        event = HistoryEvent(
            timestamp=context.timestamp,
            app_name=context.app_name,
            window_title=context.window_title,
            state=result.state,
            summary=result.task_relation or result.reason,
        )
        self.history_store.append_event(event)
        anchor = self.resume_generator.generate(self.task, self.history_store.get_recent_events())
        if self.on_result:
            self.on_result(context, result, anchor)
        return context, result, anchor

    def stop(self) -> None:
        if self.running:
            self.history_store.end_session()
        self.running = False
        self.task = None


class MockContextProvider:
    def capture(self, task: str) -> ContextSnapshot:
        return ContextSnapshot(
            timestamp=datetime.now().astimezone(),
            task=task,
            app_name="MockCode.exe",
            window_title="main.py - Mock Editor",
            screenshot=b"mock-screenshot",
        )


class MockClassifier:
    def classify(self, context: ContextSnapshot) -> ClassificationResult:
        title = context.window_title.lower()
        if "stackoverflow" in title or "documentation" in title:
            state = ActivityState.NECESSARY_DETOUR
            relation = "Looking up information needed for the task."
        elif "bilibili" in title or "entertainment" in title:
            state = ActivityState.DISTRACTION
            relation = "This activity is unrelated to the declared task."
        else:
            state = ActivityState.MAIN_TASK
            relation = "Directly progressing the declared task."
        return ClassificationResult(state=state, confidence=1.0, reason="Mock classification.", task_relation=relation)


class MockResumeGenerator:
    def generate(self, task: str, history: list[HistoryEvent]) -> ResumeAnchor:
        latest = history[-1] if history else None
        return ResumeAnchor(
            last_position=(f"{latest.window_title} ({latest.app_name})" if latest else "No productive context yet."),
            current_problem="Mock mode does not infer an unresolved problem.",
            next_step=f"Return to: {task}",
        )
