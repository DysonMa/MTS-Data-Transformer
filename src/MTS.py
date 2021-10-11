import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
)
from UI_Manager import UI


class MTS:
    def __init__(self, ui_file):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        self.ui_file = ui_file

    def run(self):
        ui = UI(self.ui_file)
        ui.show()
        self.app.exec_()


if __name__ == "__main__":
    os.chdir("./src")
    MTS("MTS.ui").run()
