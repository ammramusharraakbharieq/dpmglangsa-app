
import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from io import BytesIO
from pathlib import Path
import shutil

class ExcelExporter:
    def __init__(self, base_path):
        self.base_path = Path(base_path)

    def _load_template(self, filename):
        """Load the workbook from file, effectively using it as a template"""
        file_path = self.base_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {filename}")
        
        # Load workbook
        wb = openpyxl.load_workbook(file_path)
        return wb

    def _clear_data(self, ws, start_row, end_col):
        """Clear data from start_row downwards, preserving row structure/style"""
        from openpyxl.cell import MergedCell
        
        # KEY FIX: Unmerge all cells in the data area first!
        # Writing to a merged cell (except top-left) raises ReadOnly error.
        # Since we are overwriting data, we should flatten the structure in the data area.
        
        # Find ranges to unmerge
        ranges_to_unmerge = []
        for merged_range in ws.merged_cells.ranges:
            # Check if range intersects with our data area (row >= start_row)
            if merged_range.min_row >= start_row:
                ranges_to_unmerge.append(merged_range)
        
        # Unmerge them
        for merged_range in ranges_to_unmerge:
            ws.unmerge_cells(str(merged_range))

        max_row = ws.max_row
        if max_row >= start_row:
            # Iterate row by row
            for row in range(start_row, max_row + 1):
                for col in range(1, end_col + 1):
                    cell = ws.cell(row=row, column=col)
                    cell.value = None

    def export_camat_mukim_geuchik(self, df):
        filename = "data_(camat,mukim,dan geuchik).xlsx"
        wb = self._load_template(filename)
        ws = wb.active
        start_row = 2 # Start clearing from Row 2

        self._clear_data(ws, start_row, 7)

        # Columns mapping:
        # A: NO, B: KECAMATAN, C: NAMA CAMAT, D: KEMUKIMAN, E: NAMA MUKIM, F: GAMPONG, G: NAMA GEUCHIK
        
        # Ensure DF has these columns
        # DF from load_camat_mukim_geuchik has:
        # NO, KECAMATAN, NAMA_CAMAT, KEMUKIMAN, NAMA_MUKIM, GAMPONG, NAMA_GEUCHIK
        
        for index, row in df.iterrows():
            current_row = start_row + index
            ws.cell(row=current_row, column=1, value=index + 1) # NO
            ws.cell(row=current_row, column=2, value=row.get('KECAMATAN'))
            # Corrected keys based on data_loader (from Excel Header)
            ws.cell(row=current_row, column=3, value=row.get('NAMA CAMAT'))
            ws.cell(row=current_row, column=4, value=row.get('KEMUKIMAN'))
            ws.cell(row=current_row, column=5, value=row.get('NAMA MUKIM'))
            ws.cell(row=current_row, column=6, value=row.get('GAMPONG'))
            ws.cell(row=current_row, column=7, value=row.get('NAMA GEUCHIK'))

        output = BytesIO()
        wb.save(output)
        return output.getvalue()

    def export_geuchik_detail(self, df):
        filename = "data_(geuchik kota langsa).xlsx"
        wb = self._load_template(filename)
        ws = wb.active
        start_row = 4

        self._clear_data(ws, start_row, 18)

        # Mapping based on analysis and data_loader
        # A(1): PROVINSI (NO in df?), 
        # B(2): PROVINSI NAME? -> Header says PROVINSI merged? 
        # Wait, let's look at row 4 of analysis:
        # Col 0 ('11'): NO_PROV? 
        # Col 1 ('ACEH'): PROVINSI
        # Col 2 ('11.74'): NO_KAB
        # Col 3 ('LANGSA'): KABUPATEN
        # Col 4 ('11.74.01'): NO_KEC
        # Col 5 ('LANGSA TIMUR'): KECAMATAN
        # Col 6 ('11.74.01.2007'): NO_DESA
        # Col 7 ('BUKET MEDANG ARA'): DESA
        # Col 8 ('MUHAMMAD JAMIL...'): NAMA_LENGKAP
        # Col 9: TGL_LAHIR
        # Col 10: BLN_LAHIR
        # Col 11: THN_LAHIR
        # Col 12: JENIS_KELAMIN
        # Col 13: PENDIDIKAN
        # Col 14: SK_NOMOR
        # Col 15: SK_TANGGAL
        # Col 16: JABATAN
        # Col 17: NO_HP
        
        for index, row in df.iterrows():
            r = start_row + index
            # data_loader.load_geuchik_detail columns:
            # NO_PROV, PROVINSI, NO_KAB, KABUPATEN, NO_KEC, KECAMATAN, NO_DESA, DESA, 
            # NAMA_LENGKAP, TGL_LAHIR, BLN_LAHIR, THN_LAHIR, JENIS_KELAMIN, PENDIDIKAN,
            # SK_NOMOR, SK_TANGGAL, JABATAN, NO_HP
            
            ws.cell(row=r, column=1, value=row.get('NO_PROV'))
            ws.cell(row=r, column=2, value=row.get('PROVINSI'))
            ws.cell(row=r, column=3, value=row.get('NO_KAB'))
            ws.cell(row=r, column=4, value=row.get('KABUPATEN'))
            ws.cell(row=r, column=5, value=row.get('NO_KEC'))
            ws.cell(row=r, column=6, value=row.get('KECAMATAN'))
            ws.cell(row=r, column=7, value=row.get('NO_DESA'))
            ws.cell(row=r, column=8, value=row.get('DESA'))
            ws.cell(row=r, column=9, value=row.get('NAMA_LENGKAP'))
            ws.cell(row=r, column=10, value=row.get('TGL_LAHIR'))
            ws.cell(row=r, column=11, value=row.get('BLN_LAHIR'))
            ws.cell(row=r, column=12, value=row.get('THN_LAHIR'))
            ws.cell(row=r, column=13, value=row.get('JENIS_KELAMIN'))
            ws.cell(row=r, column=14, value=row.get('PENDIDIKAN'))
            ws.cell(row=r, column=15, value=row.get('SK_NOMOR'))
            ws.cell(row=r, column=16, value=row.get('SK_TANGGAL'))
            ws.cell(row=r, column=17, value=row.get('JABATAN'))
            ws.cell(row=r, column=18, value=row.get('NO_HP'))

        output = BytesIO()
        wb.save(output)
        return output.getvalue()


    def export_perangkat_desa(self, df):
        # USE NEW TEMPLATE (Created from User Upload)
        filename = "template_perangkat_desa_new.xlsx"
        wb = self._load_template(filename)
        ws = wb.active
        
        # Start Row usually 4 based on analysis of the new file
        # (Row 1-3 are headers, Row 4 is first data)
        start_row = 4
        
        # Clear existing data in template (it has data!)
        # Columns A to P (1 to 16)
        self._clear_data(ws, start_row, 16)

        # Mapping based on analysis of uploaded file:
        # Col 1 (A): NO_PROV
        # Col 2 (B): PROVINSI
        # Col 3 (C): NO_KAB
        # Col 4 (D): KABUPATEN
        # Col 5 (E): NO_KEC
        # Col 6 (F): KECAMATAN
        # Col 7 (G): NO_DESA
        # Col 8 (H): DESA
        # Col 9 (I): Unnamed/Spacer (Status A/B?) -> In previous code this was Col 9.
        # Col 10 (J): Unnamed/Spacer (Jabatan Group?) -> In previous code this was Col 10.
        # Col 11 (K): NO (Urut)
        # Col 12 (L): NAMA LENGKAP
        # Col 13 (M): NIK
        # Col 14 (N): JK
        # Col 15 (O): JABATAN
        # Col 16 (P): HP
        
        current_row = start_row
        last_desa = None
        
        # Sort by NO_KEC, NO_DESA, DESA, then NO_URUT
        # First ensure NO_URUT is numeric
        df['NO_URUT_NUM'] = pd.to_numeric(df['NO_URUT'], errors='coerce')
        
        # KEY FIX: Filter out "Ghost Rows" (result of ffill on empty source rows)
        # ONLY remove if BOTH Name AND Jabatan are empty/null.
        # PRESERVES valid vacant positions (Name empty, Jabatan filled)
        if 'NAMA_LENGKAP' in df.columns and 'JABATAN' in df.columns:
             name_str = df['NAMA_LENGKAP'].fillna('').astype(str).str.strip()
             jabatan_str = df['JABATAN'].fillna('').astype(str).str.strip()
             
             # Keep row if it has Name OR Jabatan content
             df = df[(name_str != '') | (jabatan_str != '')]

        # Sort!
        sort_cols = []
        if 'NO_KEC' in df.columns: sort_cols.append('NO_KEC')
        if 'NO_DESA' in df.columns: sort_cols.append('NO_DESA')
        if 'DESA' in df.columns: sort_cols.append('DESA') # Vital: Sort by Name too in case IDs are dupes
        sort_cols.append('NO_URUT_NUM')
        
        df = df.sort_values(by=sort_cols)
        
        for index, row in df.iterrows():
            desa = row.get('DESA')
            is_new_desa = (desa != last_desa)
            
            # --- VILLAGE BLOCK HEADERS (Cols A-H) ---
            # Grouping Logic: Only write Village info on the FIRST row of the village
            # This mimics the "Merge" look without actually merging cells (which complicates sorting/filtering later)
            # OR should we fill every row? 
            # The previous code (and typical requirement for sorting) is 
            # to Fill A-H only on 'is_new_desa'.
            
            if is_new_desa:
                ws.cell(row=current_row, column=1, value=row.get('NO_PROV'))
                ws.cell(row=current_row, column=2, value=row.get('PROVINSI'))
                ws.cell(row=current_row, column=3, value=row.get('NO_KAB'))
                ws.cell(row=current_row, column=4, value=row.get('KABUPATEN'))
                ws.cell(row=current_row, column=5, value=row.get('NO_KEC'))
                ws.cell(row=current_row, column=6, value=row.get('KECAMATAN'))
                ws.cell(row=current_row, column=7, value=row.get('NO_DESA'))
                ws.cell(row=current_row, column=8, value=desa)
                last_desa = desa
            
            # --- STATUS/GROUP COLUMNS (Cols I-J) ---
            # Col 9 (I): A/B code
            # Col 10 (J): Kades/Prangkat label
            
            jabatan_raw = row.get('JABATAN')
            # Extra safety check for empty rows, though filter above handles it
            if (pd.isna(jabatan_raw) or str(jabatan_raw).strip() == '') and \
               (pd.isna(row.get('NAMA_LENGKAP')) or str(row.get('NAMA_LENGKAP')).strip() == ''):
                 continue

            jabatan = str(jabatan_raw).upper() if pd.notna(jabatan_raw) else ''
            
            if 'KEPALA DESA' in jabatan or 'PJ. KEPALA DESA' in jabatan:
                ws.cell(row=current_row, column=9, value='A')
                ws.cell(row=current_row, column=10, value='Kades')
            elif 'KADUS' in jabatan or 'KEPALA DUSUN' in jabatan:
                ws.cell(row=current_row, column=9, value='B')
                ws.cell(row=current_row, column=10, value='Prangkat')
            else:
                ws.cell(row=current_row, column=9, value='B')
                ws.cell(row=current_row, column=10, value='Prangkat')

            # --- PERSON DATA (Cols K-P) ---
            ws.cell(row=current_row, column=11, value=row.get('NO_URUT'))
            ws.cell(row=current_row, column=12, value=row.get('NAMA_LENGKAP'))
            
            nik = row.get('NIK')
            ws.cell(row=current_row, column=13, value=str(nik) if pd.notna(nik) else '')
            
            ws.cell(row=current_row, column=14, value=row.get('JENIS_KELAMIN'))
            ws.cell(row=current_row, column=15, value=row.get('JABATAN'))
            
            hp = row.get('NO_HP')
            ws.cell(row=current_row, column=16, value=str(hp) if pd.notna(hp) else '')

            current_row += 1

        output = BytesIO()
        wb.save(output)
        return output.getvalue()

    def export_tuha_peuet(self, df):
        filename = "data_(tuha peuet gampong).xlsx"
        wb = self._load_template(filename)
        ws = wb.active
        start_row = 8
        self._clear_data(ws, start_row, 11)

        # Cols:
        # A(1): NO (Global Sequential 1,1,1..?)
        # Wait, Analysis Row 8: '1', 'LANGSA TIMUR', '1', 'SEUNEUBOK ANTARA', '1', 'BUKET MEDANG ARA', '1', 'Nurhasan'...
        # Row 9: '', '', '', '', '', '', '2', 'Bustami'...
        # So Cols A-F are Grouping Cols.
        # Col G(7): No Anggota (1,2,3...)
        # Col H(8): Nama
        # Col I(9): L (Checkmark)
        # Col J(10): P (Checkmark)
        # Col K(11): Ket
        
        current_row = start_row
        last_gampong = None
        global_no = 1
        
        # We need external counters for grouping
        # But looking at analysis:
        # Row 8 (New Gampong):
        # A: 1 (Global No?)
        # B: LANGSA TIMUR
        # C: 1 (No Mukim?)
        # D: SEUNEUBOK ANTARA (Mukim)
        # E: 1 (No Gampong?)
        # F: BUKET MEDANG ARA (Gampong)
        
        for index, row in df.iterrows():
            gampong = row.get('GAMPONG')
            is_new_gampong = (gampong != last_gampong)
            
            if is_new_gampong:
                # We assume simple global increment for A? 
                # Or is it per Kecamatan? Analysis shows '1' at start.
                # Let's just use an incrementing integer for now.
                ws.cell(row=current_row, column=1, value=global_no)
                ws.cell(row=current_row, column=2, value=row.get('KECAMATAN'))
                ws.cell(row=current_row, column=3, value=row.get('NO_KEMUKIMAN'))
                ws.cell(row=current_row, column=4, value=row.get('KEMUKIMAN'))
                ws.cell(row=current_row, column=5, value=row.get('NO_GAMPONG'))
                ws.cell(row=current_row, column=6, value=gampong)
                
                global_no += 1
                last_gampong = gampong
            
            # Data Columns (G-K)
            ws.cell(row=current_row, column=7, value=row.get('NO_ANGGOTA'))
            ws.cell(row=current_row, column=8, value=row.get('NAMA_ANGGOTA'))
            
            # Checkbox Logic
            # Check input from DF (LAKI_LAKI / PEREMPUAN cols)
            # If they contain '✓' or specific codes, preserve them.
            # If empty but we have JENIS_KELAMIN info? (Helper might need to add JK column to Load if missing)
            # Currently load_tuha_peuet returns LAKI_LAKI and PEREMPUAN columns directly from sheet.
            # So we just pass them through.
            
            ws.cell(row=current_row, column=9, value=row.get('LAKI_LAKI'))
            ws.cell(row=current_row, column=10, value=row.get('PEREMPUAN'))
            ws.cell(row=current_row, column=11, value=row.get('KETERANGAN'))
            
            current_row += 1

        output = BytesIO()
        wb.save(output)
        return output.getvalue()
