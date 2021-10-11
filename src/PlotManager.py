from typing import Dict, List
# import pandas as pd
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PIL import Image
from PyQt5.QtGui import (
    QPixmap,
)
from PyQt5.QtWidgets import (
    QLabel,
    QGraphicsScene,
    QWidget,
)
from Utilities import (
    linear_regression,
)
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


def Initial_layout_Figure(window) -> None:
    text_list = [
        "Stress-Strain Figure",
        "Compressive Strength Figure",
        "Elastic Modulus Figure"
    ]

    graphic_view_list = [
        window.graphicsView_all,
        window.graphicsView_comp,
        window.graphicsView_em,
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


def layout_Figure(figure_name: str, graphicsView: QWidget, scale=[1, 1]) -> None:
    img = Image.open(figure_name)

    label = QLabel()
    scene = QGraphicsScene()

    label.setFixedWidth(img.size[0]*scale[0])
    label.setFixedHeight(img.size[1]*scale[1])
    label.setPixmap(QPixmap(figure_name))
    label.setScaledContents(True)

    scene.addWidget(label)
    graphicsView.setScene(scene)


def ax_plot(ax, kind: str, **kwargs: Dict) -> None:
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


def plot_bar(x: List, y: List, title: str) -> None:
    plt.figure(figsize=(5, 3))
    plot = plt.bar(x, y, align='center', alpha=0.5)
    plt.ylabel('kgf/c$\mathregular{m^2}$')
    plt.title(title)
    # create labels
    for item in plot:
        height = item.get_height()
        plt.text(
            item.get_x()+item.get_width()/2.,
            height*1.00,
            '%.2f' % float(height),
            ha="center",
            va="bottom",
        )


def get_plot_args_1(specimens_data: List) -> Dict:
    return {
        "info": {
            "title": "Data_All",
            "specimen_name": specimens_data["name"]
        },
        "datas": {
            "strain_list": specimens_data["info"]["strain"][
                "data"],
            "stress_list": specimens_data["info"]["stress"]["data"]
        }
    }


def get_plot_args_2(specimens_data: List) -> Dict:
    return {
        "info": {
            "title": "Data_Until_Max",
            "specimen_name": specimens_data["name"]
        },
        "datas": {
            "x": specimens_data["info"]["elastic_modulus"]["data"]["x"],
            "y": specimens_data["info"]["elastic_modulus"]["data"]["y"],
            "slope": specimens_data["info"]["elastic_modulus"]["data"]["slope"],
            "intercept": specimens_data["info"]["elastic_modulus"]["data"]["intercept"]
        }
    }
