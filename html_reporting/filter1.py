'''
This python script can extract out the data from csv and later applying some filter on the specific
column values (Filtering should not be case sensitive and condition should be contains rather than
string match)

Inside column values - Filters are following OR condition
Between columns - Following AND condition
'''

import pandas as pd

file_path = "rpt026.xlsx"

# Define filter variables
filter_description = ["pida.op", "station failure", "operator logged in"]
filter_condition = ["change", "display call up"]
filter_operator = ["seenu", "panchal", "froth op"]

filters = {
    "description": filter_description,
    "condition": filter_condition,
    "operator": filter_operator
}

# Read all sheets
excel_file = pd.ExcelFile(file_path)

filtered_sheets = []


for sheet_name in excel_file.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=1) # header determines which row has column

    df.columns = df.columns.str.strip().str.lower()

    required_cols = set(filters.keys())
    if not required_cols.issubset(df.columns):
        print(f"Skipping sheet '{sheet_name}' (required columns missing)")
        continue

    # Start with TRUE mask for AND logic
    mask = pd.Series([True] * len(df))

    for col, values in filters.items():
        if values:   # Only apply filter if list not empty
            pattern = "|".join(values)
            column_mask = df[col].astype(str).str.contains(
                pattern, case=False, na=False
            )
            mask &= column_mask   # AND between columns

    filtered_df = df[mask]

    if not filtered_df.empty:
        filtered_df["source_sheet"] = sheet_name
        filtered_sheets.append(filtered_df)

if filtered_sheets:
    final_df = pd.concat(filtered_sheets, ignore_index=True)
else:
    final_df = pd.DataFrame()

print(final_df)

# Source - https://stackoverflow.com/a/16923367
# Posted by Andy Hayden, modified by community. See post 'Timeline' for change history
# Retrieved 2026-02-22, License - CC BY-SA 4.0

final_df.to_csv('filtered.csv', sep='\t', encoding='utf-8', index=False, header=True)



   
