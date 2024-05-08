import pandas as pd
import io
import msoffcrypto
import re
from datetime import datetime
import psycopg2
from psycopg2 import Error
from sqlalchemy.exc import IntegrityError  # Import IntegrityError from SQLAlchemy
from sqlalchemy import create_engine
from datetime import timedelta
import subprocess
import time



def Realizirano():
    batch_script_path = "C:/Users/ivan.tonkic/Desktop/Mega_metal/fix_plan/invoices.py"
    python_interpreter_path = "C:/Users/ivan.tonkic/AppData/Local/Programs/Python/Python312-32/python.exe"
    # Run the batch script

    filtered_df = pd.DataFrame()
    #subprocess.run([python_interpreter_path ,batch_script_path])

    result = subprocess.run([python_interpreter_path, batch_script_path], capture_output=True, text=True)
    print(result.returncode)
    if result.returncode == 0:
        # Process the output
        output_lines = result.stdout.splitlines()
        column_names = output_lines[0].split(',')
        column_names.extend(['new_column1', 'new_column2','new_column11', 'new_column22'])
        # Remove the first row (column names) from the data
        data = [line.split(';') for line in output_lines[1:]]  # Assuming CSV-like data, adjust delimiter as needed
        # Create DataFrame
        df = pd.DataFrame(data, columns=column_names)
    else:
        print("Error occurred while running the script.")

    df.columns = df.columns.str.strip("[]").str.strip("'").str.strip()
    df.columns = df.columns.str.replace("'", "").str.strip()


    def convert_to_float(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0

    # Apply the conversion function to the 'Endpreis' column and assign it to 'Unnamed: 11'
    filtered_df['Unnamed: 11'] = df['Einzelpreis'].apply(convert_to_float)


    print(df.columns)
    print(df[ "Endpreis"])
    filtered_df['Unnamed: 7']=df[ "Kd-KommNr"]
    #filtered_df['Unnamed: 11']=df[ "Endpreis"].astype(float)
    filtered_df['Unnamed: 18']=df[ "BelDatum"]
    df["PosGewicht"] = pd.to_numeric(df["PosGewicht"], errors='coerce')
    df["Menge"] = pd.to_numeric(df["Menge"], errors='coerce')
    print((df[ "Kd-KommNr"]))
    # Now perform multiplication
    filtered_df['Unnamed: 78'] = df["PosGewicht"] * df["Menge"]
    filtered_df['Unnamed: 78']=df["PosGewicht"]*df["Menge"]



    print(filtered_df['Unnamed: 18'])
    df.to_excel("ASD.xlsx", index=False)

    print("PROSLO")
        

    # PostgreSQL connection parameters''
    db_host = "192.168.100.216"
    db_port = "5432"
    db_name = "megametal"
    db_user = "postgres"
    db_password = "postgresql"
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    connection = psycopg2.connect(host=db_host, port=db_port, database=db_name, user=db_user, password=db_password)
    cursor = connection.cursor()

    conn = psycopg2.connect(
        host="192.168.100.216",
        database="megametal",
        user="postgres",
        password="postgresql"
    )

    # SQL statement for insertion
    insert_query = """INSERT INTO public."TREZ_KALK"(
                        "Ident", "Id_rn", "Bruto", "Debljina", "Kvaliteta")
                        VALUES (%s, %s, %s, %s, %s);"""


    def get_week_number(date_str):
        # Convert the date string to a datetime object
        try:
            date_object = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        except:
            date_object = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        
        # Get the ISO week number
        week_number = date_object.isocalendar()[1]

        return week_number
    """
    decrypted_workbook = io.BytesIO()
    with open('//192.168.100.188/mm/01_Management/00_Mega Metal Transformation/5 Nabava - Prodaja/1_Prodaja/Timeline - Orders&Invoices/01_Analize/Updated_Orders_Invoices_analize_v5.xlsx', 'rb') as file:
        office_file = msoffcrypto.OfficeFile(file)
        office_file.load_key(password='mega')
        office_file.decrypt(decrypted_workbook)
    shipping_data = pd.read_excel(decrypted_workbook, sheet_name='Invoices', dtype={'BT': str}, skiprows=[1, 2, 3])  # Skip the header row and one additional row
    columns_to_extract = [7, 18,11,78]
    extracted_columns = shipping_data.iloc[:, columns_to_extract]
    extracted_df = shipping_data.iloc[:, columns_to_extract].copy()
    filtered_df = extracted_df
    """


    rows_with_zeros = filtered_df[filtered_df['Unnamed: 18'] == '00:00:00']
    for index, row in filtered_df.iterrows():
        try:
            filtered_df.at[index, 'Unnamed: 18'] = pd.to_datetime(row['Unnamed: 18'], format='%Y-%m-%d %H:%M:%S')
        except:
            filtered_df.at[index, 'Unnamed: 18'] = pd.to_datetime(row['Unnamed: 18'], format='%Y-%m-%d %H:%M:%S.%f')



    print(filtered_df['Unnamed: 11'])
    filtered_df = filtered_df[filtered_df['Unnamed: 18'] >= pd.to_datetime('2024-01-01')]
    filtered_df['Unnamed: 7'] = filtered_df['Unnamed: 7'].apply(lambda x: '-'.join([str(int(part)) if i == 2 else str(part) for i, part in enumerate(str(x).split('-'))]) if re.match(r'^\d+-\d+-\d+$', str(x)) else str(x)) # svi podatci
    filtered_df['Unnamed: 13'] = filtered_df['Unnamed: 18'].apply(lambda x: get_week_number(str(x)))

    #grouped_df_kw_invoices = filtered_df.groupby(['Unnamed: 13'])['Unnamed: 11'].sum().reset_index()# po tjednu
    grouped_df_kw_invoices = filtered_df.groupby(['Unnamed: 13']).agg({'Unnamed: 11': 'sum', 'Unnamed: 78': 'sum'}).reset_index()#po tjednu




    filtered_df['Unnamed: 18'] = pd.to_datetime(filtered_df['Unnamed: 18'])
    filtered_df['Month'] = filtered_df['Unnamed: 18'].dt.month
    #grouped_df_month_invoices = filtered_df.groupby(filtered_df['Month'])['Unnamed: 11'].sum().reset_index() #po mjesecu
    grouped_df_month_invoices = filtered_df.groupby(filtered_df['Month']).agg({'Unnamed: 11': 'sum', 'Unnamed: 78': 'sum'}).reset_index() #po mjesecu



    #grouped_df_month_invoices.rename(columns={'Unnamed: 91': 'Iznos'}, inplace=True)

    grouped_df_kw_invoices.rename(columns={'Unnamed: 13': 'Tjedan'}, inplace=True)
    grouped_df_kw_invoices.rename(columns={'Unnamed: 11': 'Iznos'}, inplace=True)
    grouped_df_month_invoices.rename(columns={'Unnamed: 11': 'Iznos'}, inplace=True)
    grouped_df_kw_invoices.rename(columns={'Unnamed: 78': 'Tezina'}, inplace=True)
    grouped_df_month_invoices.rename(columns={'Unnamed: 78': 'Tezina'}, inplace=True)
    grouped_df_kw_invoices.loc[grouped_df_kw_invoices['Iznos'] == 0, 'Tezina'] = 0
    grouped_df_month_invoices.loc[grouped_df_month_invoices['Iznos'] == 0, 'Tezina'] = 0
    for index, row in grouped_df_kw_invoices.iterrows():
        # Define the SQL UPDATE query
        print("ASDASDASD")
        print(row)
        print(int(row['Tjedan']))
        sql_query = """
            UPDATE "TBA_FIX_REAL"
            SET "IZNOS" = %(iznos)s, "TEZINA" = %(tezina)s
            WHERE "KW" = %(tjedan)s
        """
        # Execute the query
        conn.cursor().execute(sql_query, {'iznos': row['Iznos'], 'tezina': row['Tezina'], 'tjedan': int(row['Tjedan'])})
        conn.commit()

    for index, row in grouped_df_month_invoices.iterrows():
        # Define the SQL UPDATE query
        sql_query = """
            UPDATE "TBA_FIX_REAL"
            SET "IZNOS" = %(iznos)s, "TEZINA" = %(tezina)s
            WHERE "MJESEC" = %(mjesec)s
        """
        # Execute the query
        conn.cursor().execute(sql_query, {'iznos': row['Iznos'], 'tezina': row['Tezina'], 'mjesec': int(row['Month'])})
        conn.commit()
    print("bas proslo")
    with pd.ExcelWriter('Fix_plan_realizirano.xlsx') as writer:
        # Write each dataframe to a different sheet
        grouped_df_kw_invoices.to_excel(writer, sheet_name='KW', index=False)
        grouped_df_month_invoices.to_excel(writer, sheet_name='Month', index=False)

if __name__ == '__main__':
    Realizirano()

