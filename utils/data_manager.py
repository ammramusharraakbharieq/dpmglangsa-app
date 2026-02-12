"""
Data Manager Module
Sistem Manajemen Data Gampong - Dinas Pemberdayaan Kota Langsa

Module untuk operasi CRUD dan integrasi cross-file di Google Sheets.
"""

import pandas as pd
import streamlit as st
import gspread
from utils.data_loader import SPREADSHEET_NAME, get_gspread_client

# We need to manually clear cache when updating data
def clear_cache():
    st.cache_data.clear()

def get_worksheet(sheet_name):
    """Helper to get worksheet object"""
    client = get_gspread_client()
    if not client:
        return None
    try:
        sh = client.open(SPREADSHEET_NAME)
        return sh.worksheet(sheet_name)
    except Exception as e:
        st.error(f"Error accessing sheet {sheet_name}: {e}")
        return None


def _sync_geuchik_data_across_files(gampong_name, field_map):
    """
    Internal helper to sync ANY Geuchik data across files.
    field_map: dict of {field_name: new_value}
    Supported fields: NAMA_LENGKAP, JENIS_KELAMIN, JABATAN, NO_HP, NO_DESA
    """
    try:
        # 1. Camat_Mukim_Geuchik (Only has NAMA GEUCHIK)
        if 'NAMA_LENGKAP' in field_map:
            new_name = field_map['NAMA_LENGKAP']
            ws1 = get_worksheet("Camat_Mukim_Geuchik")
            if ws1:
                try:
                    cell = ws1.find(gampong_name)
                    if cell and cell.col == 6:
                        ws1.update_cell(cell.row, 7, new_name)
                except gspread.exceptions.CellNotFound:
                    pass

        # 2. Geuchik_Detail
        # Fields: NO_DESA(7), NAMA_LENGKAP(9), JENIS_KELAMIN(13), JABATAN(17), NO_HP(18)
        ws2 = get_worksheet("Geuchik_Detail")
        if ws2:
            try:
                cell = ws2.find(gampong_name)
                if cell and cell.col == 8:
                    row = cell.row
                    if 'NO_DESA' in field_map: ws2.update_cell(row, 7, field_map['NO_DESA'])
                    if 'NAMA_LENGKAP' in field_map: ws2.update_cell(row, 9, field_map['NAMA_LENGKAP'])
                    if 'JENIS_KELAMIN' in field_map: ws2.update_cell(row, 13, field_map['JENIS_KELAMIN'])
                    if 'JABATAN' in field_map: ws2.update_cell(row, 17, field_map['JABATAN'])
                    if 'NO_HP' in field_map: ws2.update_cell(row, 18, field_map['NO_HP'])
            except gspread.exceptions.CellNotFound:
                pass

        # 3. Perangkat_Desa
        # Fields: NO_DESA(7), NAMA_LENGKAP(12), JENIS_KELAMIN(14), JABATAN(15), NO_HP(16)
        ws3 = get_worksheet("Perangkat_Desa")
        if ws3:
            cells = ws3.findall(gampong_name)
            for cell in cells:
                if cell.col == 8:
                    # Check if this row is for Kepala Desa
                    jabatan_val = ws3.cell(cell.row, 15).value
                    # We check if it's currently Kepdes OR if we are updating Jabatan to/from Kepdes
                    # Ideally we find the existing Kepdes row
                    if jabatan_val and str(jabatan_val).strip().upper() in ['KEPALA DESA', 'PJ. KEPALA DESA']:
                        row = cell.row
                        if 'NO_DESA' in field_map: ws3.update_cell(row, 7, field_map['NO_DESA'])
                        if 'NAMA_LENGKAP' in field_map: ws3.update_cell(row, 12, field_map['NAMA_LENGKAP'])
                        if 'JENIS_KELAMIN' in field_map: ws3.update_cell(row, 14, field_map['JENIS_KELAMIN'])
                        if 'JABATAN' in field_map: ws3.update_cell(row, 15, field_map['JABATAN'])
                        if 'NO_HP' in field_map: ws3.update_cell(row, 16, field_map['NO_HP'])
                        break

    except Exception as e:
        print(f"Sync error: {e}")

def update_geuchik_name(gampong_name, old_name, new_name):
    """Update nama Geuchik di semua sheet (Triggered from Page 2)"""
    try:
        _sync_geuchik_data_across_files(gampong_name, {'NAMA_LENGKAP': new_name})
        clear_cache()
        return {'file1': {'updated': True, 'rows': 1}, 'file2': {'updated': True, 'rows': 1}, 'file3': {'updated': True, 'rows': 1}}
    except Exception as e:
         return {'error': str(e)}

def update_geuchik_detail(desa, field, new_value):
    """Update satu field data detail Geuchik"""
    try:
        ws = get_worksheet("Geuchik_Detail")
        if not ws: return {'success': False, 'message': 'Sheet not found'}
        
        field_col_map = {
            'NO_DESA': 7, 'NAMA_LENGKAP': 9, 'TGL_LAHIR': 10, 'BLN_LAHIR': 11,
            'THN_LAHIR': 12, 'JENIS_KELAMIN': 13, 'PENDIDIKAN': 14,
            'SK_NOMOR': 15, 'SK_TANGGAL': 16, 'JABATAN': 17, 'NO_HP': 18
        }
        col = field_col_map.get(field)
        if not col: return {'success': False, 'message': 'Field invalid'}

        cell = ws.find(desa)
        if cell and cell.col == 8: 
             ws.update_cell(cell.row, col, new_value)
             
             # SYNC: If updating key fields, sync to other files
             sync_fields = ['NO_DESA', 'NAMA_LENGKAP', 'JENIS_KELAMIN', 'JABATAN', 'NO_HP']
             if field in sync_fields:
                 _sync_geuchik_data_across_files(desa, {field: new_value})
                 
             clear_cache()
             return {'success': True, 'message': 'Updated'}
        
        return {'success': False, 'message': 'Desa not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def update_camat_name(kecamatan, old_name, new_name):
    """Update nama Camat di Sheet 1"""
    try:
        ws = get_worksheet("Camat_Mukim_Geuchik")
        if not ws: return {'success': False, 'message': 'Sheet not found'}
        
        cells = ws.findall(kecamatan)
        count = 0
        for cell in cells:
            if cell.col == 2:
                 camat_val = ws.cell(cell.row, 3).value
                 if camat_val == old_name:
                     ws.update_cell(cell.row, 3, new_name)
                     count += 1
        
        if count > 0:
            clear_cache()
            return {'success': True, 'rows': count}
        return {'success': False, 'message': 'Data not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def update_mukim_name(kemukiman, old_name, new_name):
    try:
        ws = get_worksheet("Camat_Mukim_Geuchik")
        cells = ws.findall(kemukiman)
        count = 0
        for cell in cells:
            if cell.col == 4:
                if ws.cell(cell.row, 5).value == old_name:
                    ws.update_cell(cell.row, 5, new_name)
                    count += 1
        if count > 0:
            clear_cache()
            return {'success': True, 'rows': count}
        return {'success': False, 'message': 'Data not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def add_gampong(data):
    try:
        ws = get_worksheet("Camat_Mukim_Geuchik")
        vals = ws.col_values(1) 
        nums = [int(x) for x in vals if str(x).isdigit()]
        new_no = max(nums) + 1 if nums else 1
        
        row = [
            new_no, data['KECAMATAN'], data['NAMA_CAMAT'], 
            data['KEMUKIMAN'], data['NAMA_MUKIM'], 
            data['GAMPONG'], data['NAMA_GEUCHIK']
        ]
        ws.append_row(row)
        clear_cache()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_gampong(gampong_name):
    try:
        ws = get_worksheet("Camat_Mukim_Geuchik")
        cell = ws.find(gampong_name)
        if cell and cell.col == 6: 
            ws.delete_rows(cell.row)
            clear_cache()
            return {'success': True, 'message': 'Deleted'}
        return {'success': False, 'message': 'Not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def update_perangkat_desa(desa, no_urut, field, new_value):
    try:
         ws = get_worksheet("Perangkat_Desa")
         cells = ws.findall(desa)
         for cell in cells:
             if cell.col == 8:
                 urut = ws.cell(cell.row, 11).value
                 if str(urut).strip() == str(no_urut).strip():
                     field_col_map = {'NO_DESA': 7, 'NAMA_LENGKAP': 12, 'NIK': 13, 'JENIS_KELAMIN': 14, 'JABATAN': 15, 'NO_HP': 16}
                     c_idx = field_col_map.get(field)
                     if c_idx:
                         ws.update_cell(cell.row, c_idx, new_value)
                         
                         # SYNC: Check if this was Kepala Desa
                         sync_fields = ['NO_DESA', 'NAMA_LENGKAP', 'JENIS_KELAMIN', 'JABATAN', 'NO_HP']
                         if field in sync_fields:
                             jabatan = ws.cell(cell.row, 15).value
                             if jabatan and str(jabatan).strip().upper() in ['KEPALA DESA', 'PJ. KEPALA DESA']:
                                 _sync_geuchik_data_across_files(desa, {field: new_value})
                                 
                         clear_cache()
                         return {'success': True}
         return {'success': False, 'message': 'Data Not Found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def add_kadus(data):
    """Add KADUS row to Perangkat_Desa"""
    try:
        ws = get_worksheet("Perangkat_Desa")
        target_desa = str(data['DESA']).strip()
        all_vals = ws.get_all_values()
        
        start_row_idx = -1
        last_row_idx = -1
        max_no = 0
        
        for i, row in enumerate(all_vals):
            if len(row) > 7:
                curr_desa = str(row[7]).strip()
                if curr_desa:
                     tracking_desa = curr_desa
                
                if 'tracking_desa' in locals() and tracking_desa.upper() == target_desa.upper():
                     if start_row_idx == -1: start_row_idx = i
                     last_row_idx = i
                     if len(row) > 10 and str(row[10]).isdigit():
                         max_no = max(max_no, int(row[10]))
        
        if start_row_idx == -1:
             return {'success': False, 'message': 'Desa not found'}

        insert_idx = last_row_idx + 1 
        new_row = [''] * 16 
        new_row[7] = target_desa 
        new_row[10] = max_no + 1 
        new_row[11] = data.get('NAMA_LENGKAP', '') 
        new_row[12] = data.get('NIK', '') 
        new_row[13] = data.get('JENIS_KELAMIN', 'L') 
        new_row[14] = data.get('JABATAN', 'KADUS') 
        new_row[15] = data.get('NO_HP', '') 
        
        ws.insert_row(new_row, index=insert_idx + 1)
        clear_cache()
        return {'success': True, 'message': f'Added KADUS No {max_no + 1}'}

    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_kadus(desa, no_urut):
    try:
        ws = get_worksheet("Perangkat_Desa")
        cells = ws.findall(desa)
        for cell in cells:
             if cell.col == 8:
                 urut = ws.cell(cell.row, 11).value
                 if str(urut).strip() == str(no_urut).strip():
                      ws.delete_rows(cell.row)
                      clear_cache()
                      return {'success': True}
        return {'success': False}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def update_geuchik_detail_all(desa, data):
    """Update detail Geuchik (all fields)"""
    try:
        ws = get_worksheet("Geuchik_Detail")
        if not ws: return {'success': False, 'message': 'Sheet not found'}
        
        field_col_map = {
            'NO_DESA': 7, 'NAMA_LENGKAP': 9, 'TGL_LAHIR': 10, 'BLN_LAHIR': 11,
            'THN_LAHIR': 12, 'JENIS_KELAMIN': 13, 'PENDIDIKAN': 14,
            'SK_NOMOR': 15, 'SK_TANGGAL': 16, 'JABATAN': 17, 'NO_HP': 18
        }
        
        cell = ws.find(desa)
        if cell and cell.col == 8:
            row = cell.row
            for field, value in data.items():
                col_idx = field_col_map.get(field)
                if col_idx and value is not None:
                     ws.update_cell(row, col_idx, value)
            
            # SYNC: Sync all relevant fields
            sync_fields = {}
            for k in ['NO_DESA', 'NAMA_LENGKAP', 'JENIS_KELAMIN', 'JABATAN', 'NO_HP']:
                if k in data and data[k]:
                     sync_fields[k] = data[k]
            
            if sync_fields:
                 _sync_geuchik_data_across_files(desa, sync_fields)
            
            clear_cache()
            return {'success': True}
            
        return {'success': False, 'message': 'Desa not found in Geuchik_Detail'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def update_perangkat_desa_all(desa, data_list):
    """Update multiple perangkat desa rows"""
    try:
        ws = get_worksheet("Perangkat_Desa")
        if not ws: return {'success': False, 'message': 'Sheet not found'}
        
        field_col_map = {
            'NO_DESA': 7, 'NO_URUT': 11, 'NAMA_LENGKAP': 12, 
            'NIK': 13, 'JENIS_KELAMIN': 14, 'JABATAN': 15, 'NO_HP': 16
        }
        
        cells = ws.findall(desa)
        desa_rows = {c.row: c for c in cells if c.col == 8}
        
        updated_count = 0
        sync_payload = {}
        
        for item in data_list:
            target_no = str(item.get('NO_URUT')).strip()
            target_row = None
            for r_idx in desa_rows:
                curr_no = str(ws.cell(r_idx, 11).value).strip()
                if curr_no == target_no:
                    target_row = r_idx
                    break
            
            if target_row:
                # Check Jabatan BEFORE update
                jabatan = ws.cell(target_row, 15).value
                is_kepdes = jabatan and str(jabatan).strip().upper() in ['KEPALA DESA', 'PJ. KEPALA DESA']
                
                for field, val in item.items():
                    col = field_col_map.get(field)
                    if col and val is not None:
                         ws.update_cell(target_row, col, val)
                         
                         if is_kepdes and field in ['NO_DESA', 'NAMA_LENGKAP', 'JENIS_KELAMIN', 'JABATAN', 'NO_HP']:
                             sync_payload[field] = val
                             
                updated_count += 1
        
        if sync_payload:
            _sync_geuchik_data_across_files(desa, sync_payload)
        
        clear_cache()
        return {'success': True, 'updated': updated_count}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def update_tuha_peuet_all(gampong, data_list):
    """Update multiple anggota tuha peuet"""
    try:
        ws = get_worksheet("Tuha_Peuet")
        if not ws: return {'success': False, 'message': 'Sheet not found'}
        
        cells = ws.findall(gampong)
        gampong_rows = [c.row for c in cells if c.col == 6]
        
        for item in data_list:
            target_no = str(item.get('NO_ANGGOTA')).strip()
            target_row = None
            for r in gampong_rows:
                curr = str(ws.cell(r, 7).value).strip()
                if curr == target_no:
                    target_row = r
                    break
            
            if target_row:
                if 'NAMA_ANGGOTA' in item:
                    ws.update_cell(target_row, 8, item['NAMA_ANGGOTA'])
                
                jk = item.get('JENIS_KELAMIN')
                if jk:
                    if jk == 'L':
                        ws.update_cell(target_row, 9, '✓') 
                        ws.update_cell(target_row, 10, '') 
                    elif jk == 'P':
                        ws.update_cell(target_row, 9, '')
                        ws.update_cell(target_row, 10, '✓')
                
                if 'KETERANGAN' in item:
                    ws.update_cell(target_row, 11, item['KETERANGAN'])

        clear_cache()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def add_tuha_peuet(data):
    """Add new anggota Tuha Peuet"""
    try:
        ws = get_worksheet("Tuha_Peuet")
        gampong = data.get('GAMPONG')
        
        cells = ws.findall(gampong)
        gampong_rows = [c.row for c in cells if c.col == 6]
        
        if not gampong_rows:
            return {'success': False, 'message': 'Gampong block not found'}
        
        last_row = max(gampong_rows)
        insert_idx = last_row + 1
        
        row_data = ws.row_values(last_row)
        kec = row_data[1] if len(row_data) > 1 else ''
        kem = row_data[3] if len(row_data) > 3 else ''
        
        new_row = [''] * 11
        new_row[1] = kec 
        new_row[3] = kem 
        new_row[5] = gampong 
        new_row[6] = data.get('NO_ANGGOTA') 
        new_row[7] = data.get('NAMA_ANGGOTA') 
        
        jk = data.get('JENIS_KELAMIN')
        if jk == 'L':
            new_row[8] = '✓'
        elif jk == 'P':
            new_row[9] = '✓'
            
        new_row[10] = data.get('KETERANGAN', '')
        
        ws.insert_row(new_row, index=insert_idx)
        clear_cache()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_tuha_peuet(gampong, no_anggota):
    """Delete anggota Tuha Peuet"""
    try:
        ws = get_worksheet("Tuha_Peuet")
        cells = ws.findall(gampong)
        gampong_rows = [c.row for c in cells if c.col == 6]
        
        for r in gampong_rows:
            curr_no = str(ws.cell(r, 7).value).strip()
            if curr_no == str(no_anggota).strip():
                ws.delete_rows(r)
                clear_cache()
                return {'success': True}
        return {'success': False, 'message': 'Anggota not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def update_sekretaris_tpg(gampong, no_anggota, new_nama, new_jabatan):
    """Update Secretary TPG info"""
    try:
        ws = get_worksheet("Tuha_Peuet")
        cells = ws.findall(gampong)
        target_row = None
        for cell in cells:
            if cell.col == 6:
                val = cell.value
                if val == gampong: 
                    no_anggota_val = ws.cell(cell.row, 7).value
                    if not no_anggota_val:
                        target_row = cell.row
                        break
        
        if target_row:
            ws.update_cell(target_row + 2, 6, new_jabatan)
            ws.update_cell(target_row + 3, 6, new_nama)
            clear_cache()
            return {'success': True}
        return {'success': False, 'message': 'Gampong Header not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
