import numpy as np
from Utilities import linear_regression
from scipy.optimize import curve_fit
from typing import List, Tuple
from shutil import copyfile
import os


class DataManager:
    def __init__(self, input_file_name: str, MTS_type: str) -> None:
        self.input_file_name = input_file_name   # full filepath name
        self.MTS_type = MTS_type # 大台MTS | 小台MTS

    def __read_input_file(self) -> List:
        # bigger MTS
        if self.MTS_type == "大台MTS":
            with open(self.input_file_name, 'r', encoding="utf-8") as f:
                specimens = f.read().split('\n\n')
                specimens.pop(0)
        # smaller MTS
        elif self.MTS_type == "小台MTS":
            with open(self.input_file_name, 'r', encoding="utf-8") as f:
                content = f.read().strip()
                # check if "END" seperator is in the file, which means multiple files
                if "END" in content:
                    specimens = content.split("END")
                    specimens.pop(-1)   # the last one is ""
                # single file
                else:
                    specimens = [content]
        return specimens

    def __get_each_line(self, each_specimens) -> List:
        # bigger MTS
        if self.MTS_type == "大台MTS":
            data_per_specimen = each_specimens.split("s\tmm\tN\tmm\tmm\tsegments\n")[-1]
            each_line = data_per_specimen.split('\n')
        # smaller MTS
        elif self.MTS_type == "小台MTS":
            each_line = each_specimens.strip().split("\n")
            each_line.pop(0)   # the first number in each data, e.g. 291
        return each_line

    def __extract_from_data_per_sec(self, data_per_sec) -> Tuple:
        # bigger MTS
        if self.MTS_type == "大台MTS":
            _, displacement, force, D1, D2, _ = data_per_sec.split("\t")
        # smaller MTS
        elif self.MTS_type == "小台MTS":
            displacement, force, _, D1, D2 = data_per_sec.strip().split("\t")
        return displacement, force, D1, D2

    def __get_ratio_type_labels(self, ratio_type: List, exNum: List) -> List:
        ratio_type_labels = []
        for i in range(len(ratio_type)):
            ratio_type_labels.extend([ratio_type[i]]*exNum[i])
        return ratio_type_labels

    def __get_exNum_ids(self, exNum: List) -> List:
        '''
        e.g.
        exNum: [3, 3, 3, 3, 3, 3, 3, 2] 
        exNum_ids: [0, 3, 6, 9, 12, 15, 18, 21, 23]
        '''
        initial_num = 0
        exNum_ids = [initial_num]
        for i in range(len(exNum)):
            initial_num += exNum[i]
            exNum_ids.append(initial_num)
        return exNum_ids

    def __get_specimen_datas_json(self, area: float, ratio_type: List, exNum: List) -> List:
        specimens = self.__read_input_file()
        ratio_type_labels = self.__get_ratio_type_labels(ratio_type, exNum)

        # validate numbers
        if len(ratio_type_labels) != len(specimens):
            raise Exception("資料筆數與輸入數量不符合!")

        specimens_datas = []
        for Id in range(len(specimens)):
            each_line = self.__get_each_line(specimens[Id])
            displacement_list, force_list, D1_list, D2_list, stress_list, strain_list = [], [], [], [], [], []
            for data_per_sec in each_line:
                if data_per_sec:
                    displacement, force, D1, D2 = self.__extract_from_data_per_sec(data_per_sec)
                    displacement_list.append(float(displacement))

                    strain = abs((float(D1)+float(D2))/2)/100*5.384
                    stress = float(force)/9.81/area

                    force_list.append(float(force))
                    D1_list.append(float(D1))
                    D2_list.append(float(D2))
                    strain_list.append(strain)
                    stress_list.append(stress)

            x, y, slope, intercept = self.__get_curve_fitting_datas(strain_list, stress_list)

            specimens_datas.append({
                "id": Id+1,
                "name": ratio_type_labels[Id],
                "info": {
                    "displacement": {
                        "unit": "mm",
                        "data": displacement_list
                    },
                    "force": {
                        "unit": "N",
                        "data": force_list
                    },
                    "D1": {
                        "unit": "mm",
                        "data": D1_list
                    },
                    "D2": {
                        "unit": "mm",
                        "data": D2_list
                    },
                    "strain": {
                        "unit": "none",
                        "data": strain_list
                    },
                    "stress": {
                        "unit": "kgf/cm^2",
                        "data": stress_list
                    },
                    "elastic_modulus": {
                        "unit": "kgf/cm^2",
                        "data": {
                            "x": x,
                            "y": y,
                            "slope": slope,
                            "intercept": intercept
                        }
                    }
                }
            })
        return specimens_datas

    def __get_curve_fitting_datas(self, strain_list: List, stress_list: List) -> Tuple:
        lower_point = min(strain_list, key=lambda x: abs(x-0.00005))
        lower_point_index = strain_list.index(lower_point)
        upper_point = min(stress_list, key=lambda x: abs(x-max(stress_list)*0.45))
        upper_point_index = stress_list.index(upper_point)

        x = np.array(strain_list[lower_point_index:upper_point_index])
        y = np.array(stress_list[lower_point_index:upper_point_index])

        (slope, intercept), _ = curve_fit(linear_regression, x, y)

        return x, y, slope, intercept

    def __get_max_stress_list(self, specimens_datas: List) -> List:
        max_stress_list = []
        for specimens_data in specimens_datas:
            max_stress = max(specimens_data["info"]["stress"]["data"])
            max_stress_list.append(max_stress)
        return max_stress_list

    def __get_max_em_list(self, specimens_datas: List) -> List:
        max_em_list = []
        for specimens_data in specimens_datas:
            max_em = specimens_data["info"]["elastic_modulus"]["data"]["slope"]
            max_em_list.append(max_em)
        return max_em_list

    def __get_avg_max_stress_per_group(self, specimens_datas: List, exNum: List) -> List:
        max_stress_list = self.__get_max_stress_list(specimens_datas)
        exNum_ids = self.__get_exNum_ids(exNum)
        avg_max_stress_list = []
        for i in range(1, len(exNum_ids)):
            start_id = exNum_ids[i-1]
            end_id = exNum_ids[i]
            avg_max_stress_list.append(sum(max_stress_list[start_id:end_id])/(end_id - start_id))
        return avg_max_stress_list

    def __get_avg_max_em_per_group(self, specimens_datas: List, exNum: List) -> List:
        max_em_list = self.__get_max_em_list(specimens_datas)
        exNum_ids = self.__get_exNum_ids(exNum)
        avg_em_list = []
        for i in range(1, len(exNum_ids)):
            start_id = exNum_ids[i-1]
            end_id = exNum_ids[i]
            avg_em_list.append(sum(max_em_list[start_id:end_id])/(end_id - start_id))
        return avg_em_list

   # public method
    def get_datas(self, payload):
        specimens_datas = self.__get_specimen_datas_json(payload["area"], payload["ratio_type"], payload["exNum"])
        exNum_ids = self.__get_exNum_ids(payload["exNum"])
        max_stress_list = self.__get_max_stress_list(specimens_datas)
        avg_max_stress_list = self.__get_avg_max_stress_per_group(specimens_datas, payload["exNum"])
        max_em_list = self.__get_max_em_list(specimens_datas)
        avg_max_em_list = self.__get_avg_max_em_per_group(specimens_datas, payload["exNum"])
        return {
            "specimens_datas": specimens_datas,
            "ratio_type": payload["ratio_type"],
            "exNum": payload["exNum"],
            "exNum_ids": exNum_ids,
            "max_stress_list": max_stress_list,
            "avg_max_stress_list": avg_max_stress_list,
            "max_em_list": max_em_list,
            "avg_max_em_list": avg_max_em_list
        }


if __name__ == "__main__":
    dm = DataManager("input/1029-1.txt")  # 1029-1
    datas = dm.get_datas(payload={
        "area": np.pi/4*10**2,
        "ratio_type": ["a"],
        "exNum": [1]
    })
    print(datas)
