from PyQt6.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout


class ResumeWidget(QGroupBox):
    def __init__(self):
        super().__init__("Resume Anchor")
        self.text = QLabel("确认中断后，这里会显示有依据的恢复提示。")
        self.text.setWordWrap(True)
        self.dismiss = QPushButton("关闭提示")
        self.dismiss.clicked.connect(self.clear_anchor)
        layout = QVBoxLayout(self)
        layout.addWidget(self.text)
        layout.addWidget(self.dismiss)

    def set_anchor(self, anchor):
        self.text.setText(
            f"刚才做到：{anchor.last_position}\n\n"
            f"当前问题：{anchor.current_problem}\n\n"
            f"下一步：{anchor.next_step}")

    def clear_anchor(self):
        self.text.setText("确认中断后，这里会显示有依据的恢复提示。")
