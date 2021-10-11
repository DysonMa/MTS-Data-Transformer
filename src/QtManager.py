from typing import Union, List, Tuple
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import (
    QWidget,
    QFileDialog,
    QMessageBox,
)
import numpy as np
import os
import logging
from PlotManager import *
from DataManager import DataManager
from ThreadManager import PlotWorker


class MainWindow(QWidget):
    def __init__(self, ui_file_path) -> None:
        super().__init__()
        loadUi(ui_file_path, self)

        self.current_dir = os.path.dirname(ui_file_path)
        self.input_file_name = None

        self.setWindowTitle('MTS Data Transformer')
        Initial_layout_Figure(self)

        # connect funcs to widgets
        self.custom_area_checkbox.toggled.connect(
            self.custom_area_input.setEnabled)
        self.select_input_file_btn.clicked.connect(self.read_input_file)
        self.ratio_num_spinbox.valueChanged.connect(self.change_row)
        self.plot_btn.clicked.connect(self.plot)

    def get_datas(self) -> Dict:
        ratio_type, exNum = self.get_ratio_type_and_exNum_from_input()
        payload = {
            "area": self.get_area(),
            "ratio_type": ratio_type,
            "exNum": exNum
        }
        dataManager = DataManager(self.input_file_name)
        return dataManager.get_datas(payload)

    def get_ratio_type_and_exNum_from_input(self) -> Tuple:
        ratio_type, exNum = [], []
        for i in range(self.ratio_widget.rowCount()):
            if self.ratio_widget.item(i, 0) == None or self.ratio_widget.item(i, 0).text() == "":
                raise Exception("配比種類輸入不正確!")
            if self.ratio_widget.item(i, 1) == None or not self.ratio_widget.item(i, 1).text().isdigit():
                raise Exception("配比數量輸入不正確!")
            ratio_type.append(self.ratio_widget.item(i, 0).text())
            exNum.append(int(self.ratio_widget.item(i, 1).text()))
        if ratio_type == [] or exNum == []:
            raise Exception("配比種類數量為零!")
        return (ratio_type, exNum)

    def get_area(self) -> Union[float, int]:
        # cylinder
        if self.cylinder_checkbox.isChecked():
            return np.pi/4*10**2
        # cube
        elif self.cube_checkbox.isChecked():
            return 5**2
        # custom area
        elif self.custom_area_checkbox.isChecked() and self.custom_area_input != "":
            return float(self.custom_area_input.text())
        else:
            raise Exception("沒有正確輸入試體尺寸!")

    def read_input_file(self) -> None:
        self.input_file_name, filetype = QFileDialog.getOpenFileName(
            self, "選取檔案", os.path.join(
                self.current_dir, "input"), "txt file(*.txt)",
        )
        self.path_txt.setText(self.input_file_name)

    def change_row(self) -> None:
        self.ratio_widget.setRowCount(self.ratio_num_spinbox.value())

    def finish(self, path: Dict) -> None:
        # message box
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Success")
        msgBox.setWindowTitle("Congratulation")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

        # put the figures on the canvas
        layout_Figure(
            path["bigger_figure_path"], self.graphicsView_all)
        layout_Figure(
            path["avg_max_stress_figure_path"], self.graphicsView_comp)
        layout_Figure(
            path["avg_max_em_figure_path"], self.graphicsView_em)

        # enable plot button
        self.plot_btn.setEnabled(True)

    def update_progressbar(self, value: int) -> None:
        self.progressBar.setValue(value)

    def plot(self) -> None:
        try:
            # validate input file path
            if not self.input_file_name:
                raise Exception("輸入資料路徑為空!")

            # process datas
            datas = self.get_datas()

            # validate datas
            if len(datas["specimens_datas"]) == 0:
                raise Exception("輸入資料筆數為零!")
            if self.save_file_name_input.text() == "":
                raise Exception("存檔資料夾的名稱為空!")

            # set save folder path (output)
            folder_name = "output"
            folder_path = os.path.join(self.current_dir, folder_name)
            if folder_name not in os.listdir(self.current_dir):
                os.mkdir(folder_path)
            logging.debug(f"folder_path: {folder_path}")
            # set save folder path (ex: test, test2, WTF_MTS...)
            save_folder_name = self.save_file_name_input.text()
            save_folder_path = os.path.join(folder_path, save_folder_name)
            if save_folder_name not in os.listdir(folder_path):
                os.mkdir(save_folder_path)
            logging.debug(f"save_folder_path: {save_folder_path}")

            # add additional datas
            datas["comp_title"] = self.comp_title_input.text()
            datas["em_title"] = self.em_title_input.text()
            datas["save_folder_path"] = save_folder_path

            # execute PlotWorker thread
            Initial_layout_Figure(self)  # initialize all canvas
            self.plot_btn.setEnabled(False)  # disable plot button
            self.plotWorker = PlotWorker(datas)
            self.plotWorker.start()
            self.plotWorker.trigger.connect(self.update_progressbar)
            self.plotWorker.finish.connect(self.finish)

        except Exception as e:
            logging.error("Catch an exception.", exc_info=True)
            QMessageBox.critical(self, 'Error', str(
                e), QMessageBox.Yes | QMessageBox.Yes)
