import pandas as pd
import warnings
warnings.filterwarnings('ignore')

output = []

def log(text):
    output.append(text)
    print(text)

def analyze_file(filepath, title):
    log('='*80)
    log(f'{title}')
    log('='*80)
    
    xl = pd.ExcelFile(filepath)
    log(f'Sheet names: {xl.sheet_names}')
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet, header=None)
        log(f'\n--- Sheet: {sheet} ---')
        log(f'Dimensi: {df.shape[0]} baris x {df.shape[1]} kolom')
        
        # Print first 5 rows
        log('\nHeader dan beberapa baris data:')
        for idx, row in df.head(8).iterrows():
            values = [str(v)[:25] if pd.notna(v) else 'NaN' for v in row.values]
            log(f'  Row {idx}: {values}')
    log('')

# File 1
analyze_file('data_(camat,mukim,dan geuchik).xlsx', 'FILE 1: data_(camat,mukim,dan geuchik).xlsx')

# File 2  
analyze_file('data_(geuchik kota langsa).xlsx', 'FILE 2: data_(geuchik kota langsa).xlsx')

# File 3
analyze_file('data_(kepala desa & perangkat desa).xlsx', 'FILE 3: data_(kepala desa & perangkat desa).xlsx')

# File 4
analyze_file('data_(tuha peuet gampong).xlsx', 'FILE 4: data_(tuha peuet gampong).xlsx')

# Save to file
with open('analysis_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

log('\nHasil analisis disimpan ke analysis_result.txt')
