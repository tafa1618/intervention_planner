
import pandas as pd
import sys

file_path = "data/Programmes.xlsx"

try:
    print("Reading file...", flush=True)
    df = pd.read_excel(file_path, sheet_name='Suivi_PS')
    print("Columns found:", flush=True)
    print(df.columns.tolist(), flush=True)
    print("First row:", flush=True)
    print(df.iloc[0].to_dict(), flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
