import pandas as pd


def select_by_pref_cd(pref_cd: list, df_station: pd.DataFrame, df_line=None, df_join=None, df_company=None) -> dict:
    delete_index = [i for i, pc in enumerate(
        df_station['pref_cd']) if pc not in pref_cd]
    df_tmp = df_station.drop(delete_index).reset_index(drop=True)
    line_cd = list(set(df_tmp['line_cd']))
    line_cd.sort()
    delete_index = [i for i, lc in enumerate(
        df_station['line_cd']) if lc not in line_cd]
    df_station = df_station.drop(delete_index).reset_index(drop=True)
    result = {'station': df_station}

    if type(df_line) == pd.DataFrame:
        delete_index = [i for i, lc in enumerate(
            df_line['line_cd']) if lc not in line_cd]
        df_line = df_line.drop(delete_index).reset_index(drop=True)
        result['line'] = df_line

    if type(df_join) == pd.DataFrame:
        delete_index = [i for i, lc in enumerate(
            df_join['line_cd']) if lc not in line_cd]
        df_join = df_join.drop(delete_index).reset_index(drop=True)
        result['join'] = df_join

    if type(df_company) == pd.DataFrame:
        company_cd = list(set(df_line['company_cd']))
        delete_index = [i for i, lc in enumerate(
            df_company['company_cd']) if lc not in company_cd]
        df_company = df_company.drop(delete_index).reset_index(drop=True)
        result['company'] = df_company

    return result


def create_conversion_dict(df: pd.DataFrame, tag):
    tag_list = ['station', 'line', 'company', 'pref']
    if not tag in tag_list:
        raise ValueError(f'wrong tag values, please select from {tag_list}')

    else:
        code_to_name = {}
        for i in df.index:
            code_to_name[df[f'{tag}_cd'][i]] = df[f'{tag}_name'][i]

        return code_to_name


def change_name_to_name(dict_in_list: list, pre_name: str, post_name: str, key: str):
    key_list = ['company', 'line']
    if not key in key_list:
        raise ValueError(f'wrong key values, please select from {key_list}')
    else:
        tmp = [dl for dl in dict_in_list if dl[key] == pre_name]
        for t in tmp:
            t[key] = post_name

        return dict_in_list


def get_pref_cd(df_pref: pd.DataFrame, df_station: pd.DataFrame, station_cd):

    if type(station_cd) == list:
        return [df_station[df_station['station_cd'] == sc]['pref_cd'].values[0] for sc in station_cd]

    pref_cd = df_station[df_station['station_cd']
                         == station_cd]['pref_cd'].values[0]
    return pref_cd


def get_first_and_last_pref_cd(df_pref: pd.DataFrame, df_station: pd.DataFrame, first_station_cd, last_station_cd):
    first_station_pref_cd = get_pref_cd(
        df_pref, df_station, first_station_cd)
    last_station_pref_cd = get_pref_cd(
        df_pref, df_station, last_station_cd)

    return first_station_pref_cd, last_station_pref_cd
