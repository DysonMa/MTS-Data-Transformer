import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt5.uic import loadUi
from UI_Manager import UI
import os

app = QApplication(sys.argv)
app.setStyle("Fusion")
# w = loadUi('MTS.ui')
ui = UI('MTS.ui')
ui.show()
# w.show()
app.exec_()
