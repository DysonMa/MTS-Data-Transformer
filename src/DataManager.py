import numpy as np
from Utilities import linear_regression
from scipy.optimize import curve_fit


class DataManager():
    def __init__(self, input_fileName):
        self.input_fileName = input_fileName

    def read_input_file(self):
        with open(self.input_fileName, 'r', encoding="utf-8") as f:
            specimens = f.read().split('\n\n')
            specimens.pop(0)
            return specimens

    def get_ratio_type_labels(self, ratio_type, exNum):
        ratio_type_labels = []
        for i in range(len(ratio_type)):
            ratio_type_labels.extend([ratio_type[i]]*exNum[i])
        return ratio_type_labels

    def get_exNum_ids(self, exNum):
        '''
        exNum: [3, 3, 3, 3, 3, 3, 3, 2] 
        exNum_ids: [0, 3, 6, 9, 12, 15, 18, 21, 23]
        '''
        initial_num = 0
        exNum_ids = [initial_num]
        for i in range(len(exNum)):
            initial_num += exNum[i]
            exNum_ids.append(initial_num)
        return exNum_ids

    def get_specimen_datas_json(self, area):
        specimens = self.read_input_file()
        self.specimens_num = len(specimens)
        if not self.specimens_num:
            print("Error")
        specimens_datas = []
        for Id in range(self.specimens_num):
            data_per_specimen = specimens[Id].split(
                "Sec\tmm\tN\tmm\tmm\tsegments\n"
            )[-1]
            each_line = data_per_specimen.split('\n')
            displacement_list, force_list, D1_list, D2_list, stress_list, strain_list = [
            ], [], [], [], [], []
            for data_per_sec in each_line:
                if data_per_sec:
                    _, displacement, force, D1, D2, _ = data_per_sec.split(
                        "\t")
                    displacement_list.append(displacement)

                    strain = abs((float(D1)+float(D2))/2)/100*5.384
                    stress = float(force)/9.81/area

                    force_list.append(force)
                    D1_list.append(D1)
                    D2_list.append(D2)
                    strain_list.append(strain)
                    stress_list.append(stress)

            x, y, slope, intercept = self.get_curve_fitting_datas(
                strain_list, stress_list)

            specimens_datas.append({
                "id": Id+1,
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

    def get_curve_fitting_datas(self, strain_list, stress_list):
        lower_point = min(strain_list,
                          key=lambda x: abs(x-0.00005))
        lower_point_index = strain_list.index(lower_point)
        upper_point = min(stress_list,
                          key=lambda x: abs(x-max(stress_list)*0.45))
        upper_point_index = stress_list.index(upper_point)

        x = np.array(strain_list[lower_point_index:upper_point_index])
        y = np.array(stress_list[lower_point_index:upper_point_index])

        (slope, intercept), _ = curve_fit(linear_regression, x, y)

        return x, y, slope, intercept

    def get_max_stress_list(self, specimens_datas):
        max_stress_list = []
        for i, specimens_data in enumerate(specimens_datas):
            max_stress = max(specimens_data["info"]["stress"]["data"])
            max_stress_list.append(max_stress)
        return max_stress_list

    def get_max_em_list(self, specimens_datas):
        max_em_list = []
        for i, specimens_data in enumerate(specimens_datas):
            max_em = specimens_data["info"]["elastic_modulus"]["data"]["slope"]
            max_em_list.append(max_em)
        return max_em_list

    def get_avg_max_stress_per_group(self, specimens_datas, exNum):
        max_stress_list = self.get_max_stress_list(specimens_datas)
        exNum_ids = self.get_exNum_ids(exNum)
        avg_max_stress_list = []
        for i in range(1, len(exNum_ids)):
            start_id = exNum_ids[i-1]
            end_id = exNum_ids[i]
            avg_max_stress_list.append(
                sum(max_stress_list[start_id:end_id])/(end_id - start_id)
            )
        return avg_max_stress_list

    def get_avg_max_em_per_group(self, specimens_datas, exNum):
        max_em_list = self.get_max_em_list(specimens_datas)
        exNum_ids = self.get_exNum_ids(exNum)
        avg_em_list = []
        for i in range(1, len(exNum_ids)):
            start_id = exNum_ids[i-1]
            end_id = exNum_ids[i]
            avg_em_list.append(
                sum(max_em_list[start_id:end_id])/(end_id - start_id)
            )
        return avg_em_list
