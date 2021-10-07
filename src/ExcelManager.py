import json
from datetime import datetime
from Utilities import get_file_path
from openpyxl import (
    load_workbook,
    Workbook,
    drawing
)


class ExcelManager:
    def __init__(self, save_folder_path, export_name, ratio_type, avg_max_stress_list, avg_max_em_list, specimens_datas):
        # self.setting_file = setting_file
        # self.config = {}
        # with open(setting_file, "r") as f:
        #     self.config = json.load(f)
        self.save_folder_path = save_folder_path
        self.export_name = export_name
        self.ratio_type = ratio_type
        self.avg_max_stress_list = avg_max_stress_list
        self.avg_max_em_list = avg_max_em_list
        self.specimens_datas = specimens_datas
        # self.ws1_title = self.config["ws1_title"]
        # self.ws2_title = self.config["ws2_title"]
        # self.titles = self.config["title"]

    def export(self):
        wb = Workbook()
        wb.remove_sheet(wb["Sheet"])

        # TODO
        # overall datas
        wb.create_sheet("overall")
        ws = wb["overall"]
        ws.append(("Date: ", datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
        # compressive stress
        ws.append(
            ("Average Compressive Stress [f'c(kgf/cm2)]",))
        ws.append(tuple(self.ratio_type))
        ws.append(tuple(self.avg_max_stress_list))
        # elastic modulus
        ws.append(
            ("Average Elastic Modulus [f'c(kgf/cm2)]",))
        ws.append(tuple(self.ratio_type))
        ws.append(tuple(self.avg_max_em_list))

        # detail datas for each specimen
        for data in self.specimens_datas:

            Id = data["id"]
            name = data["name"]

            wb.create_sheet(name)
            ws = wb[name]
            ws.append(("id", Id))
            ws.append(("name", name))
            ws.append(tuple(data["info"].keys()))

            for dis, force, d1, d2, strain, stress in zip(
                data["info"]["displacement"]["data"],
                data["info"]["force"]["data"],
                data["info"]["D1"]["data"],
                data["info"]["D2"]["data"],
                data["info"]["strain"]["data"],
                data["info"]["stress"]["data"],
            ):
                ws.append((dis, force, d1, d2, strain, stress))

            ws["G4"] = data["info"]["elastic_modulus"]["data"]["slope"]

            img = drawing.image.Image(
                get_file_path(
                    self.save_folder_path,
                    f"figure_{str(Id)}.png"
                )
            )
            img.anchor = 'K5'
            ws.add_image(img)

        wb.save(
            get_file_path(
                self.save_folder_path,
                self.export_name
            )
        )
