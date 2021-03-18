import pandas as pd


def create_files():
    xl = pd.ExcelFile('data.xlsx', engine='xlrd')
    sheet = xl.parse(0)
    start = []
    end = []
    flag = 1
    for i in range(0, len(sheet.index)):
        if type(sheet.iloc[i][0]) == str:
            if sheet.iloc[i][0].split()[0] == 'Расчетный':
                if len(start) == 0:
                    start.append(i)
                    flag = 1
                elif flag:
                    start.append(i)
                    flag = 0
                    end.append(i)
                else:
                    end.append(i)
                    flag = 1
                    start.append(i)
    end.append(len(sheet.index))

    for i in range(len(end)):
        data = []
        for j in range(start[i], end[i]):
            data.append(j)
        name = sheet.loc[data].iloc[3][0][10:]
        excel = sheet.loc[data]
        excel.columns = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']
        excel.to_excel(f'files/{name}.xlsx', index=False)