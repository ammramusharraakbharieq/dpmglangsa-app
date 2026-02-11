"""Full row dump around SUNGAI PAUH FIRDAUS"""
import openpyxl
from pathlib import Path

file_path = Path(__file__).parent / "data_(kepala desa & perangkat desa).xlsx"
wb = openpyxl.load_workbook(file_path)
ws = wb.active

lines = []
for r in range(349, 380):
    vals = {}
    for col in range(1, 17):
        v = ws.cell(row=r, column=col).value
        if v is not None:
            vals[col] = v
    lines.append(f"Row {r}: {vals if vals else 'EMPTY'}")

wb.close()

with open('spf_dump.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("Done - check spf_dump.txt")
