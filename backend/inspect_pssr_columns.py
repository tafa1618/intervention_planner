
import pandas as pd

try:
    df = pd.read_excel('data/Programmes.xlsx', sheet_name='Inspection Rate', nrows=5)
    print("SPECIFIC COLUMNS:")
    print(df[['Last Inspect', 'Is Inspected']])
except Exception as e:
    print(f"Error: {e}")
