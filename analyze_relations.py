import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Load all files
print("="*80)
print("ANALISIS RELASI DATA ANTAR FILE")
print("="*80)

# File 1: Camat, Mukim, Geuchik
df1 = pd.read_excel('data_(camat,mukim,dan geuchik).xlsx')
print(f"\n1. File Camat/Mukim/Geuchik: {len(df1)} rows")
print(f"   Kolom: {list(df1.columns)}")
print(f"   Kecamatan unik: {df1['KECAMATAN'].nunique()}")
print(f"   Gampong unik: {df1['GAMPONG'].nunique()}")

# File 2: Geuchik Kota Langsa (detail)
df2 = pd.read_excel('data_(geuchik kota langsa).xlsx', header=2)
print(f"\n2. File Geuchik Detail: {len(df2)-1} rows (header excluded)")
print(f"   Kolom: {list(df2.columns)}")

# File 3: Kepala Desa & Perangkat
df3 = pd.read_excel('data_(kepala desa & perangkat desa).xlsx', header=4)
print(f"\n3. File Kepala Desa & Perangkat: {len(df3)} rows")
print(f"   Kolom: {list(df3.columns)}")

# File 4: Tuha Peuet Gampong
df4 = pd.read_excel('data_(tuha peuet gampong).xlsx', header=6)
print(f"\n4. File Tuha Peuet Gampong: {len(df4)} rows")
print(f"   Kolom: {list(df4.columns)}")

print("\n" + "="*80)
print("IDENTIFIKASI DATA YANG TERKAIT ANTAR FILE")
print("="*80)

# Check nama geuchik in file 1
print("\n--- Nama Geuchik dari File 1 (sample) ---")
for i, row in df1.head(5).iterrows():
    print(f"  Gampong: {row['GAMPONG']}, Geuchik: {row['NAMA GEUCHIK']}")

# Check corresponding data in file 2
print("\n--- Data dari File 2 untuk Gampong yang sama ---")
for i, row in df2.head(5).iterrows():
    if pd.notna(row.get('8')):
        print(f"  Desa: {row.get('8', 'N/A')}, Nama: {row.get('9', 'N/A')}")

# Check in file 3
print("\n--- Data dari File 3 untuk Gampong yang sama ---")
for i, row in df3.head(10).iterrows():
    if pd.notna(row.get('8')) and pd.notna(row.get('12')):
        print(f"  Desa: {row.get('8', 'N/A')}, Nama: {row.get('12', 'N/A')}, Jabatan: {row.get('15', 'N/A')}")

print("\n" + "="*80)
print("RINGKASAN RELASI DATA")
print("="*80)
print("""
Data yang SALING TERKAIT antar file:

1. NAMA GAMPONG/DESA: 
   - Ada di File 1 (GAMPONG), File 2 (DESA/NAMA), File 3 (DESA/NAMA), File 4 (GAMPONG)

2. NAMA GEUCHIK/KEPALA DESA:
   - Ada di File 1 (NAMA GEUCHIK), File 2 (NAMA LENGKAP), File 3 (NAMA LENGKAP dengan jabatan Kepala Desa)

3. KECAMATAN:
   - Ada di semua 4 file

4. KEMUKIMAN:
   - Ada di File 1 dan File 4

Ketika user mengedit NAMA GEUCHIK di satu tempat, sistem harus update di:
- File 1: kolom NAMA GEUCHIK
- File 2: kolom NAMA LENGKAP (untuk baris yang sesuai)
- File 3: kolom NAMA LENGKAP (untuk baris dengan jabatan KEPALA DESA/PJ. KEPALA DESA)
""")
