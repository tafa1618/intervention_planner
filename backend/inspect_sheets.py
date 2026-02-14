
import pandas as pd
import os

file_path = "data/Programmes.xlsx"

try:
    df = pd.read_excel(file_path, sheet_name='Suivi_PS')
    print("Found Suivi_PS sheet.")
    print("Columns:", df.columns.tolist())
    print("First 3 rows:")
    print(df.head(3).to_dict(orient='records'))
except Exception as e:
    print(f"Error: {e}")
