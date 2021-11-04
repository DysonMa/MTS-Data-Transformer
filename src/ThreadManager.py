from PyQt5.QtCore import QThread, pyqtSignal
from PlotManager import *
import matplotlib.pyplot as plt
import os
from ExcelManager import ExcelManager


class PlotWorker(QThread):
    # set signal type
    trigger = pyqtSignal(int)
    finish = pyqtSignal(dict)

    def __init__(self, datas: Dict) -> None:
        super().__init__()
        self.datas = datas

    def run(self) -> None:
        # set a bigger figure
        bigger_fig, bigger_ax = plt.subplots(
            nrows=len(self.datas["specimens_datas"]),
            ncols=2,
            figsize=(11.5, 3.3*len(self.datas["specimens_datas"])),
            squeeze=False if len(
                self.datas["specimens_datas"]) == 1 else True  # one row!!
        )
        plt.tight_layout(pad=3.5)

        # progressbar
        step = 100/len(self.datas["specimens_datas"])
        progress = 0

        # stress-strain curve & elastic modulus
        for i, specimens_data in enumerate(self.datas["specimens_datas"]):

            plot_args_1 = get_plot_args_1(specimens_data)
            plot_args_2 = get_plot_args_2(specimens_data)

            # stress-strain curve
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            ax_plot(ax1, "stress_strain_curve", **plot_args_1)
            ax_plot(ax2, "elastic_modulus", **plot_args_2)
            fig.savefig(
                os.path.join(self.datas["save_folder_path"],
                             f"figure_{str(i+1)}.png")
            )

            plt.clf()       # clear the entire current figure
            plt.cla()       # clear an axis
            plt.close(fig)  # close figure

            # stress-strain curve(put them into a bigger figure)
            ax_plot(bigger_ax[i, 0], "stress_strain_curve", **plot_args_1)
            ax_plot(bigger_ax[i, 1], "elastic_modulus", **plot_args_2)

            # progressbar
            progress += step
            self.trigger.emit(round(progress))

        # save bigger figure
        bigger_figure_path = os.path.join(
            self.datas["save_folder_path"], "fig_All.png")
        bigger_fig.savefig(bigger_figure_path, dpi=100)

        # avg max compressive strength
        plot_bar(
            x=self.datas["ratio_type"],
            y=self.datas["avg_max_stress_list"],
            title=self.datas["comp_title"] or "Compressive Strength"
        )
        avg_max_stress_figure_path = os.path.join(
            self.datas["save_folder_path"], "Compressive Strength.png")
        plt.savefig(
            avg_max_stress_figure_path,
            bbox_inches='tight'
        )

        # avg max elastic modulus
        plot_bar(
            x=self.datas["ratio_type"],
            y=self.datas["avg_max_em_list"],
            title=self.datas["em_title"] or "Elastic modulus"
        )
        avg_max_em_figure_path = os.path.join(
            self.datas["save_folder_path"], "Elastic modulus.png")
        plt.savefig(
            avg_max_em_figure_path,
            bbox_inches='tight'
        )

        # export to Excel
        ExcelManager(datas=self.datas, export_name="datas.xlsx").export()

        self.finish.emit({
            "bigger_figure_path": bigger_figure_path,
            "avg_max_stress_figure_path": avg_max_stress_figure_path,
            "avg_max_em_figure_path": avg_max_em_figure_path
        })
