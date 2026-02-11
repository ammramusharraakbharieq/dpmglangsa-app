"""
Verifikasi struktur file Excel baru: data_(kepala desa & perangkat desa).xlsx
"""
import pandas as pd
from pathlib import Path

fp = Path(r'd:\sistem-dpmg-langsa\data_(kepala desa & perangkat desa).xlsx')

print("=" * 60)
print("VERIFIKASI FILE EXCEL BARU")
print("=" * 60)
print(f"File: {fp.name}")
print(f"Exists: {fp.exists()}")
print(f"Size: {fp.stat().st_size} bytes")
print()

# Read raw
df = pd.read_excel(fp, header=None)
print(f"Total rows (raw): {len(df)}")
print(f"Total columns: {len(df.columns)}")
print()

# Show header rows (first 5)
print("--- Header Rows (baris 1-5, akan diskip oleh app) ---")
for i in range(min(5, len(df))):
    vals = []
    for v in df.iloc[i].tolist():
        s = str(v) if pd.notna(v) else "NaN"
        vals.append(s[:30])
    print(f"  Row {i+1}: {vals}")
print()

# Check column count
if len(df.columns) != 16:
    print(f"GAGAL: Kolom = {len(df.columns)}, seharusnya 16")
    exit(1)

print("Kolom count: 16 OK")
print()

# Load like the app
columns = [
    'NO_PROV', 'PROVINSI', 'NO_KAB', 'KABUPATEN', 'NO_KEC', 'KECAMATAN',
    'NO_DESA', 'DESA', 'KATEGORI', 'JENIS', 'NO_URUT', 'NAMA_LENGKAP',
    'NIK', 'JENIS_KELAMIN', 'JABATAN', 'NO_HP'
]

df_data = df.iloc[5:].copy()
df_data.columns = columns
df_data = df_data.reset_index(drop=True)

# Forward fill
merge_columns = ['NO_PROV', 'PROVINSI', 'NO_KAB', 'KABUPATEN', 'NO_KEC', 'KECAMATAN', 'NO_DESA', 'DESA']
for col in merge_columns:
    df_data[col] = df_data[col].ffill()

valid_kecamatan = ['LANGSA TIMUR', 'LANGSA BARAT', 'LANGSA KOTA', 'LANGSA BARO', 'LANGSA LAMA']
df_data = df_data[df_data['KECAMATAN'].isin(valid_kecamatan)]
df_data = df_data.reset_index(drop=True)

# Convert NO_URUT
df_data['NO_URUT'] = pd.to_numeric(df_data['NO_URUT'], errors='coerce')

print(f"Valid data rows: {len(df_data)}")
kec_list = sorted(df_data['KECAMATAN'].unique().tolist())
print(f"Kecamatan ({len(kec_list)}): {kec_list}")
desa_count = df_data['DESA'].nunique()
print(f"Jumlah Desa: {desa_count}")
jabatan_list = sorted(df_data['JABATAN'].dropna().unique().tolist())
print(f"Jabatan unik ({len(jabatan_list)}): {jabatan_list}")
print()

# Sample data
print("--- Sample Data (10 baris pertama) ---")
sample = df_data[['KECAMATAN', 'DESA', 'NO_URUT', 'NAMA_LENGKAP', 'JABATAN', 'NO_HP']].head(10)
print(sample.to_string(index=False))
print()

# Verify each column has data
print("--- Column Summary ---")
for col in columns:
    non_null = df_data[col].notna().sum()
    pct = non_null / len(df_data) * 100 if len(df_data) > 0 else 0
    sample_val = str(df_data[col].dropna().iloc[0])[:30] if non_null > 0 else "KOSONG"
    print(f"  {col:20s}: {non_null:4d}/{len(df_data)} ({pct:.0f}%) | sample: {sample_val}")

print()
print("=" * 60)
if len(df_data) > 0 and len(kec_list) == 5:
    print("HASIL: FILE EXCEL VALID - Siap digunakan!")
elif len(df_data) > 0:
    print(f"PERINGATAN: File bisa dibaca tapi kecamatan hanya {len(kec_list)} (seharusnya 5)")
else:
    print("GAGAL: Tidak ada data valid yang bisa dibaca")
print("=" * 60)
