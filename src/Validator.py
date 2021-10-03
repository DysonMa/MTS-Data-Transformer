from PyQt5.QtWidgets import (
    QMessageBox,

)
import numpy as np


class Validator():
    def __init__(self, window):
        self.w = window

    # 判斷是否有選擇text檔案
    def validate_input_file(self):
        if self.w.PathTxt.toPlainText() == "":
            QMessageBox.critical(self.w, 'Error', "沒有選檔案!",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return

    #判斷是否有勾選cube or cylinder
    def validate_specimen_size_and_get_area(self):
        if self.w.Cylinder.isChecked():
            area = np.pi/4*10**2
        elif self.w.Cube.isChecked():
            area = 5**2
        else:
            QMessageBox.critical(self.w, 'Error', "沒有選試體尺寸!",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        return area

    # 判斷是否有輸入配比數量

    def validate_ratio_type_number(self):
        if self.w.inputWidget.rowCount() == 0:
            QMessageBox.critical(self.w, 'Error', "沒有輸入配比數量!",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
    # 判斷是否有選擇存檔路徑

    def validate_save_folder_path(self):
        if self.w.savePathTxt.toPlainText() == "":
            QMessageBox.critical(self.w, 'Error', "沒有選存檔路徑!",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return

    # 判斷是否有輸入存檔檔名
    def validate_save_file_name(self):
        if self.w.saveFileName.text() == "":
            QMessageBox.critical(self.w, 'Error', "沒有輸入存檔名稱!",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return

    def validate(self):
        self.validate_input_file()
        # self.validate_specimen_size()
        self.validate_ratio_type_number()
        self.validate_save_folder_path()
        self.validate_save_file_name()
