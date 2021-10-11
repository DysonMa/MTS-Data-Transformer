import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
)
from QtManager import MainWindow
import logging


class MTS:
    def __init__(self, ui_file):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        self.ui_file = ui_file

    def run(self):
        ui = MainWindow(self.ui_file)
        ui.show()
        self.app.exec_()


if __name__ == "__main__":
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(
        level=logging.DEBUG,
        filename='MTS_Log.log',
        filemode='w',
        format=FORMAT
    )
    try:
        os.chdir("./src")
        MTS("MTS.ui").run()
    except Exception as e:
        logging.error("Catch an exception.", exc_info=True)
