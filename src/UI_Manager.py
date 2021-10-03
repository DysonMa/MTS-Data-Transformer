from PyQt5.uic import loadUi
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QFileDialog,
    QPushButton,
    QTableWidget,
    QSpinBox,
    QMessageBox,
)
import numpy as np
import os

from PlotManager import PlotManager


class UI(QWidget):
    def __init__(self, UI_FileName):
        super().__init__()
        loadUi(UI_FileName, self)

        self.setWindowTitle('MTSDataProcess')
        self.plotManager = PlotManager(self)
        self.plotManager.Initial_layout_Figure()

        # 垂直滑動棒 -> 控制剔除的%數，預設20%
        self.compVerticalSlider.setValue(20)
        self.EMVerticalSlider.setValue(20)

        self.compVerticalSlider.valueChanged.connect(
            lambda: self.add_percentage_label(
                self.compLabel, self.compVerticalSlider.value()
            )
        )
        self.EMVerticalSlider.valueChanged.connect(
            lambda: self.add_percentage_label(
                self.EMLabel, self.EMVerticalSlider.value()
            )
        )

        # self.ReCompPlotBtn.clicked.connect(self.compRePlot)
        # self.ReEMPlotBtn.clicked.connect(self.EMRePlot)

        # self.selectBtn.clicked.connect(self.test)

        self.selectBtn.clicked.connect(self.read_input_file)
        self.spinBox.valueChanged.connect(self.change_row)
        self.saveBtn.clicked.connect(self.save_folder)
        self.pltBtn.clicked.connect(self.plot)

    def plot(self):
        return self.plotManager.plot()

    def read_input_file(self):
        fileName, filetype = QFileDialog.getOpenFileName(
            self, "選取檔案", "", "txt file(*.txt)", None
        )
        if fileName == '':
            return
        self.PathTxt.setText(fileName)

    def change_row(self):
        self.inputWidget.setRowCount(self.spinBox.value())

    def save_folder(self):
        # global PathFile
        PathFile = QFileDialog.getExistingDirectory(self, "選取資料夾", "")
        if PathFile == '':
            return
        self.savePathTxt.setText(PathFile)

    # utility
    def add_percentage_label(self, labeledElement, value):
        labeledElement.setText(str(value)+"%")
