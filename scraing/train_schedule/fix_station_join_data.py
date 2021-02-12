import pandas as pd

join_path = '~/share/data/station/join20200619.csv'
df_join = pd.read_csv(join_path)

# 99425:あいの風とやま鉄道線
line_cd = 99425

df_join_tmp = df_join[df_join['line_cd'] == line_cd]
symmetric_difference_station_cd = set(
    df_join_tmp['station_cd1']) ^ set(df_join_tmp['station_cd2'])

if len(symmetric_difference_station_cd) == 4:
    df_join = df_join.append(
        {'line_cd': 99425, 'station_cd1': 1140509, 'station_cd2': 1140510}, ignore_index=True)
    fix_join_path = '~/share/data/station/join20200619_fix.csv'
    df_join.to_csv(fix_join_path, index=False)
