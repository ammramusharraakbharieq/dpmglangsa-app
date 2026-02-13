
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
        
        # KEY FIX 2: Explicitly find all merged ranges in data area and unmerge them
        # We must collect them first to avoid iterator modification issues
        ranges_to_unmerge = []
        for merged_range in list(ws.merged_cells.ranges): # Use list() to copy
            if merged_range.min_row >= start_row:
                ranges_to_unmerge.append(merged_range)
        
        for merged_range in ranges_to_unmerge:
            try:
                ws.unmerge_cells(str(merged_range))
            except KeyError:
                pass # Already unmerged or not found

        max_row = ws.max_row
        if max_row >= start_row:
            for row in range(start_row, max_row + 1):
                for col in range(1, end_col + 1):
                    cell = ws.cell(row=row, column=col)
                    # Double check: if it's still a merged cell (e.g. from above header), skip it
                    if isinstance(cell, MergedCell):
                        continue # Don't touch header-merged cells!
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
        start_row = 4
        
        # Clear existing data in template (it has data!)
        # Columns A to P (1 to 16)
        self._clear_data(ws, start_row, 16)
        
        from openpyxl.cell import MergedCell

        def safe_write(r, c, val):
            """Helper to write to cell only if it's NOT a merged cell (read-only)"""
            cell = ws.cell(row=r, column=c)
            if isinstance(cell, MergedCell):
                return # Skip writing to merged cells
            cell.value = val

        # Mapping based on analysis of uploaded file:
        # Col 1 (A): NO_PROV
        # ... (same as before) ...
        
        current_row = start_row
        last_desa = None
        
        # Sort by NO_KEC, NO_DESA, DESA, then NO_URUT
        df['NO_URUT_NUM'] = pd.to_numeric(df['NO_URUT'], errors='coerce')
        
        # KEY FIX: Filter out "Ghost Rows" 
        if 'NAMA_LENGKAP' in df.columns and 'JABATAN' in df.columns:
             name_str = df['NAMA_LENGKAP'].fillna('').astype(str).str.strip()
             jabatan_str = df['JABATAN'].fillna('').astype(str).str.strip()
             df = df[(name_str != '') | (jabatan_str != '')]

        # Sort!
        sort_cols = []
        if 'NO_KEC' in df.columns: sort_cols.append('NO_KEC')
        if 'NO_DESA' in df.columns: sort_cols.append('NO_DESA')
        if 'DESA' in df.columns: sort_cols.append('DESA') 
        sort_cols.append('NO_URUT_NUM')
        
        df = df.sort_values(by=sort_cols)
        
        for index, row in df.iterrows():
            desa = row.get('DESA')
            is_new_desa = (desa != last_desa)
            
            if is_new_desa:
                safe_write(current_row, 1, row.get('NO_PROV'))
                safe_write(current_row, 2, row.get('PROVINSI'))
                safe_write(current_row, 3, row.get('NO_KAB'))
                safe_write(current_row, 4, row.get('KABUPATEN'))
                safe_write(current_row, 5, row.get('NO_KEC'))
                safe_write(current_row, 6, row.get('KECAMATAN'))
                safe_write(current_row, 7, row.get('NO_DESA'))
                safe_write(current_row, 8, desa)
                last_desa = desa
            
            jabatan_raw = row.get('JABATAN')
            if (pd.isna(jabatan_raw) or str(jabatan_raw).strip() == '') and \
               (pd.isna(row.get('NAMA_LENGKAP')) or str(row.get('NAMA_LENGKAP')).strip() == ''):
                 continue

            jabatan = str(jabatan_raw).upper() if pd.notna(jabatan_raw) else ''
            
            if 'KEPALA DESA' in jabatan or 'PJ. KEPALA DESA' in jabatan:
                safe_write(current_row, 9, 'A')
                safe_write(current_row, 10, 'Kades')
            elif 'KADUS' in jabatan or 'KEPALA DUSUN' in jabatan:
                safe_write(current_row, 9, 'B')
                safe_write(current_row, 10, 'Prangkat')
            else:
                safe_write(current_row, 9, 'B')
                safe_write(current_row, 10, 'Prangkat')

            safe_write(current_row, 11, row.get('NO_URUT'))
            safe_write(current_row, 12, row.get('NAMA_LENGKAP'))
            
            nik = row.get('NIK')
            safe_write(current_row, 13, str(nik) if pd.notna(nik) else '')
            
            safe_write(current_row, 14, row.get('JENIS_KELAMIN'))
            safe_write(current_row, 15, row.get('JABATAN'))
            
            hp = row.get('NO_HP')
            safe_write(current_row, 16, str(hp) if pd.notna(hp) else '')

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
