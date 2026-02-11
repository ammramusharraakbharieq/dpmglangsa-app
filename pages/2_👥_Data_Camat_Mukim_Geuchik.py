"""
Data Camat, Mukim, dan Geuchik Page
Sistem Manajemen Data Gampong - DPMG Langsa
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_camat_mukim_geuchik, get_kecamatan_list, 
    get_kemukiman_list, get_gampong_list
)
from utils.data_manager import (
    update_geuchik_name, update_camat_name, update_mukim_name,
    add_gampong, delete_gampong
)
from utils.auth import is_admin

# Page config
st.set_page_config(
    page_title="Data Camat/Mukim/Geuchik - DPMG Langsa",
    page_icon="👥",
    layout="wide"
)

# Check authentication
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Anda harus login terlebih dahulu untuk mengakses halaman ini.")
    st.markdown("[🔐 Kembali ke Halaman Login](/)")
    st.stop()

# Check if user is admin
user_is_admin = is_admin(st.session_state.get('role'))

# Load custom CSS
def load_css():
    css_file = Path(__file__).parent.parent / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Title
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="color: #3498DB;">👥 Data Camat, Mukim, dan Geuchik</h1>
    <p style="color: #BDC3C7;">Kelola data pejabat pemerintahan gampong</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Load data
df = load_camat_mukim_geuchik()

# Tabs - show edit/add only for admin
if user_is_admin:
    tab_view, tab_edit, tab_add = st.tabs(["📋 Lihat Data", "✏️ Edit Data", "➕ Tambah Data"])
else:
    tab_view = st.tabs(["📋 Lihat Data"])[0]

with tab_view:
    st.subheader("📋 Data Camat, Mukim, dan Geuchik")
    
    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        kecamatan_options = ['Semua'] + get_kecamatan_list()
        filter_kecamatan = st.selectbox("Filter Kecamatan", kecamatan_options, key="view_kec")
    
    with col_f2:
        if filter_kecamatan != 'Semua':
            kemukiman_options = ['Semua'] + get_kemukiman_list(filter_kecamatan)
        else:
            kemukiman_options = ['Semua'] + get_kemukiman_list()
        filter_kemukiman = st.selectbox("Filter Kemukiman", kemukiman_options, key="view_kem")
    
    with col_f3:
        search_text = st.text_input("🔍 Cari (Nama Geuchik/Gampong)", key="search_view")
    
    # Apply filters
    filtered_df = df.copy()
    
    if filter_kecamatan != 'Semua':
        filtered_df = filtered_df[filtered_df['KECAMATAN'] == filter_kecamatan]
    
    if filter_kemukiman != 'Semua':
        filtered_df = filtered_df[filtered_df['KEMUKIMAN'] == filter_kemukiman]
    
    if search_text:
        mask = (
            filtered_df['NAMA GEUCHIK'].str.contains(search_text, case=False, na=False) |
            filtered_df['GAMPONG'].str.contains(search_text, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Display data
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "NO": st.column_config.NumberColumn("No", width="small"),
            "KECAMATAN": st.column_config.TextColumn("Kecamatan", width="medium"),
            "NAMA CAMAT": st.column_config.TextColumn("Nama Camat", width="large"),
            "KEMUKIMAN": st.column_config.TextColumn("Kemukiman", width="medium"),
            "NAMA MUKIM": st.column_config.TextColumn("Nama Mukim", width="medium"),
            "GAMPONG": st.column_config.TextColumn("Gampong", width="medium"),
            "NAMA GEUCHIK": st.column_config.TextColumn("Nama Geuchik", width="large"),
        }
    )
    
    st.info(f"📊 Menampilkan {len(filtered_df)} dari {len(df)} data")

# Admin-only tabs
if user_is_admin:
    with tab_edit:
        st.subheader("✏️ Edit Data")
        
        edit_type = st.radio(
            "Pilih jenis data yang akan diedit:",
            ["Nama Geuchik", "Nama Camat", "Nama Mukim"],
            horizontal=True
        )
        
        if edit_type == "Nama Geuchik":
            st.markdown("""
            <div style="padding: 10px; background: rgba(52, 152, 219, 0.1); border-radius: 8px; border-left: 3px solid #3498DB; margin-bottom: 20px;">
                <p style="color: #E0E0E0; margin: 0;"><strong>ℹ️ Integrasi Cross-File</strong><br>
                <span style="color: #BDC3C7;">Perubahan nama Geuchik akan otomatis diupdate di File 1, 2, dan 3</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            col_e1, col_e2 = st.columns(2)
            
            with col_e1:
                # Select gampong
                gampong_list = get_gampong_list()
                selected_gampong = st.selectbox("Pilih Gampong", gampong_list, key="edit_gampong")
                
                # Get current geuchik name
                if selected_gampong:
                    current_data = df[df['GAMPONG'] == selected_gampong]
                    if not current_data.empty:
                        current_name = current_data.iloc[0]['NAMA GEUCHIK']
                        st.info(f"Nama Geuchik saat ini: **{current_name}**")
            
            with col_e2:
                new_name = st.text_input("Nama Geuchik Baru", key="new_geuchik_name")
            
            if st.button("💾 Simpan Perubahan Geuchik", type="primary"):
                if selected_gampong and new_name:
                    result = update_geuchik_name(selected_gampong, current_name, new_name)
                    
                    success_count = sum(1 for r in result.values() if r.get('updated'))
                    if success_count > 0:
                        st.success(f"✅ Berhasil update data di {success_count} file!")
                        for file_key, res in result.items():
                            if res.get('updated'):
                                st.write(f"  - {file_key}: {res['rows']} baris diupdate")
                        st.rerun()
                    else:
                        st.warning("⚠️ Tidak ada data yang diupdate")
                else:
                    st.error("❌ Mohon lengkapi semua field")
        
        elif edit_type == "Nama Camat":
            col_e1, col_e2 = st.columns(2)
            
            with col_e1:
                kecamatan_list = get_kecamatan_list()
                selected_kecamatan = st.selectbox("Pilih Kecamatan", kecamatan_list, key="edit_kec")
                
                if selected_kecamatan:
                    current_data = df[df['KECAMATAN'] == selected_kecamatan]
                    if not current_data.empty:
                        current_camat = current_data.iloc[0]['NAMA CAMAT']
                        st.info(f"Nama Camat saat ini: **{current_camat}**")
            
            with col_e2:
                new_camat_name = st.text_input("Nama Camat Baru", key="new_camat_name")
            
            if st.button("💾 Simpan Perubahan Camat", type="primary"):
                if selected_kecamatan and new_camat_name:
                    result = update_camat_name(selected_kecamatan, current_camat, new_camat_name)
                    if result.get('success'):
                        st.success(f"✅ Berhasil update {result['rows']} baris!")
                        st.rerun()
                    else:
                        st.error(f"❌ Gagal: {result.get('error', result.get('message'))}")
                else:
                    st.error("❌ Mohon lengkapi semua field")
        
        elif edit_type == "Nama Mukim":
            col_e1, col_e2 = st.columns(2)
            
            with col_e1:
                kemukiman_list = get_kemukiman_list()
                selected_kemukiman = st.selectbox("Pilih Kemukiman", kemukiman_list, key="edit_kem")
                
                if selected_kemukiman:
                    current_data = df[df['KEMUKIMAN'] == selected_kemukiman]
                    if not current_data.empty:
                        current_mukim = current_data.iloc[0]['NAMA MUKIM']
                        st.info(f"Nama Mukim saat ini: **{current_mukim}**")
            
            with col_e2:
                new_mukim_name = st.text_input("Nama Mukim Baru", key="new_mukim_name")
            
            if st.button("💾 Simpan Perubahan Mukim", type="primary"):
                if selected_kemukiman and new_mukim_name:
                    result = update_mukim_name(selected_kemukiman, current_mukim, new_mukim_name)
                    if result.get('success'):
                        st.success(f"✅ Berhasil update {result['rows']} baris!")
                        st.rerun()
                    else:
                        st.error(f"❌ Gagal: {result.get('error', result.get('message'))}")
                else:
                    st.error("❌ Mohon lengkapi semua field")

    with tab_add:
        st.subheader("➕ Tambah Data Gampong Baru")
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            add_kecamatan = st.selectbox("Kecamatan", get_kecamatan_list(), key="add_kec")
            add_kemukiman = st.text_input("Kemukiman", key="add_kem")
            add_gampong_name = st.text_input("Nama Gampong", key="add_gampong")
        
        with col_a2:
            # Get existing camat name for selected kecamatan
            if add_kecamatan:
                existing_camat = df[df['KECAMATAN'] == add_kecamatan]['NAMA CAMAT'].iloc[0] if not df[df['KECAMATAN'] == add_kecamatan].empty else ""
                add_camat = st.text_input("Nama Camat", value=existing_camat, key="add_camat")
            else:
                add_camat = st.text_input("Nama Camat", key="add_camat")
            
            add_mukim = st.text_input("Nama Mukim", key="add_mukim")
            add_geuchik = st.text_input("Nama Geuchik", key="add_geuchik")
        
        if st.button("➕ Tambah Data", type="primary"):
            if add_kecamatan and add_kemukiman and add_gampong_name and add_camat and add_mukim and add_geuchik:
                data = {
                    'KECAMATAN': add_kecamatan,
                    'NAMA_CAMAT': add_camat,
                    'KEMUKIMAN': add_kemukiman,
                    'NAMA_MUKIM': add_mukim,
                    'GAMPONG': add_gampong_name,
                    'NAMA_GEUCHIK': add_geuchik
                }
                result = add_gampong(data)
                if result.get('success'):
                    st.success("✅ Data berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error(f"❌ Gagal: {result.get('error', result.get('message'))}")
            else:
                st.error("❌ Mohon lengkapi semua field")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <p style="color: #7F8C8D; font-size: 0.8em;">Data Camat, Mukim, Geuchik - Sistem Manajemen Data Gampong DPMG Langsa</p>
</div>
""", unsafe_allow_html=True)
