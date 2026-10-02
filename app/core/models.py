"""Stable shared schemas. Later milestones must import, never redefine, these."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ActivityState(str, Enum):
    MAIN_TASK = "MAIN_TASK"
    NECESSARY_DETOUR = "NECESSARY_DETOUR"
    DISTRACTION = "DISTRACTION"


@dataclass
class ContextSnapshot:
    timestamp: datetime
    task: str
    app_name: str
    window_title: str
    screenshot: bytes


@dataclass
class ClassificationResult:
    state: ActivityState
    confidence: float
    reason: str
    task_relation: str


@dataclass
class HistoryEvent:
    timestamp: datetime
    app_name: str
    window_title: str
    state: ActivityState
    summary: str


@dataclass
class ResumeAnchor:
    last_position: str
    current_problem: str
    next_step: str
