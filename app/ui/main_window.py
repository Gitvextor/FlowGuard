"""Main FlowGuard desktop window."""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import (QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QPushButton, QSystemTrayIcon, QVBoxLayout, QWidget)

from app.controller.controller import IntegratedController
from app.core import ActivityState
from app.notifications import WindowsNotifier
from .resume_widget import ResumeWidget
from .timeline_widget import TimelineWidget


class _Bridge(QObject):
    result = pyqtSignal(object, object, object, object)
    error = pyqtSignal(str)


class MainWindow(QMainWindow):
    COLORS = {ActivityState.MAIN_TASK: "#1f9d55", ActivityState.NECESSARY_DETOUR: "#d97706",
              ActivityState.DISTRACTION: "#dc2626"}

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowGuard")
        self.resize(850, 720)
        self.bridge = _Bridge()
        self.bridge.result.connect(self._show_result)
        self.bridge.error.connect(lambda message: self.statusBar().showMessage(message, 8000))
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        self.tray.show()
        self.controller = IntegratedController(notifier=WindowsNotifier(self.tray),
            on_result=self.bridge.result.emit, on_error=self.bridge.error.emit)
        self._build_ui()

    def _build_ui(self):
        root, layout = QWidget(), QVBoxLayout()
        root.setLayout(layout)
        task_box, task_layout = QGroupBox("Current Task"), QVBoxLayout()
        task_box.setLayout(task_layout)
        self.task_input = QLineEdit(); self.task_input.setPlaceholderText("例如：完成操作系统 Priority Scheduling 实验")
        buttons = QHBoxLayout()
        self.start_button, self.pause_button = QPushButton("开始护航"), QPushButton("暂停")
        self.pause_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_guard); self.pause_button.clicked.connect(self.pause_guard)
        buttons.addWidget(self.start_button); buttons.addWidget(self.pause_button)
        task_layout.addWidget(self.task_input); task_layout.addLayout(buttons)
        state_box, form = QGroupBox("Current State"), QFormLayout()
        state_box.setLayout(form)
        self.state_label, self.app_label, self.window_label = QLabel("WAITING"), QLabel("—"), QLabel("—")
        self.state_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #64748b")
        self.window_label.setWordWrap(True)
        form.addRow("分类", self.state_label); form.addRow("App", self.app_label); form.addRow("Window", self.window_label)
        self.timeline = TimelineWidget(); timeline_box = QGroupBox("Recent Activity")
        timeline_layout = QVBoxLayout(); timeline_layout.addWidget(self.timeline); timeline_box.setLayout(timeline_layout)
        self.resume = ResumeWidget()
        layout.addWidget(task_box); layout.addWidget(state_box); layout.addWidget(timeline_box, 1); layout.addWidget(self.resume)
        self.setCentralWidget(root)
        self.statusBar().showMessage("Mock 模式可设置 FLOWGUARD_MOCK=true；截图仅在内存中处理。")

    def showEvent(self, event):
        super().showEvent(event)
        try: self.controller.provider.register_own_window(int(self.winId()), self.windowTitle())
        except Exception: pass

    def start_guard(self):
        try: session_id = self.controller.start(self.task_input.text())
        except Exception as exc: self.statusBar().showMessage(str(exc), 8000); return
        self.task_input.setEnabled(False); self.start_button.setEnabled(False); self.pause_button.setEnabled(True)
        self.statusBar().showMessage(f"护航已开始 · Session {session_id}")

    def pause_guard(self):
        self.controller.pause()
        self.task_input.setEnabled(True); self.start_button.setEnabled(True); self.pause_button.setEnabled(False)
        self.statusBar().showMessage("已暂停；不会发起新的分析请求。")

    def _show_result(self, snapshot, result, history, anchor):
        self.state_label.setText(result.state.value.replace("_", " "))
        self.state_label.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {self.COLORS[result.state]}")
        self.app_label.setText(snapshot.app_name); self.window_label.setText(snapshot.window_title)
        self.timeline.update_events(history)
        if anchor is not None: self.resume.set_anchor(anchor)
        self.statusBar().showMessage(f"置信度 {result.confidence:.0%} · {result.reason}", 10000)

    def closeEvent(self, event):
        self.controller.shutdown(); self.tray.hide(); event.accept()
