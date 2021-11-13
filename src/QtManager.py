from typing import Union, List, Tuple
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import (
    QWidget,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import QItemSelectionModel
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

        self.current_dir = os.path.abspath(os.path.join(os.path.dirname(ui_file_path), '..'))
        self.input_file_name = ""
        self.multiple_file_names = []
        self.model = None

        self.setWindowTitle('MTS Data Transformer')
        Initial_layout_Figure(self)

        # connect funcs to widgets
        # 1. merge files
        self.select_multiple_files_btn.clicked.connect(self.__add_multiple_files)
        self.move_up_btn.clicked.connect(self.__move_up)
        self.move_down_btn.clicked.connect(self.__move_down)
        self.merge_btn.clicked.connect(self.__merge_file)
        self.delete_one_file_btn.clicked.connect(self.__delete_one_file)
        self.delete_all_files_btn.clicked.connect(self.__delete_all_files)
        # 2. process data
        self.custom_area_checkbox.toggled.connect(self.custom_area_input.setEnabled)
        self.select_input_file_btn.clicked.connect(self.__read_input_file)
        self.ratio_num_spinbox.valueChanged.connect(self.__change_row)
        self.plot_btn.clicked.connect(self.plot)

    # ================================ MERGE FILES ===================================
    def __add_multiple_files(self) -> None:
        selected_file_names, filetype = QFileDialog.getOpenFileNames(
            self, 
            "選取檔案", 
            os.path.join(self.current_dir, "input"), 
            "txt files(*.txt)",
        )  # selected_file_names is a list

        if self.multiple_file_names != [] and len(set(selected_file_names)&set(self.multiple_file_names)) > 0:
            QMessageBox.critical(self, 'Error', "有檔案已經選過惹", QMessageBox.Yes | QMessageBox.Yes)
        else:
            self.multiple_file_names += selected_file_names
            self.__initialize_model()
            self.__arrange_table()

    def __initialize_model(self):
        self.model = QStandardItemModel(len(self.multiple_file_names), 1)
        self.model.setHorizontalHeaderLabels(["載入檔案"])
        
    def __arrange_table(self) -> None:
        self.__initialize_model()
        for i in range(len(self.multiple_file_names)):
            self.model.setItem(i, 0, QStandardItem(self.multiple_file_names[i]))
        self.tableView.setModel(self.model)

    def __move_up(self) -> None:
        indexes = self.tableView.selectionModel().selection().indexes()
        if len(indexes) > 0:
            index = indexes[0].row()
            next_index = len(self.multiple_file_names)-1 if index==0 else index-1
            # swap
            if(index == 0): 
                self.multiple_file_names = self.multiple_file_names[1:] + [self.multiple_file_names[0]]
            else:
                self.multiple_file_names[index], self.multiple_file_names[next_index] = self.multiple_file_names[next_index], self.multiple_file_names[index]
            self.__arrange_table()
            self.tableView.selectionModel().setCurrentIndex(self.tableView.model().index(next_index, 0), QItemSelectionModel.SelectCurrent)

    def __move_down(self) -> None:
        indexes = self.tableView.selectionModel().selection().indexes()
        if len(indexes) > 0:
            index = indexes[0].row()
            next_index = 0 if index==len(self.multiple_file_names)-1 else index+1
            # swap
            if(index == len(self.multiple_file_names)-1): 
                self.multiple_file_names = [self.multiple_file_names[-1]] + self.multiple_file_names[:-1]
            else:
                self.multiple_file_names[index], self.multiple_file_names[next_index] = self.multiple_file_names[next_index], self.multiple_file_names[index]
            self.__arrange_table()
            self.tableView.selectionModel().setCurrentIndex(self.tableView.model().index(next_index, 0), QItemSelectionModel.SelectCurrent)

    def __delete_one_file(self) -> None:
        indexes = self.tableView.selectionModel().selection().indexes()
        if len(indexes) > 0:
            index = indexes[0].row()
            self.multiple_file_names.pop(index)
            self.__arrange_table()

    def __delete_all_files(self) -> None:
        self.multiple_file_names = []
        self.__initialize_model()
        self.__arrange_table()

    def __merge_file(self) -> None:
        try:
            if not self.save_merge_file_name_input.text():
                raise Exception("輸入合併的檔案名稱為空!")
            if self.multiple_file_names == []:
                raise Exception("沒有任何要合併的檔案")

            # create "smaller_MTS_data" folder in "input" folder
            input_path_name = os.path.join(self.current_dir, "input")
            if "smaller_MTS_data" not in os.listdir(input_path_name):
                os.mkdir(f"{input_path_name}/smaller_MTS_data")

            # create "merged_txt_files" folder in "smaller_MTS_data" folder
            smaller_MTS_data_path_name = os.path.join(input_path_name, "smaller_MTS_data")
            if "merged_txt_files" not in os.listdir(smaller_MTS_data_path_name):
                os.mkdir(f"{smaller_MTS_data_path_name}/merged_txt_files")
            
            with open(f"{smaller_MTS_data_path_name}/merged_txt_files/{self.save_merge_file_name_input.text()}.txt", "w") as writefile:
                for i, fname in enumerate(self.multiple_file_names):
                    with open(fname, 'r', encoding="utf-8") as readfile:
                        writefile.write(readfile.read())
                    # add segment point --> "END"
                    if i == len(self.multiple_file_names)-1:
                        writefile.write("END")
                    else:
                        writefile.write("END\n")
            self.__show_message_box(text="Success")
        except Exception as e:
            logging.error("Catch an exception.", exc_info=True)
            QMessageBox.critical(self, 'Error', str(e), QMessageBox.Yes | QMessageBox.Yes)


    # ================================ PROCESS DATA ===================================
    def __get_datas(self) -> Dict:
        ratio_type, exNum = self.__get_ratio_type_and_exNum_from_input()
        payload = {
            "area": self.__get_area(),
            "ratio_type": ratio_type,
            "exNum": exNum
        }
        dataManager = DataManager(input_file_name=self.input_file_name, MTS_type=self.MTS_type.currentText())
        return dataManager.get_datas(payload)

    def __get_ratio_type_and_exNum_from_input(self) -> Tuple:
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

    def __get_area(self) -> Union[float, int]:
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

    def __read_input_file(self) -> None:
        self.input_file_name, filetype = QFileDialog.getOpenFileName(
            self, 
            "選取檔案", 
            os.path.join(self.current_dir, "input"), 
            "txt file(*.txt)",
        )
        self.path_txt.setText(self.input_file_name)

    def __change_row(self) -> None:
        self.ratio_widget.setRowCount(self.ratio_num_spinbox.value())

    def __show_message_box(self, text) -> None:
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(text)
        msgBox.setWindowTitle("Congratulation")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    def __finish(self, path: Dict) -> None:
        # show message box
        self.__show_message_box(text="Success")

        # put the figures on the canvas
        layout_Figure(path["bigger_figure_path"], self.graphicsView_all)
        layout_Figure(path["avg_max_stress_figure_path"], self.graphicsView_comp)
        layout_Figure(path["avg_max_em_figure_path"], self.graphicsView_em)

        # enable plot button
        self.plot_btn.setEnabled(True)

    def __update_progressbar(self, value: int) -> None:
        self.progressBar.setValue(value)

    def plot(self) -> None:
        try:
            # validate input file path
            if not self.input_file_name:
                raise Exception("輸入資料路徑為空!")

            # process datas
            datas = self.__get_datas()

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
            self.plotWorker.trigger.connect(self.__update_progressbar)
            self.plotWorker.finish.connect(self.__finish)

        except Exception as e:
            logging.error("Catch an exception.", exc_info=True)
            QMessageBox.critical(self, 'Error', str(e), QMessageBox.Yes | QMessageBox.Yes)
