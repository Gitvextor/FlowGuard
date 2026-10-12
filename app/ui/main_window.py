"""Small Windows-first dashboard for the FlowGuard foundation.

The UI intentionally consumes the stable controller and model contracts. It
lets B's ContextMonitor own polling and only receives completed snapshots on
Qt signals; later AI/network modules can replace the classifier safely.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.controller.base_controller import (
    FlowGuardController,
    MockClassifier,
    MockContextProvider,
    MockResumeGenerator,
)
from app.context import ContextMonitor, WindowsContextProvider
from app.core.models import ActivityState, ClassificationResult, ContextSnapshot, ResumeAnchor
from app.storage.session_store import SessionStore


COLORS = {
    "canvas": "#08111F",
    "panel": "#0F1D31",
    "panel_2": "#122640",
    "line": "#233A56",
    "text": "#F2F6FC",
    "muted": "#9FB1C7",
    "cyan": "#36E6D0",
    "green": "#8BE28A",
    "gold": "#F4C96B",
    "violet": "#AFA4FF",
    "red": "#FF8A8A",
}


STATE_LABELS = {
    ActivityState.MAIN_TASK: ("主任务", COLORS["green"]),
    ActivityState.NECESSARY_DETOUR: ("必要绕路", COLORS["gold"]),
    ActivityState.DISTRACTION: ("真正偏航", COLORS["red"]),
}


def _card() -> QFrame:
    frame = QFrame()
    frame.setObjectName("card")
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return frame


class FlowGuardWindow(QMainWindow):
    """Readable single-window dashboard for a declared task."""

    snapshot_signal = pyqtSignal(object)
    monitor_error_signal = pyqtSignal(object)

    def __init__(self, controller: FlowGuardController | None = None) -> None:
        super().__init__()
        self.setWindowTitle("FlowGuard · 任务护航")
        self.resize(1120, 760)
        self.live_provider = WindowsContextProvider()
        self.live_dependency_error = self.live_provider._dependency_error()
        self.controller = controller or self._build_controller()
        self.monitor: ContextMonitor | None = None
        self._running = False
        self._last_event_count = 0

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("先写下你现在要完成的任务，例如：完成调度实验并整理报告")
        self.start_button = QPushButton("开始护航")
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self.toggle_session)
        self.session_badge = QLabel("未开始")
        self.session_badge.setObjectName("badge")

        self.state_value = QLabel("—")
        self.state_value.setObjectName("stateValue")
        self.confidence_value = QLabel("置信度 —")
        self.context_value = QLabel("等待任务开始")
        self.context_value.setWordWrap(True)
        self.context_value.setObjectName("muted")
        self.reason_value = QLabel("FlowGuard 会把当前行为分成主任务、必要绕路或真正偏航。")
        self.reason_value.setWordWrap(True)
        self.reason_value.setObjectName("muted")

        self.timeline = QListWidget()
        self.timeline.setObjectName("timeline")
        self.timeline.setMinimumHeight(220)

        self.anchor_position = QLabel("—")
        self.anchor_problem = QLabel("—")
        self.anchor_next = QLabel("—")
        for label in (self.anchor_position, self.anchor_problem, self.anchor_next):
            label.setWordWrap(True)
            label.setObjectName("anchorValue")

        self.timer = QTimer(self)
        self.timer.setInterval(1800)
        self.timer.timeout.connect(self.process_once)
        self.snapshot_signal.connect(self._handle_snapshot)
        self.monitor_error_signal.connect(self._handle_monitor_error)

        self._build_ui()
        self._apply_style()

    def _build_controller(self) -> FlowGuardController:
        data_dir = Path.home() / ".flowguard" / "sessions"
        return FlowGuardController(
            MockContextProvider(),
            MockClassifier(),
            SessionStore(data_dir),
            MockResumeGenerator(),
        )

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(30, 26, 30, 26)
        root_layout.setSpacing(18)

        header = QHBoxLayout()
        title = QLabel("FlowGuard")
        title.setObjectName("title")
        subtitle = QLabel("智能任务护航与中断恢复助手")
        subtitle.setObjectName("subtitle")
        brand = QVBoxLayout()
        brand.setSpacing(2)
        brand.addWidget(title)
        brand.addWidget(subtitle)
        header.addLayout(brand)
        header.addStretch(1)
        header.addWidget(self.session_badge)
        root_layout.addLayout(header)

        task_bar = _card()
        task_layout = QHBoxLayout(task_bar)
        task_layout.setContentsMargins(16, 14, 16, 14)
        task_layout.addWidget(self.task_input, 1)
        task_layout.addWidget(self.start_button)
        root_layout.addWidget(task_bar)

        state_card = _card()
        state_layout = QVBoxLayout(state_card)
        state_layout.setContentsMargins(18, 16, 18, 16)
        state_layout.addWidget(self._section_label("当前判断"))
        state_row = QHBoxLayout()
        state_row.addWidget(self.state_value)
        state_row.addSpacing(14)
        state_row.addWidget(self.confidence_value)
        state_row.addStretch(1)
        state_layout.addLayout(state_row)
        state_layout.addWidget(self.context_value)
        state_layout.addWidget(self.reason_value)

        timeline_card = _card()
        timeline_layout = QVBoxLayout(timeline_card)
        timeline_layout.setContentsMargins(18, 16, 18, 16)
        timeline_layout.addWidget(self._section_label("最近轨迹"))
        timeline_layout.addWidget(self.timeline)

        top_row = QHBoxLayout()
        top_row.setSpacing(18)
        top_row.addWidget(state_card, 1)
        top_row.addWidget(timeline_card, 1)
        root_layout.addLayout(top_row)

        anchor_card = _card()
        anchor_layout = QGridLayout(anchor_card)
        anchor_layout.setContentsMargins(18, 16, 18, 16)
        anchor_layout.setHorizontalSpacing(26)
        anchor_layout.addWidget(self._section_label("Resume Anchor · 返回工作时先看这里"), 0, 0, 1, 2)
        anchor_layout.addWidget(self._field_label("刚才做到哪里"), 1, 0)
        anchor_layout.addWidget(self.anchor_position, 2, 0)
        anchor_layout.addWidget(self._field_label("正在解决什么"), 1, 1)
        anchor_layout.addWidget(self.anchor_problem, 2, 1)
        anchor_layout.addWidget(self._field_label("下一步"), 3, 0)
        anchor_layout.addWidget(self.anchor_next, 4, 0, 1, 2)
        root_layout.addWidget(anchor_card)

        privacy = QLabel("截图仅在内存中处理；暂停后不再采集。Windows 版本优先读取前台窗口变化，只有稳定变化后才抓取上下文。")
        privacy.setObjectName("footer")
        privacy.setWordWrap(True)
        root_layout.addWidget(privacy)
        self.setCentralWidget(root)

    @staticmethod
    def _section_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sectionLabel")
        return label

    @staticmethod
    def _field_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def toggle_session(self) -> None:
        if self._running:
            self.timer.stop()
            if self.monitor is not None:
                self.monitor.stop()
                self.monitor = None
            self.controller.stop()
            self._running = False
            self.session_badge.setText("已暂停")
            self.start_button.setText("继续护航")
            return

        task = self.task_input.text().strip()
        if not task:
            self.task_input.setFocus()
            self.context_value.setText("请先输入一个具体任务，再开始护航。")
            return
        try:
            self.controller.start(task)
        except RuntimeError:
            self.controller.stop()
            self.controller.start(task)
        self._running = True
        self._last_event_count = 0
        self.timeline.clear()
        self.start_button.setText("暂停")
        if self.live_dependency_error is None:
            try:
                self.live_provider.register_own_window(int(self.winId()), self.windowTitle())
                self.monitor = ContextMonitor(
                    self.live_provider,
                    on_snapshot=lambda snapshot: self.snapshot_signal.emit(snapshot),
                    on_error=lambda error: self.monitor_error_signal.emit(error),
                )
                self.monitor.start(task)
                self.session_badge.setText("护航中 · 实时")
            except Exception as exc:
                self.monitor = None
                self.session_badge.setText("护航中 · 演示")
                self.reason_value.setText(f"实时监控未启动，已回退演示链路：{exc}")
                self.process_once()
                self.timer.start()
        else:
            self.session_badge.setText("护航中 · 演示")
            self.reason_value.setText(f"当前环境未启用 Windows Context，使用演示链路：{self.live_dependency_error}")
            self.process_once()
            self.timer.start()

    def process_once(self) -> None:
        if not self._running:
            return
        try:
            context, result, anchor = self.controller.process_once()
        except Exception as exc:  # keep a UI error from terminating the session
            self.session_badge.setText("等待重试")
            self.reason_value.setText(f"本次采集未完成：{exc}")
            return
        self._update_state(context, result, anchor)

    def _handle_snapshot(self, snapshot: ContextSnapshot) -> None:
        if not self._running:
            return
        try:
            context, result, anchor = self.controller.process_snapshot(snapshot)
        except Exception as exc:
            self._handle_monitor_error(exc)
            return
        self._update_state(context, result, anchor)

    def _handle_monitor_error(self, error: Exception) -> None:
        self.session_badge.setText("护航中 · 等待重试")
        self.reason_value.setText(f"上下文采集暂未完成：{error}")

    def _update_state(self, context: ContextSnapshot, result: ClassificationResult, anchor: ResumeAnchor) -> None:
        label, color = STATE_LABELS[result.state]
        self.state_value.setText(label)
        self.state_value.setStyleSheet(f"color: {color};")
        self.confidence_value.setText(f"置信度 {result.confidence:.0%}")
        self.context_value.setText(f"{context.app_name}  ·  {context.window_title}")
        self.reason_value.setText(result.task_relation or result.reason)
        self.anchor_position.setText(anchor.last_position)
        self.anchor_problem.setText(anchor.current_problem)
        self.anchor_next.setText(anchor.next_step)

        events = self.controller.history_store.get_recent_events(8)
        if len(events) == self._last_event_count:
            return
        self._last_event_count = len(events)
        self.timeline.clear()
        for event in reversed(events):
            event_label, event_color = STATE_LABELS[event.state]
            stamp = event.timestamp.astimezone().strftime("%H:%M:%S")
            item = QListWidgetItem(f"{stamp}   {event_label}   {event.window_title}")
            item.setForeground(Qt.GlobalColor.white)
            item.setToolTip(event.summary)
            self.timeline.addItem(item)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            f"""
            QMainWindow, QWidget {{ background: {COLORS['canvas']}; color: {COLORS['text']}; font-family: 'Microsoft YaHei'; }}
            QLabel {{ background: transparent; }}
            QFrame#card {{ background: {COLORS['panel']}; border: 1px solid {COLORS['line']}; border-radius: 14px; }}
            QLabel#title {{ color: {COLORS['text']}; font-size: 30px; font-weight: 700; }}
            QLabel#subtitle {{ color: {COLORS['cyan']}; font-size: 14px; }}
            QLabel#badge {{ color: {COLORS['cyan']}; background: #102E3A; border: 1px solid #225A67; border-radius: 11px; padding: 7px 14px; font-weight: 600; }}
            QLabel#sectionLabel {{ color: {COLORS['cyan']}; font-size: 15px; font-weight: 700; padding-bottom: 5px; }}
            QLabel#fieldLabel {{ color: {COLORS['muted']}; font-size: 12px; }}
            QLabel#stateValue {{ font-size: 28px; font-weight: 700; }}
            QLabel#muted, QLabel#footer {{ color: {COLORS['muted']}; font-size: 13px; }}
            QLabel#anchorValue {{ color: {COLORS['text']}; font-size: 14px; line-height: 1.4; }}
            QLineEdit {{ background: {COLORS['panel_2']}; border: 1px solid {COLORS['line']}; border-radius: 9px; padding: 11px 13px; color: {COLORS['text']}; font-size: 14px; }}
            QLineEdit:focus {{ border: 1px solid {COLORS['cyan']}; }}
            QPushButton#primaryButton {{ background: {COLORS['cyan']}; color: #07121D; border: none; border-radius: 9px; padding: 10px 20px; font-weight: 700; }}
            QPushButton#primaryButton:hover {{ background: #72F3E4; }}
            QListWidget#timeline {{ background: transparent; border: none; outline: none; padding: 2px; }}
            QListWidget#timeline::item {{ padding: 9px 8px; border-bottom: 1px solid {COLORS['line']}; }}
            QListWidget#timeline::item:selected {{ background: {COLORS['panel_2']}; }}
            """
        )

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt callback name
        if self.monitor is not None:
            self.monitor.stop()
            self.monitor = None
        if self.controller.running:
            self.controller.stop()
        event.accept()


def launch() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("FlowGuard")
    window = FlowGuardWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(launch())
