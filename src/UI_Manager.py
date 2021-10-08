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
from DataManager import DataManager


class UI(QWidget):
    def __init__(self, UI_FileName):
        super().__init__()
        loadUi(UI_FileName, self)

        self.input_file_name = None
        self.setWindowTitle('MTSDataProcess')
        self.plotManager = PlotManager(self)
        self.plotManager.Initial_layout_Figure()

        self.select_input_file_btn.clicked.connect(self.read_input_file)
        self.ratio_num_spinbox.valueChanged.connect(self.change_row)
        self.plot_btn.clicked.connect(self.plot)

    def get_datas(self):
        dataManager = DataManager(self.input_file_name)
        specimens_datas = dataManager.get_specimen_datas_json(self.get_area())
        ratio_type, exNum = self.get_ratio_type_and_exNum_from_input()
        exNum_ids = dataManager.get_exNum_ids(exNum)
        max_stress_list = dataManager.get_max_stress_list(specimens_datas)
        avg_max_stress_list = dataManager.get_avg_max_stress_per_group(
            specimens_datas,
            exNum
        )
        max_em_list = dataManager.get_max_em_list(specimens_datas)
        avg_max_em_list = dataManager.get_avg_max_em_per_group(
            specimens_datas,
            exNum
        )
        return (
            specimens_datas,
            ratio_type,
            exNum,
            exNum_ids,
            max_stress_list,
            avg_max_stress_list,
            max_em_list,
            avg_max_em_list
        )

    def get_ratio_type_and_exNum_from_input(self):
        ratio_type, exNum = [], []
        for i in range(self.ratio_widget.rowCount()):
            if self.ratio_widget.item(i, 0) == None:
                QMessageBox.critical(
                    self,
                    'Error',
                    "配比種類沒有完整輸入!",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                )
                return
            # TODO: add ratio_type validator
            ratio_type.append(self.ratio_widget.item(i, 0).text())
            # TODO: add exNum validator
            exNum.append(int(self.ratio_widget.item(i, 1).text()))
        return (ratio_type, exNum)

    def get_area(self):
        if self.cylinder_checkbox.isChecked():
            area = np.pi/4*10**2
        elif self.cube_checkbox.isChecked():
            area = 5**2
        elif self.custom_area_checkbox.isChecked():
            area = self.custom_area_input.text()
        else:
            QMessageBox.critical(self, 'Error', "沒有選試體尺寸!",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        return area

    def plot(self):
        (specimens_datas,
         ratio_type,
         exNum,
         exNum_ids,
         max_stress_list,
         avg_max_stress_list,
         max_em_list,
         avg_max_em_list) = self.get_datas()
        return self.plotManager.plot(
            specimens_datas=specimens_datas,
            ratio_type=ratio_type,
            exNum=exNum,
            exNum_ids=exNum_ids,
            max_stress_list=max_stress_list,
            avg_max_stress_list=avg_max_stress_list,
            max_em_list=max_em_list,
            avg_max_em_list=avg_max_em_list
        )

    def read_input_file(self):
        self.input_file_name, filetype = QFileDialog.getOpenFileName(
            self, "選取檔案", "", "txt file(*.txt)", None
        )
        if self.input_file_name == '':
            return
        self.path_txt.setText(self.input_file_name)

    def change_row(self):
        self.ratio_widget.setRowCount(self.ratio_num_spinbox.value())

    # def save_folder(self):
    #     # global PathFile
    #     PathFile = QFileDialog.getExistingDirectory(self, "選取資料夾", "")
    #     if PathFile == '':
    #         return
    #     self.savePathTxt.setText(PathFile)

    # utility
    def add_percentage_label(self, labeledElement, value):
        labeledElement.setText(str(value)+"%")
