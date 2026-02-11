"""
Data Geuchik Detail Page
Sistem Manajemen Data Gampong - DPMG Langsa
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_geuchik_detail, get_kecamatan_list
from utils.data_manager import update_geuchik_detail_all
from utils.auth import is_admin

# Page config
st.set_page_config(
    page_title="Data Geuchik Detail - DPMG Langsa",
    page_icon="📋",
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
    <h1 style="color: #3498DB;">📋 Data Detail Geuchik</h1>
    <p style="color: #BDC3C7;">Informasi lengkap Geuchik/Kepala Desa Kota Langsa</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Load data
df = load_geuchik_detail()

if not df.empty:
    # Tabs - show edit only for admin
    if user_is_admin:
        tab_view, tab_filter, tab_edit = st.tabs(["📋 Lihat Data", "🔍 Filter & Cari", "✏️ Edit Data"])
    else:
        tab_view, tab_filter = st.tabs(["📋 Lihat Data", "🔍 Filter & Cari"])
    
    with tab_view:
        st.subheader("📋 Data Lengkap Geuchik Kota Langsa")
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Data", len(df))
        with col2:
            kec_count = df['KECAMATAN'].nunique()
            st.metric("Kecamatan", kec_count)
        with col3:
            jabatan_count = df['JABATAN'].value_counts()
            st.metric("Kepala Desa Definitif", jabatan_count.get('KEPALA DESA', 0))
        
        st.markdown("---")
        
        # Simplified column names for display
        display_df = df[['KECAMATAN', 'DESA', 'NAMA_LENGKAP', 'JABATAN', 'NO_HP']].copy()
        display_df.columns = ['Kecamatan', 'Desa', 'Nama Lengkap', 'Jabatan', 'No HP']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    
    with tab_filter:
        st.subheader("🔍 Filter Data")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            kecamatan_options = ['Semua'] + sorted([str(x) for x in df['KECAMATAN'].dropna().unique().tolist()])
            selected_kec = st.selectbox("Kecamatan", kecamatan_options)
        
        with col_f2:
            jabatan_options = ['Semua'] + sorted([str(x) for x in df['JABATAN'].dropna().unique().tolist()])
            selected_jabatan = st.selectbox("Jabatan", jabatan_options)
        
        with col_f3:
            search = st.text_input("🔍 Cari Nama/Desa")
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_kec != 'Semua':
            filtered_df = filtered_df[filtered_df['KECAMATAN'].astype(str) == selected_kec]
        
        if selected_jabatan != 'Semua':
            filtered_df = filtered_df[filtered_df['JABATAN'].astype(str) == selected_jabatan]
        
        if search:
            mask = (
                filtered_df['NAMA_LENGKAP'].str.contains(search, case=False, na=False) |
                filtered_df['DESA'].str.contains(search, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        # Display filtered data
        display_filtered = filtered_df[['KECAMATAN', 'DESA', 'NAMA_LENGKAP', 'JABATAN', 'NO_HP']].copy()
        display_filtered.columns = ['Kecamatan', 'Desa', 'Nama Lengkap', 'Jabatan', 'No HP']
        
        st.dataframe(display_filtered, use_container_width=True, hide_index=True)
        st.info(f"📊 Menampilkan {len(filtered_df)} dari {len(df)} data")
    
    # Admin-only edit tab
    if user_is_admin:
        with tab_edit:
            st.subheader("✏️ Edit Data Geuchik")
            
            st.markdown("""
            <div style="padding: 10px; background: rgba(52, 152, 219, 0.1); border-radius: 8px; border-left: 3px solid #3498DB; margin-bottom: 20px;">
                <p style="color: #E0E0E0; margin: 0;"><strong>🔄 Sinkronisasi Cross-File</strong><br>
                <span style="color: #BDC3C7;">Perubahan <strong>Nama, Jenis Kelamin, Jabatan, dan No HP</strong> akan otomatis disinkronkan ke menu Data Camat/Mukim/Geuchik & Data Kepala Desa/Perangkat Desa</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Select Desa
            desa_list = sorted([str(x) for x in df['DESA'].dropna().unique().tolist()])
            selected_desa = st.selectbox("🔍 Pilih Desa untuk diedit", desa_list, key="edit_desa")
            
            # Show edit form for selected desa
            if selected_desa:
                current_data = df[df['DESA'].astype(str) == selected_desa]
                if not current_data.empty:
                    row = current_data.iloc[0]
                    
                    # Use unique key prefix based on selected desa to force refresh
                    key_prefix = f"edit_{selected_desa.replace(' ', '_')}"
                    
                    st.markdown("---")
                    st.markdown("### 📝 Form Edit Data")
                    
                    st.markdown("""
                    <div style="padding: 10px; background: rgba(52, 152, 219, 0.1); border-radius: 8px; border-left: 3px solid #3498DB; margin-bottom: 20px;">
                        <p style="color: #E0E0E0; margin: 0;"><strong>ℹ️ Kecamatan:</strong> {} | <strong>Desa:</strong> {}</p>
                    </div>
                    """.format(row.get('KECAMATAN', '-'), row.get('DESA', '-')), unsafe_allow_html=True)
                    
                    # Get current values
                    current_kode = str(row.get('NO_DESA', '')) if pd.notna(row.get('NO_DESA')) else ''
                    current_nama = str(row.get('NAMA_LENGKAP', '')) if pd.notna(row.get('NAMA_LENGKAP')) else ''
                    current_tgl = str(row.get('TGL_LAHIR', '')) if pd.notna(row.get('TGL_LAHIR')) else ''
                    current_bln = str(row.get('BLN_LAHIR', '')) if pd.notna(row.get('BLN_LAHIR')) else ''
                    current_thn = str(row.get('THN_LAHIR', '')) if pd.notna(row.get('THN_LAHIR')) else ''
                    current_jk = str(row.get('JENIS_KELAMIN', 'L')) if pd.notna(row.get('JENIS_KELAMIN')) else 'L'
                    current_pendidikan = str(row.get('PENDIDIKAN', '')) if pd.notna(row.get('PENDIDIKAN')) else ''
                    current_sk_nomor = str(row.get('SK_NOMOR', '')) if pd.notna(row.get('SK_NOMOR')) else ''
                    current_sk_tanggal = str(row.get('SK_TANGGAL', '')) if pd.notna(row.get('SK_TANGGAL')) else ''
                    current_jabatan = str(row.get('JABATAN', '')) if pd.notna(row.get('JABATAN')) else ''
                    current_hp = str(row.get('NO_HP', '')) if pd.notna(row.get('NO_HP')) else ''
                    
                    # Form dengan semua field - using unique keys per desa
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Kode Desa
                        edit_kode_desa = st.text_input(
                            "📍 Kode Desa (Kolom 7)", 
                            value=current_kode,
                            key=f"{key_prefix}_kode_desa"
                        )
                        
                        # Nama Lengkap
                        edit_nama = st.text_input(
                            "👤 Nama Lengkap (Kolom 9)", 
                            value=current_nama,
                            key=f"{key_prefix}_nama"
                        )
                        
                        # Tanggal Lahir (Opsional)
                        st.markdown("**🎂 Kelahiran (Kolom 10, 11, 12)** - *Opsional*")
                        col_tgl, col_bln, col_thn = st.columns(3)
                        with col_tgl:
                            edit_tgl = st.text_input("Tanggal", value=current_tgl, placeholder="DD", key=f"{key_prefix}_tgl")
                        with col_bln:
                            edit_bln = st.text_input("Bulan", value=current_bln, placeholder="MM", key=f"{key_prefix}_bln")
                        with col_thn:
                            edit_thn = st.text_input("Tahun", value=current_thn, placeholder="YYYY", key=f"{key_prefix}_thn")
                        
                        # Jenis Kelamin
                        jk_options = ['L', 'P']
                        jk_index = jk_options.index(current_jk) if current_jk in jk_options else 0
                        edit_jk = st.selectbox(
                            "⚧ Jenis Kelamin (Kolom 13)",
                            options=jk_options,
                            format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan',
                            index=jk_index,
                            key=f"{key_prefix}_jk"
                        )
                    
                    with col2:
                        # Pendidikan
                        pendidikan_options = ['', 'SD', 'SMP', 'SMA', 'D1', 'D3', 'D4', 'S1', 'S2', 'S3']
                        pend_index = pendidikan_options.index(current_pendidikan) if current_pendidikan in pendidikan_options else 0
                        edit_pendidikan = st.selectbox(
                            "🎓 Pendidikan (Kolom 14)",
                            options=pendidikan_options,
                            index=pend_index,
                            key=f"{key_prefix}_pendidikan"
                        )
                        
                        # SK Pengangkatan
                        st.markdown("**📜 SK Pengangkatan (Kolom 15, 16)**")
                        edit_sk_nomor = st.text_input("Nomor SK", value=current_sk_nomor, key=f"{key_prefix}_sk_nomor")
                        edit_sk_tanggal = st.text_input("Tanggal SK", value=current_sk_tanggal, key=f"{key_prefix}_sk_tanggal")
                        
                        # Jabatan
                        jabatan_options = ['KEPALA DESA', 'PJ. KEPALA DESA']
                        jab_index = jabatan_options.index(current_jabatan) if current_jabatan in jabatan_options else 0
                        edit_jabatan = st.selectbox(
                            "🏛️ Jabatan (Kolom 17)",
                            options=jabatan_options,
                            index=jab_index,
                            key=f"{key_prefix}_jabatan"
                        )
                        
                        # No HP
                        edit_hp = st.text_input(
                            "📱 No HP (Kolom 18)", 
                            value=current_hp,
                            key=f"{key_prefix}_hp"
                        )
                    
                    st.markdown("---")
                    
                    # Save button
                    if st.button("💾 Simpan Semua Perubahan", type="primary", use_container_width=True):
                        # Prepare data dict - format dates with zero padding if provided
                        tgl_formatted = None
                        bln_formatted = None
                        thn_formatted = None
                        
                        if edit_tgl.strip():
                            try:
                                tgl_formatted = f"{int(edit_tgl):02d}"  # Format: 01, 02, ... 31
                            except ValueError:
                                tgl_formatted = edit_tgl
                        
                        if edit_bln.strip():
                            try:
                                bln_formatted = f"{int(edit_bln):02d}"  # Format: 01, 02, ... 12
                            except ValueError:
                                bln_formatted = edit_bln
                        
                        if edit_thn.strip():
                            thn_formatted = edit_thn
                        
                        update_data = {
                            'NO_DESA': edit_kode_desa if edit_kode_desa else None,
                            'NAMA_LENGKAP': edit_nama if edit_nama else None,
                            'TGL_LAHIR': tgl_formatted,
                            'BLN_LAHIR': bln_formatted,
                            'THN_LAHIR': thn_formatted,
                            'JENIS_KELAMIN': edit_jk,
                            'PENDIDIKAN': edit_pendidikan if edit_pendidikan else None,
                            'SK_NOMOR': edit_sk_nomor if edit_sk_nomor else None,
                            'SK_TANGGAL': edit_sk_tanggal if edit_sk_tanggal else None,
                            'JABATAN': edit_jabatan,
                            'NO_HP': edit_hp if edit_hp else None
                        }
                        
                        result = update_geuchik_detail_all(selected_desa, update_data)
                        if result.get('success'):
                            st.success("✅ Semua data berhasil diupdate!")
                            st.rerun()
                        else:
                            st.error(f"❌ Gagal: {result.get('error', result.get('message'))}")

else:
    st.warning("⚠️ Tidak dapat memuat data. Pastikan file Excel tersedia.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <p style="color: #7F8C8D; font-size: 0.8em;">Data Geuchik Detail - Sistem Manajemen Data Gampong DPMG Langsa</p>
</div>
""", unsafe_allow_html=True)
