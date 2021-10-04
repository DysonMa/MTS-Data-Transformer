import os
from PIL import Image
from PyQt5.QtGui import (
    QPixmap,
)
from PyQt5.QtWidgets import (
    QLabel,
    QGraphicsScene,
    QMessageBox,
)
from DataManager import DataManager
from Validator import Validator
from scipy.sparse import data
from Utilities import (
    linear_regression,
    get_file_path,
    get_folder_path,
)
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


class PlotManager():
    def __init__(self, window):
        self.w = window
        self.validator = Validator(self.w)
        self.Initial_layout_Figure()

    # 放預設預覽圖
    def Initial_layout_Figure(self):
        text_list = [
            "Stress-Strain Figure",
            "Compressive Strength Figure",
            "Elastic Modulus Figure"
        ]

        graphic_view_list = [
            self.w.graphicsView_all,
            self.w.graphicsView_comp,
            self.w.graphicsView_em,
        ]

        for i in range(len(text_list)):
            text_label = QLabel()
            text_label.setText(text_list[i])
            text_label.setStyleSheet(
                "QLabel{color:rgb(0,0,0,255);background-color:rgb(255,255,255,255);font-size:30px;font-weight:normal;font-family:Arial;}")
            text_label.setScaledContents(True)
            scene = QGraphicsScene()
            scene.addWidget(text_label)
            graphic_view_list[i].setScene(scene)

    # 放預覽圖
    def layout_Figure(self, figure_name, graphicsView, scale=[1, 1]):
        img = Image.open(figure_name)

        label = QLabel()
        scene = QGraphicsScene()

        label.setFixedWidth(img.size[0]*scale[0])
        label.setFixedHeight(img.size[1]*scale[1])
        label.setPixmap(QPixmap(figure_name))
        label.setScaledContents(True)

        scene.addWidget(label)
        graphicsView.setScene(scene)

    def ax_plot(self, ax, kind, **kwargs):
        ax.grid(ls='-')
        ax.set_label('sine')
        xlabel = "strain"
        ylabel = "f'c(kgf/c$\mathregular{m^2}$)"
        title, specimen_name = kwargs["info"]["title"], kwargs["info"]["specimen_name"]

        if kind == "stress_strain_curve":
            strain_list, stress_list = kwargs["datas"]["strain_list"], kwargs["datas"]["stress_list"]

            ax.set(title=title, xlabel=xlabel, ylabel=ylabel,
                   xlim=(0, max(strain_list)*1.25))
            ax.scatter(strain_list, stress_list)
            ax.legend([specimen_name], loc='upper left')
        elif kind == "elastic_modulus":
            x, y, slope, intercept = kwargs["datas"]["x"], kwargs["datas"][
                "y"], kwargs["datas"]["slope"], kwargs["datas"]["intercept"]

            ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
            ax.plot(x, y, 'o', x, linear_regression(x, slope, intercept), 'r')
            ax.legend(
                [specimen_name, f'Elastic Modulus: {round(slope, 2)}'], loc='upper left')
        else:
            print(f"The kind {kind} is not defined!")

    def plot_bar(self, x, y, title):
        plt.figure(figsize=(5, 3))
        plot = plt.bar(x, y, align='center', alpha=0.5)
        plt.ylabel('Compressive Strength(kgf/c$\mathregular{m^2}$)')
        plt.title(title)
        self.createLabels(plot)

    def createLabels(self, data):
        for item in data:
            height = item.get_height()
            plt.text(
                item.get_x()+item.get_width()/2.,
                height*1.00,
                '%.2f' % float(height),
                ha="center",
                va="bottom",
            )

    def get_ratio_type_and_exNum_from_input(self):
        ratio_type, exNum = [], []
        for i in range(self.w.ratio_widget.rowCount()):
            if self.w.ratio_widget.item(i, 0) == None:
                QMessageBox.critical(
                    self.w,
                    'Error',
                    "配比種類沒有完整輸入!",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                )
                return
            # TODO: add ratio_type validator
            ratio_type.append(self.w.ratio_widget.item(i, 0).text())
            # TODO: add exNum validator
            exNum.append(int(self.w.ratio_widget.item(i, 1).text()))
        return (ratio_type, exNum)

    def get_area(self):
        return self.validator.validate_specimen_size_and_get_area()

    def plot(self):
        # self.validator.validate()
        self.area = self.get_area()

        dataManager = DataManager("../datas/specimen.txt")

        ratio_type, exNum = self.get_ratio_type_and_exNum_from_input()
        specimens_datas = dataManager.get_specimen_datas_json(self.area)
        ratio_type_labels = dataManager.get_ratio_type_labels(
            ratio_type,
            exNum
        )

        # set save folder path
        save_folder_name = self.w.save_file_name_input.text()
        folder_path = get_folder_path("output")
        save_folder_path = get_file_path(folder_path, save_folder_name)
        if not os.path.isdir(save_folder_path):
            os.mkdir(save_folder_path)

        # set a bigger figure
        bigger_fig, bigger_ax = plt.subplots(
            len(specimens_datas),
            2,
            figsize=(11.5, 3.3*len(specimens_datas))
        )
        plt.tight_layout(pad=3.5)

        # progressbar
        step = 100/len(specimens_datas)
        progress = 0

        # stress-strain curve & elastic modulus
        for i, specimens_data in enumerate(specimens_datas):
            strain_list, stress_list = specimens_data["info"]["strain"][
                "data"], specimens_data["info"]["stress"]["data"]

            plot_args_1 = {
                "info": {
                    "title": "Data_All",
                    "specimen_name": specimens_data["id"]
                },
                "datas": {
                    "strain_list": strain_list,
                    "stress_list": stress_list
                }
            }

            plot_args_2 = {
                "info": {
                    "title": "Data_Until_Max",
                    "specimen_name": specimens_data["id"]
                },
                "datas": {
                    "x": specimens_data["info"]["elastic_modulus"]["data"]["x"],
                    "y": specimens_data["info"]["elastic_modulus"]["data"]["y"],
                    "slope": specimens_data["info"]["elastic_modulus"]["data"]["slope"],
                    "intercept": specimens_data["info"]["elastic_modulus"]["data"]["intercept"]
                }
            }

            # stress-strain curve
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            self.ax_plot(ax1, "stress_strain_curve", **plot_args_1)
            self.ax_plot(ax2, "elastic_modulus", **plot_args_2)
            fig.savefig(
                get_file_path(
                    save_folder_path,
                    f"figure_{str(i+1)}.png"
                )
            )

            plt.clf()       # clear the entire current figure
            plt.cla()       # clear an axis
            plt.close(fig)  # close figure

            # stress-strain curve(put them into a bigger figure)
            self.ax_plot(bigger_ax[i, 0], "stress_strain_curve", **plot_args_1)
            self.ax_plot(bigger_ax[i, 1], "elastic_modulus", **plot_args_2)

            # progressbar
            progress += step
            self.w.progressBar.setValue(round(progress))

        # save bigger figure
        bigger_figure_path = get_file_path(
            save_folder_path,
            "fig_All.png"
        )
        bigger_fig.savefig(
            bigger_figure_path,
            dpi=100
        )

        # avg max compressive strength
        avg_max_stress_list = dataManager.get_avg_max_stress_per_group(
            specimens_datas,
            exNum
        )
        self.plot_bar(
            x=ratio_type,
            y=avg_max_stress_list,
            title=self.w.comp_title_input.text() or "Compressive Strength"
        )
        avg_max_stress_figure_path = get_file_path(
            save_folder_path,
            "Compressive Strength.png"
        )
        plt.savefig(
            avg_max_stress_figure_path,
            bbox_inches='tight'
        )

        # avg max elastic modulus
        avg_max_em_list = dataManager.get_avg_max_em_per_group(
            specimens_datas,
            exNum
        )
        self.plot_bar(
            x=ratio_type,
            y=avg_max_em_list,
            title=self.w.em_title_input.text() or "Elastic modulus"
        )
        avg_max_em_figure_path = get_file_path(
            save_folder_path,
            "Elastic modulus.png"
        )
        plt.savefig(
            avg_max_em_figure_path,
            bbox_inches='tight'
        )

        # OK
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Success")
        msgBox.setWindowTitle("Congratulation")
        msgBox.setStandardButtons(QMessageBox.Ok)
        returnValue = msgBox.exec()
        if(returnValue == QMessageBox.Ok):
            self.layout_Figure(bigger_figure_path, self.w.graphicsView_all)
            self.layout_Figure(avg_max_stress_figure_path,
                               self.w.graphicsView_comp)
            self.layout_Figure(avg_max_em_figure_path, self.w.graphicsView_em)
