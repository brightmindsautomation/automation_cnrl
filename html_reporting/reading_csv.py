import pandas as pd

file_path = "filtered.csv"

df = pd.read_csv(file_path)


cols = df.columns

print(df["time"])


