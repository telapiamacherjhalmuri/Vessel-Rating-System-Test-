import csv

filepath = r"E:\Vessel_Rating_System - Copy\data\Risk & Compliance - Sanctioned Vessel List - completed.csv"

with open(filepath, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

data_rows = len(rows) - 1  # exclude header
print(f"File: {filepath}")
print(f"Total rows (including header): {len(rows)}")
print(f"Data rows: {data_rows}")
assert data_rows >= 28, f"Expected at least 28 data rows, found {data_rows}"
print("Check passed: file contains at least 28 vessel rows.")
