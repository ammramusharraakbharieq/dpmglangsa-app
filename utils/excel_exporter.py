
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
        """Clear data from start_row downwards, keeping style"""
        # Note: clearing cells one by one preserves style better than deleting rows
        # But for performance on large sheets, deleting rows might be needed.
        # Given the user wants to preserve structure/style, we should be careful.
        # Does openpyxl delete_rows keep style of rows below? No, it shifts them up.
        # But we are at the end of the sheet usually.
        
        max_row = ws.max_row
        if max_row >= start_row:
            # We can delete rows from start_row to max_row
            # But wait, sometimes there are footers? Assuming no footers for now based on analysis.
            ws.delete_rows(start_row, amount=(max_row - start_row + 1))

    def export_camat_mukim_geuchik(self, df):
        filename = "data_(camat,mukim,dan geuchik).xlsx"
        wb = self._load_template(filename)
        ws = wb.active
        start_row = 2

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
            ws.cell(row=current_row, column=3, value=row.get('NAMA_CAMAT'))
            ws.cell(row=current_row, column=4, value=row.get('KEMUKIMAN'))
            ws.cell(row=current_row, column=5, value=row.get('NAMA_MUKIM'))
            ws.cell(row=current_row, column=6, value=row.get('GAMPONG'))
            ws.cell(row=current_row, column=7, value=row.get('NAMA_GEUCHIK'))

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
        filename = "data_(kepala desa & perangkat desa).xlsx"
        wb = self._load_template(filename)
        ws = wb.active
        start_row = 6
        self._clear_data(ws, start_row, 16)

        # Mapping based on analysis:
        # Col 1(A): NO (Global Kades Count 1,2,3...) OR Empty?
        # Wait, Analysis Row 6: '11', 'ACEH'... -> These are Cols A..H
        # Col 11(K): NO (Urut 1..10)
        # Col 12(L): NAMA
        # Col 13(M): NIK
        # Col 14(N): JK
        # Col 15(O): JABATAN
        # Col 16(P): HP
        
        # Grouping Logic:
        # For each DESA, the first row (Kepala Desa) has info in A-H.
        # Subsquent rows (Perangkat) have A-H empty.
        
        current_row = start_row
        last_desa = None
        
        # Sort DF by Kecamatan -> Kemukiman -> Gampong -> No Urut to ensure grouping
        # DF loaded from data_loader might already be sorted but let's be safe if possible
        # However, data_loader.load_perangkat_desa filters and sorts broadly.
        
        for index, row in df.iterrows():
            desa = row.get('DESA')
            is_new_desa = (desa != last_desa)
            
            if is_new_desa:
                # Fill A-H (1-8)
                ws.cell(row=current_row, column=1, value=row.get('NO_PROV'))
                ws.cell(row=current_row, column=2, value=row.get('PROVINSI'))
                ws.cell(row=current_row, column=3, value=row.get('NO_KAB'))
                ws.cell(row=current_row, column=4, value=row.get('KABUPATEN'))
                ws.cell(row=current_row, column=5, value=row.get('NO_KEC'))
                ws.cell(row=current_row, column=6, value=row.get('KECAMATAN'))
                ws.cell(row=current_row, column=7, value=row.get('NO_DESA'))
                ws.cell(row=current_row, column=8, value=desa)
                last_desa = desa
            
            # Fill I-J (9-10) [Kategori & Jenis]
            # Logic: If it's KEPALA DESA -> A, Kades. Else -> B, Prangkat/K. Dusun
            jabatan = str(row.get('JABATAN', '')).upper()
            if 'KEPALA DESA' in jabatan or 'PJ. KEPALA DESA' in jabatan:
                ws.cell(row=current_row, column=9, value='A')
                ws.cell(row=current_row, column=10, value='Kades')
            elif 'KADUS' in jabatan or 'KEPALA DUSUN' in jabatan:
                ws.cell(row=current_row, column=9, value='B')
                ws.cell(row=current_row, column=10, value='K. Dusun')
            else:
                ws.cell(row=current_row, column=9, value='B')
                ws.cell(row=current_row, column=10, value='Perangkat')

            # Fill K-P (11-16)
            ws.cell(row=current_row, column=11, value=row.get('NO_URUT'))
            ws.cell(row=current_row, column=12, value=row.get('NAMA_LENGKAP'))
            # NIK might be loaded as float/int, ensure string
            nik = row.get('NIK')
            ws.cell(row=current_row, column=13, value=str(nik) if pd.notna(nik) else '')
            ws.cell(row=current_row, column=14, value=row.get('JENIS_KELAMIN'))
            ws.cell(row=current_row, column=15, value=row.get('JABATAN'))
            # HP might be float/int, ensure string
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
