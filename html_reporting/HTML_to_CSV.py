import pandas as pd
from io import StringIO

tables = []
path = "rpt026.html"
with open(path, "r", encoding = "ISO-8859-1") as f:
    content = f.read()
chunks = content.split("\n -------------------------------------------------------------------------------------------------------------------------------------")

custom_headers = ["Date", "Time", "Source", "Condition", "Action", "Level", "Description", "Value", "Units", "Operator", "Misc"]

all_tables = []
first = -1
for chunk in chunks:
    lines = [line for line in chunk.splitlines() if line.strip()]
    first += 1
    if len(lines)>2 and first !=0:
        #first += 1
        table_text = "\n".join(lines)
        #print("\n".join(lines[:5]))
        df = pd.read_fwf(StringIO(table_text))
        #print('cols after read_fwf: ', df.columns.tolist())
        #print('First few rows: ')
        #print(df.head())

        try:
            df.columns = custom_headers[:len(df.columns)]
            #print('test: ', df.iloc[:,1])
            df[['Time_only', 'Source_only']] = df.iloc[:, 1].str.extract(r'(\d{1,2}:\d{2}:\d{2}\.\d+)\s+(.*)')

            df["Time"] = df.iloc[:,0] + ' ' + df["Time_only"]
            df['Time'] = df['Time'].str.replace(r'\\', '/', regex=True)

            
            #df['Time'] = df["Time"].apply(normalize_datetime)
            df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
            df = pd.concat([df["Time"], df["Source_only"], df.iloc[:, 2:]], axis=1)
            
            df.columns = custom_headers[:len(df.columns)]
            df = df[~df.iloc[:,0].astype(str).str.contains('^-+$')]
            #print('df: ', df)
            tables.append(df)
            all_tables.append(df)
        except:
            a = 0

output_path = "output.xlsx"
output_path_csv = "output_htmlToCSV.xlsx"

final_df = pd.concat(all_tables, ignore_index = True)
final_df.to_excel(output_path_csv, sheet_name = "All_Tables", index=False)
