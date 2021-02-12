import pickle
import numpy as np
import pandas as pd


class LineStationInfo:

    def __init__(self, company_code_to_name: dict, line_code_to_name: dict, station_code_to_name: dict, pref_code_to_name: dict, ):
        self.line_station_info = []
        self.company_code_to_name = company_code_to_name
        self.line_code_to_name = line_code_to_name
        self.station_code_to_name = station_code_to_name
        self.pref_code_to_name = pref_code_to_name

    def covert_code_to_name(self, code, code_to_name_dict: dict):
        if type(code) in [int, np.int64]:
            name = code_to_name_dict[code]

        else:
            print(type(code))
            raise TypeError("worng code type")

        return name

    def remove_bracket(self, text: str):
        bracket_patterns = ['(', '（', '〈']

        for bp in bracket_patterns:
            text = text.split(bp)[0]

        return text

    def add_station_info(self, company_cd, line_cd, line_type, first_station_cd, last_station_cd, first_station_pref_cd, last_station_pref_cd):

        company_name = self.covert_code_to_name(
            company_cd, self.company_code_to_name)
        line_name = self.covert_code_to_name(line_cd, self.line_code_to_name)
        first_station_name = self.covert_code_to_name(
            first_station_cd, self.station_code_to_name)
        last_station_name = self.covert_code_to_name(
            last_station_cd, self.station_code_to_name)
        first_station_pref = self.covert_code_to_name(
            first_station_pref_cd, self.pref_code_to_name)
        last_station_pref = self.covert_code_to_name(
            last_station_pref_cd, self.pref_code_to_name)

        # Remove '(xxx)'
        line_name = self.remove_bracket(line_name)
        first_station_name = self.remove_bracket(first_station_name)
        last_station_name = self.remove_bracket(last_station_name)

        # # Covert 'JR東日本' and 'JR東海' to 'JR'
        # if company_name == 'JR東日本' or company_name == 'JR東海':
        #     company_name = 'JR'

        self.line_station_info.append({
            'company_name': company_name,
            'company_code': company_cd,
            'line_name': line_name,
            'line_code': line_cd,
            'line_type': line_type,
            'first_station': first_station_name,
            'last_station': last_station_name,
            'first_station_pref': first_station_pref,
            'last_station_pref': last_station_pref
        })

    def save_info(self, path: str):
        df = pd.DataFrame(self.line_station_info)
        df.to_csv(path, index=False)
        # with open(path, 'wb') as f:
        #     pickle.dump(self.line_station_info, f)
