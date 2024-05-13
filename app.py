from PyQt6.QtWidgets import QApplication
from model_window import *
import sys

def main():
    app = QApplication(sys.argv)

    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
