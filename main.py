"""FlowGuard desktop entry point."""

import sys
from PyQt6.QtWidgets import QApplication
from app.ui import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("FlowGuard")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
