import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.main_window import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    app.setApplicationName("XML Parser")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
