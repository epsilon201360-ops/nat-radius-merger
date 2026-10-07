#!/usr/bin/env python
"""
NAT/RADIUS Merger Application
Application Windows PyQt5 pour traiter et fusionner des fichiers NAT et RADIUS
"""

import sys
from PyQt5.QtWidgets import QApplication
from app.ui.main_window import MainWindow


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
