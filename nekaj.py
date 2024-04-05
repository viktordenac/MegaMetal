import datetime

import pandas as pd
import openpyxl


today = datetime.datetime.now()

godina = today.strftime('%Y')
mjesec = today.strftime('%m')
dan = today.strftime('%d')
print(dan)
try:
    dfs = pd.read_excel("//192.168.100.216/Users/ivan.tonkic/Desktop/Share/Verzugs_liste/Verzugs_lista_"+ dan + "-" + mjesec + "-" + godina + ".xlsx", sheet_name=None)
    sheet_names = list(dfs.keys())
    data = {sheet_name: df.values.tolist() for sheet_name, df in dfs.items()}
    print(data)

except Exception as e:
    print(e)