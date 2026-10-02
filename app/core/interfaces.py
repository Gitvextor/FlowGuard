"""Public integration contracts for FlowGuard."""

from typing import Protocol

from .models import ClassificationResult, ContextSnapshot, HistoryEvent, ResumeAnchor


class ContextProvider(Protocol):
    def capture(self, task: str) -> ContextSnapshot:
        """Collect one task-context snapshot without persisting the screenshot."""
        ...


class ActivityClassifier(Protocol):
    def classify(self, context: ContextSnapshot) -> ClassificationResult:
        """Classify a snapshot into the stable three-state schema."""
        ...


class ResumeAnchorGenerator(Protocol):
    def generate(self, task: str, history: list[HistoryEvent]) -> ResumeAnchor:
        """Describe where and how a user should resume a task."""
        ...
