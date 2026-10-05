"""Three-way activity classifier consuming B's ContextSnapshot directly."""

from __future__ import annotations

import os
from typing import Any

from app.ai.llm_client import LLMClient
from app.core import ActivityState, ClassificationResult, ContextSnapshot, HistoryEvent

from .classifier_parser import ClassificationParser
from .prompt_builder import build_classifier_prompt


UNAVAILABLE = ClassificationResult(
    state=ActivityState.MAIN_TASK,
    confidence=0.0,
    reason="Classification unavailable",
    task_relation="",
)


class ActivityClassifier:
    """Classify an existing snapshot without collecting context or screenshots."""

    def __init__(
        self,
        client: Any | None = None,
        *,
        parser: ClassificationParser | None = None,
        mock: bool | None = None,
    ) -> None:
        self.mock = _env_bool("FLOWGUARD_MOCK") if mock is None else mock
        self.client = client if client is not None else (None if self.mock else LLMClient())
        self.parser = parser or ClassificationParser()
        self.last_error: str | None = None

    def classify(self, context: ContextSnapshot) -> ClassificationResult:
        """Return a shared result; API and parser failures are non-fatal."""

        self.last_error = None
        if self.mock:
            return self._classify_mock(context)
        try:
            response = self.client.analyze(
                context.screenshot,
                build_classifier_prompt(context),
                context={
                    "task": context.task,
                    "app_name": context.app_name,
                    "window_title": context.window_title,
                    "timestamp": context.timestamp.isoformat(),
                },
            )
            return self.parser.parse(response)
        except Exception as exc:  # The monitor must continue even if a model call fails.
            self.last_error = str(exc) or exc.__class__.__name__
            return ClassificationResult(
                state=UNAVAILABLE.state,
                confidence=UNAVAILABLE.confidence,
                reason=UNAVAILABLE.reason,
                task_relation=UNAVAILABLE.task_relation,
            )

    @staticmethod
    def to_history_event(
        context: ContextSnapshot,
        result: ClassificationResult,
    ) -> HistoryEvent | None:
        """Build a compact record from observed fields; skip unavailable classifications."""

        if result.confidence <= 0.0 or result.reason == UNAVAILABLE.reason:
            return None
        app = _safe_label(context.app_name, "Unknown application")
        title = _safe_label(context.window_title, "Untitled window")
        # Keep this summary extractive: it reports the exact observed app/title and
        # assigned state instead of turning a model's free-form rationale into fact.
        summary = f'{app} — "{title}" [{result.state.value}]'
        return HistoryEvent(
            timestamp=context.timestamp,
            app_name=context.app_name,
            window_title=context.window_title,
            state=result.state,
            summary=summary,
        )

    def _classify_mock(self, context: ContextSnapshot) -> ClassificationResult:
        app = context.app_name.casefold()
        title = context.window_title.casefold()
        combined = f"{app} {title}"

        if _matches(combined, _DISTRACTION_TERMS):
            return _result(
                ActivityState.DISTRACTION,
                0.86,
                "The observed app or window title matches an unrelated entertainment or shopping cue.",
                "The visible context has no clear relation to the declared task.",
            )
        if _matches(combined, _DETOUR_TERMS):
            return _result(
                ActivityState.NECESSARY_DETOUR,
                0.82,
                "The observed title contains a task-supporting reference or research cue.",
                "The visible context may support the declared task; relevance is based on the title cue.",
            )
        if _matches(app, _WORK_APP_TERMS) or _matches(title, _WORK_TITLE_TERMS):
            return _result(
                ActivityState.MAIN_TASK,
                0.78,
                "The observed app or title matches a work-oriented context cue.",
                "The visible context appears to be the task workspace.",
            )
        return _result(
            ActivityState.MAIN_TASK,
            0.20,
            "The available context is ambiguous; no clear detour or distraction cue was found.",
            "Insufficient title evidence to determine the task relationship.",
        )


def _result(
    state: ActivityState,
    confidence: float,
    reason: str,
    task_relation: str,
) -> ClassificationResult:
    return ClassificationResult(state, confidence, reason, task_relation)


def _safe_label(value: str, fallback: str) -> str:
    cleaned = " ".join(str(value).split())
    return cleaned or fallback


def _matches(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().casefold() in {"1", "true", "yes", "on"}


_DISTRACTION_TERMS = (
    "bilibili", "youtube", "funny video", "funny cats", "entertainment", "shopping",
    "taobao", "tiktok", "instagram", "netflix", "gameplay", "gaming session",
    "travel photos", "vacation",
)
_DETOUR_TERMS = (
    "stack overflow", "stackoverflow", "documentation", "docs", "google scholar",
    "research paper", "research papers", "journal article", "paper search", "keyerror",
    "traceback", "python error", "debugging", "debug", "tutorial", "priority scheduling",
    "assignment group", "lab group", "exam timetable", "mdn", "css grid",
)
_WORK_APP_TERMS = (
    "code.exe", "visual studio code", "vscode", "pycharm", "notepad++", "word",
    "libreoffice", "wps", "intellij", "eclipse", "excel", "notion", "adobe reader",
)
_WORK_TITLE_TERMS = (
    "main.py", ".py -", ".py —", ".docx", ".pdf", ".tex", "priority_preemptive",
    "process_scheduling", "unsaved", "visual studio code",
)
