"""
Data Loader Module
Sistem Manajemen Data Gampong - Dinas Pemberdayaan Kota Langsa

Module untuk memuat dan menormalisasi data dari Google Sheets.
"""

import pandas as pd
import streamlit as st
import gspread
from pathlib import Path
from google.oauth2.service_account import Credentials

# Constants
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SPREADSHEET_NAME = "Database_DPMG_Langsa"

# Path to credentials file (for local development)
CREDENTIALS_FILE = Path(__file__).parent.parent / "credentials.json"

@st.cache_resource
def get_gspread_client():
    """Get authenticated gspread client"""
    try:
        if CREDENTIALS_FILE.exists():
            creds = Credentials.from_service_account_file(
                str(CREDENTIALS_FILE), scopes=SCOPES
            )
            return gspread.authorize(creds)
        
        # Support for Streamlit Cloud Secrets (Production)
        elif "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(
                dict(st.secrets["gcp_service_account"]), scopes=SCOPES
            )
            return gspread.authorize(creds)
            
        else:
            st.error("File credentials.json tidak ditemukan dan Secrets tidak terkonfigurasi!")
            return None
    except Exception as e:
        st.error(f"Error authenticating to Google Sheets: {e}")
        return None

@st.cache_data(ttl=60)
def load_raw_data_from_sheet(sheet_name):
    """
    Load raw data from a specific worksheet in Google Sheets.
    Returns a DataFrame representing the sheet content (header=None style).
    Cached for 60 seconds to prevent API rate limits.
    """
    client = get_gspread_client()
    if not client:
        return pd.DataFrame()
    
    try:
        sh = client.open(SPREADSHEET_NAME)
        ws = sh.worksheet(sheet_name)
        data = ws.get_all_values()
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error loading sheet {sheet_name}: {e}")
        return pd.DataFrame()


def load_camat_mukim_geuchik():
    """Load data Camat, Mukim, dan Geuchik"""
    df = load_raw_data_from_sheet("Camat_Mukim_Geuchik")
    if df.empty:
        return df
        
    # In Excel, this was read with default header=0 (first row is header)
    # gspread get_all_values returns list of lists, so first row is data[0]
    # We need to promote first row to header
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    df = df.reset_index(drop=True)
    
    # Ensure numeric columns are numeric
    if 'NO' in df.columns:
        df['NO'] = pd.to_numeric(df['NO'], errors='coerce')
        
    return df


def load_geuchik_detail():
    """Load data detail Geuchik Kota Langsa"""
    # Logic copied from original: read header=None equivalent
    df = load_raw_data_from_sheet("Geuchik_Detail")
    
    if df.empty:
        return df

    try:
        # The actual data starts at row 3 (after 2 header rows in Excel, so index 2 in 0-indexed DF)
        # Previous code: df.iloc[3:] from a header=None read. 
        # Wait, if pd.read_excel(header=None), row 1 is index 0.
        # Original code: df.iloc[3:].copy() implies skipping rows 0, 1, 2.
        # Row 0: Header 1 (MERGED)
        # Row 1: Header 2 (NO, NAMA...)
        # Row 2: Header 3 (Column Numbers 1, 2, 3...)
        # Row 3: Data start
        
        columns = [
            'NO_PROV', 'PROVINSI', 'NO_KAB', 'KABUPATEN', 'NO_KEC', 'KECAMATAN',
            'NO_DESA', 'DESA', 'NAMA_LENGKAP', 'TGL_LAHIR', 'BLN_LAHIR', 'THN_LAHIR',
            'JENIS_KELAMIN', 'PENDIDIKAN', 'SK_NOMOR', 'SK_TANGGAL', 'JABATAN', 'NO_HP'
        ]
        
        # Ensure we have enough columns
        if len(df.columns) < len(columns):
            # Pad with None if read fewer columns
            for i in range(len(columns) - len(df.columns)):
                df[len(df.columns)] = None

        df_data = df.iloc[3:].copy()
        
        # Take only the first len(columns) columns to avoid mismatch
        df_data = df_data.iloc[:, :len(columns)]
        
        df_data.columns = columns
        df_data = df_data.reset_index(drop=True)
        
        return df_data
    except Exception as e:
        print(f"Error processing geuchik_detail: {e}")
        return pd.DataFrame()


def load_perangkat_desa():
    """Load data Kepala Desa dan Perangkat Desa"""
    df = load_raw_data_from_sheet("Perangkat_Desa")
    
    if df.empty:
        return df

    try:
        # Create proper column names
        columns = [
            'NO_PROV', 'PROVINSI', 'NO_KAB', 'KABUPATEN', 'NO_KEC', 'KECAMATAN',
            'NO_DESA', 'DESA', 'KATEGORI', 'JENIS', 'NO_URUT', 'NAMA_LENGKAP',
            'NIK', 'JENIS_KELAMIN', 'JABATAN', 'NO_HP'
        ]
        
        # Original: df.iloc[5:].copy() (skipping 5 header rows: 0, 1, 2, 3, 4)
        df_data = df.iloc[5:].copy()
        
        # Take only required columns
        df_data = df_data.iloc[:, :len(columns)]
        
        df_data.columns = columns
        df_data = df_data.reset_index(drop=True)
        
        # Forward fill merged cells requires treating empty strings as NaN
        import numpy as np
        df_data = df_data.replace(r'^\s*$', np.nan, regex=True)
        
        # Forward fill merged columns
        merge_columns = ['NO_PROV', 'PROVINSI', 'NO_KAB', 'KABUPATEN', 'NO_KEC', 'KECAMATAN', 'NO_DESA', 'DESA']
        for col in merge_columns:
            if col in df_data.columns:
                df_data[col] = df_data[col].ffill()
        
        # List of valid kecamatan names
        valid_kecamatan = ['LANGSA TIMUR', 'LANGSA BARAT', 'LANGSA KOTA', 
                          'LANGSA BARO', 'LANGSA LAMA']
        
        # Filter out invalid rows 
        df_data = df_data[df_data['KECAMATAN'].isin(valid_kecamatan)]
        df_data = df_data.reset_index(drop=True)
        
        # Filter out artifacts
        df_data = df_data[df_data['JABATAN'].astype(str).str.strip() != 'JABATAN']
        df_data = df_data[df_data['NO_URUT'].astype(str).str.strip() != 'NO']
        df_data = df_data.reset_index(drop=True)
        
        # Convert NO_URUT to numeric
        df_data['NO_URUT'] = pd.to_numeric(df_data['NO_URUT'], errors='coerce')
        
        return df_data
    except Exception as e:
        print(f"Error processing perangkat_desa: {e}")
        return pd.DataFrame()


def load_tuha_peuet():
    """Load data Tuha Peuet Gampong"""
    df = load_raw_data_from_sheet("Tuha_Peuet")
    
    if df.empty:
        return df

    try:
        columns = [
            'NO', 'KECAMATAN', 'NO_KEMUKIMAN', 'KEMUKIMAN', 'NO_GAMPONG', 'GAMPONG',
            'NO_ANGGOTA', 'NAMA_ANGGOTA', 'LAKI_LAKI', 'PEREMPUAN', 'KETERANGAN'
        ]
        
        # Original: df.iloc[7:] (skip 7 header rows)
        df_data = df.iloc[7:].copy()
        
        # Select columns
        df_data = df_data.iloc[:, :len(columns)]
        
        df_data.columns = columns
        df_data = df_data.reset_index(drop=True)
        
        # Filter empty rows (where NO_ANGGOTA is nan or empty string)
        import numpy as np
        df_data = df_data.replace(r'^\s*$', np.nan, regex=True)
        
        df_data = df_data[df_data['NO_ANGGOTA'].notna()].copy()
        df_data = df_data.reset_index(drop=True)
        
        # Get list of valid gampong names
        valid_gampong_rows = df_data[(df_data['GAMPONG'].notna()) & (df_data['KECAMATAN'].notna())]
        valid_gampong_names = set(valid_gampong_rows['GAMPONG'].dropna().unique())
        
        # Secretary Detection Logic (Preserved from original)
        sekretaris_info = {}
        current_gampong_name = None
        
        # Note: In pure dataframe form from CSV/Sheets, row indices are reset.
        # But here we are iterating over df_data which is sliced.
        # Original logic iterated over `range(len(df_data))`
        
        for i in range(len(df_data)):
            gampong_val = df_data.iloc[i]['GAMPONG']
            
            if pd.notna(gampong_val):
                val_str = str(gampong_val).strip()
                if val_str.isupper() and len(val_str) > 3 and "SEKRETARIS" not in val_str.upper():
                    current_gampong_name = val_str
                    
                    # Look ahead logic
                    if i + 3 < len(df_data):
                        possible_name = df_data.iloc[i + 3]['GAMPONG']
                        possible_jabatan = df_data.iloc[i + 2]['GAMPONG']
                        
                        if pd.notna(possible_name):
                            name_str = str(possible_name).strip()
                            jabatan_str = str(possible_jabatan).strip() if pd.notna(possible_jabatan) else "Sekretaris TPG"
                            
                            if not name_str.isupper():
                                sekretaris_info[current_gampong_name] = (name_str, jabatan_str)
        
        # Create columns
        df_data['JABATAN'] = 'Anggota'
        df_data['SEKRETARIS_TPG'] = None
        df_data['SEKRETARIS_JABATAN'] = None
        
        # Fill/Map Gampong for mapping
        temp_gampong_series = df_data['GAMPONG'].copy()
        for i in range(len(df_data)):
            val = df_data.iloc[i]['GAMPONG']
            if pd.notna(val):
                val_str = str(val).strip()
                if not (val_str.isupper() and "SEKRETARIS" not in val_str.upper() and len(val_str) > 3):
                     temp_gampong_series.iloc[i] = None 
        
        temp_gampong_series = temp_gampong_series.ffill()
        
        for i in range(len(df_data)):
            gampong_name = temp_gampong_series.iloc[i]
            if pd.notna(gampong_name):
                gampong_name = str(gampong_name).strip()
                if gampong_name in sekretaris_info:
                    sek_name, sek_jab = sekretaris_info[gampong_name]
                    df_data.at[i, 'SEKRETARIS_TPG'] = sek_name
                    df_data.at[i, 'SEKRETARIS_JABATAN'] = sek_jab

        # Clean GAMPONG 
        def clean_gampong(val):
            if pd.isna(val): return val
            if val in valid_gampong_names: return val
            val_str = str(val).strip()
            if val_str.isupper() and len(val_str) > 3: return val
            return None
        
        df_data['GAMPONG'] = df_data['GAMPONG'].apply(clean_gampong)
        
        # Clean KEMUKIMAN
        valid_kemukiman = set(df_data[(df_data['KEMUKIMAN'].notna()) & (df_data['KECAMATAN'].notna())]['KEMUKIMAN'].dropna().unique())
        def clean_kemukiman(val):
            if pd.isna(val): return val
            if val in valid_kemukiman: return val
            val_str = str(val).strip()
            if val_str.isupper() and len(val_str) > 3: return val
            return None
        df_data['KEMUKIMAN'] = df_data['KEMUKIMAN'].apply(clean_kemukiman)
        
        # Fill merged
        merge_columns = ['NO', 'KECAMATAN', 'NO_KEMUKIMAN', 'KEMUKIMAN', 'NO_GAMPONG', 'GAMPONG']
        for col in merge_columns:
            if col in df_data.columns:
                df_data[col] = df_data[col].ffill()
        
        valid_kecamatan = ['LANGSA TIMUR', 'LANGSA BARAT', 'LANGSA KOTA', 'LANGSA BARO', 'LANGSA LAMA']
        df_data = df_data[df_data['KECAMATAN'].isin(valid_kecamatan)]
        df_data = df_data.reset_index(drop=True)
        
        return df_data
    except Exception as e:
        print(f"Error processing tuha_peuet: {e}")
        return pd.DataFrame()


def load_all_data():
    """Load semua data dari semua file"""
    return {
        'camat_mukim_geuchik': load_camat_mukim_geuchik(),
        'geuchik_detail': load_geuchik_detail(),
        'perangkat_desa': load_perangkat_desa(),
        'tuha_peuet': load_tuha_peuet()
    }


def get_kecamatan_list():
    """Get daftar kecamatan unik"""
    df = load_camat_mukim_geuchik()
    if not df.empty:
        return sorted(df['KECAMATAN'].unique().tolist())
    return []


def get_kemukiman_list(kecamatan=None):
    """Get daftar kemukiman, opsional filter by kecamatan"""
    df = load_camat_mukim_geuchik()
    if not df.empty:
        if kecamatan:
            df = df[df['KECAMATAN'] == kecamatan]
        return sorted(df['KEMUKIMAN'].dropna().unique().tolist())
    return []


def get_gampong_list(kecamatan=None, kemukiman=None):
    """Get daftar gampong, opsional filter by kecamatan atau kemukiman"""
    df = load_camat_mukim_geuchik()
    if not df.empty:
        if kecamatan:
            df = df[df['KECAMATAN'] == kecamatan]
        if kemukiman:
            df = df[df['KEMUKIMAN'] == kemukiman]
        return sorted(df['GAMPONG'].unique().tolist())
    return []


def get_statistics():
    """Get statistik ringkasan data"""
    data = load_all_data()
    
    df1 = data['camat_mukim_geuchik']
    df3 = data['perangkat_desa']
    df4 = data['tuha_peuet']
    
    stats = {
        'total_kecamatan': df1['KECAMATAN'].nunique() if not df1.empty else 0,
        'total_kemukiman': df1['KEMUKIMAN'].nunique() if not df1.empty else 0,
        'total_gampong': df1['GAMPONG'].nunique() if not df1.empty else 0,
        'total_geuchik': len(df1) if not df1.empty else 0,
        'total_perangkat': len(df3) if not df3.empty else 0,
        'total_tuha_peuet': len(df4) if not df4.empty else 0
    }
    
    return stats


def get_data_by_kecamatan(kecamatan):
    """Get semua data untuk kecamatan tertentu"""
    data = load_all_data()
    result = {}
    
    df1 = data['camat_mukim_geuchik']
    if not df1.empty:
        result['camat_mukim_geuchik'] = df1[df1['KECAMATAN'] == kecamatan]
    
    df2 = data['geuchik_detail']
    if not df2.empty:
        result['geuchik_detail'] = df2[df2['KECAMATAN'] == kecamatan]
    
    df3 = data['perangkat_desa']
    if not df3.empty:
        result['perangkat_desa'] = df3[df3['KECAMATAN'] == kecamatan]
    
    df4 = data['tuha_peuet']
    if not df4.empty:
        result['tuha_peuet'] = df4[df4['KECAMATAN'] == kecamatan]
    
    return result
