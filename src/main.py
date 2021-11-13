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
        # determine if application is a script file or frozen exe
        # if getattr(sys, 'frozen', False):
        #     application_path = os.path.dirname(sys.executable)
        # elif __file__:
        #     application_path = os.path.dirname(__file__)

        application_path = os.path.abspath( os.path.join(os.path.dirname(__file__), '..'))
        ui_file_path = os.path.join(os.path.dirname(__file__), "MTS.ui")
        
        logging.debug(f"application_path: {application_path}")
        logging.debug(f"ui_file_path: {ui_file_path}")

        MTS(ui_file_path).run()

    except Exception as e:
        logging.error("Catch an exception.", exc_info=True)
