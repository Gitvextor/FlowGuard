"""Platform-independent FlowGuard execution skeleton."""

from collections.abc import Callable
from datetime import datetime
from threading import RLock

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
        self._generation = 0
        self._state_lock = RLock()

    def start(self, task: str) -> str:
        normalized_task = task.strip()
        if not normalized_task:
            raise ValueError("A non-empty task is required to start FlowGuard.")
        with self._state_lock:
            if self.running:
                raise RuntimeError("FlowGuard is already running.")
            session_id = self.history_store.start_session(normalized_task)
            self.task = normalized_task
            self.running = True
            self._generation += 1
            return session_id

    def process_once(self) -> tuple[ContextSnapshot, ClassificationResult, ResumeAnchor]:
        with self._state_lock:
            if not self.running or not self.task:
                raise RuntimeError("Start FlowGuard before processing context.")
            task = self.task

        context = self.context_provider.capture(task)
        return self.process_snapshot(context)

    def process_snapshot(
        self, context: ContextSnapshot
    ) -> tuple[ContextSnapshot, ClassificationResult, ResumeAnchor]:
        """Classify an already captured snapshot from a context monitor.

        The Windows context monitor owns polling and screenshot triggers. This
        entry point lets the UI consume its snapshots without a second capture
        loop.
        """

        with self._state_lock:
            if not self.running or not self.task:
                raise RuntimeError("Start FlowGuard before processing context.")
            task = self.task
            generation = self._generation
        result = self.classifier.classify(context)
        with self._state_lock:
            if not self.running or generation != self._generation:
                raise RuntimeError("Discarded a result from a stopped or replaced session.")
            event = HistoryEvent(
                timestamp=context.timestamp,
                app_name=context.app_name,
                window_title=context.window_title,
                state=result.state,
                summary=result.task_relation or result.reason,
            )
            self.history_store.append_event(event)
            history = self.history_store.get_recent_events()
        anchor = self.resume_generator.generate(task, history)
        if self.on_result:
            self.on_result(context, result, anchor)
        return context, result, anchor

    def stop(self) -> None:
        with self._state_lock:
            if self.running:
                self.history_store.end_session()
                self._generation += 1
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
            relation = "演示规则命中资料检索关键词；结果仅用于展示。"
        elif "bilibili" in title or "entertainment" in title:
            state = ActivityState.DISTRACTION
            relation = "演示规则命中娱乐关键词；结果仅用于展示。"
        else:
            state = ActivityState.MAIN_TASK
            relation = "未命中演示关键词；这不能证明行为与任务相关。"
        return ClassificationResult(
            state=state,
            confidence=0.4,
            reason="演示规则判断；未调用视觉模型。",
            task_relation=relation,
        )


class MockResumeGenerator:
    def generate(self, task: str, history: list[HistoryEvent]) -> ResumeAnchor:
        latest = history[-1] if history else None
        return ResumeAnchor(
            last_position=(f"{latest.window_title} ({latest.app_name})" if latest else "No productive context yet."),
            current_problem="Mock mode does not infer an unresolved problem.",
            next_step=f"Return to: {task}",
        )
