"""
Data Perangkat Desa Page
Sistem Manajemen Data Gampong - DPMG Langsa
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_perangkat_desa
from utils.data_manager import update_perangkat_desa_all, add_kadus, delete_kadus
from utils.auth import is_admin

# Page config
st.set_page_config(
    page_title="Data Perangkat Desa - DPMG Langsa",
    page_icon="🏛️",
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
    <h1 style="color: #3498DB;">🏛️ Data Kepala Desa & Perangkat Desa</h1>
    <p style="color: #BDC3C7;">Kelola data perangkat pemerintahan desa</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Jabatan yang tidak bisa diedit (sudah default/terintegrasi)
JABATAN_READONLY = ['KEPALA DESA', 'PJ. KEPALA DESA', 'SEKRETARIS DESA', 
                    'KASI PEMERINTAHAN', 'KASI PELAYANAN', 'KASI KESEJAHTERAAN',
                    'KAUR KEUANGAN', 'KAUR UMUM', 'KAUR PERENCANAAN']

# Load data
df = load_perangkat_desa()

if not df.empty:
    # Tabs - show edit/add/delete only for admin
    if user_is_admin:
        tab_view, tab_edit, tab_add, tab_delete = st.tabs(["📋 Lihat Data", "✏️ Edit Data", "➕ Tambah KADUS", "🗑️ Hapus KADUS"])
    else:
        tab_view = st.tabs(["📋 Lihat Data"])[0]
    
    with tab_view:
        st.subheader("📋 Data Kepala Desa & Perangkat Desa")
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Data", len(df))
        with col2:
            kec_count = df['KECAMATAN'].nunique()
            st.metric("Kecamatan", kec_count)
        with col3:
            desa_count = df['DESA'].nunique()
            st.metric("Desa", desa_count)
        with col4:
            jabatan_count = df['JABATAN'].nunique()
            st.metric("Jenis Jabatan", jabatan_count)
        
        st.markdown("---")
        
        # Filters
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            kecamatan_options = ['Semua'] + sorted([str(x) for x in df['KECAMATAN'].dropna().unique().tolist()])
            selected_kec = st.selectbox("Filter Kecamatan", kecamatan_options, key="view_kec")
        
        with col_f2:
            if selected_kec != 'Semua':
                desa_options = ['Semua'] + sorted([str(x) for x in df[df['KECAMATAN'].astype(str) == selected_kec]['DESA'].dropna().unique().tolist()])
            else:
                desa_options = ['Semua'] + sorted([str(x) for x in df['DESA'].dropna().unique().tolist()])
            selected_desa = st.selectbox("Filter Desa", desa_options, key="view_desa")
        
        with col_f3:
            jabatan_options = ['Semua'] + sorted([str(x) for x in df['JABATAN'].dropna().unique().tolist()])
            selected_jabatan = st.selectbox("Filter Jabatan", jabatan_options, key="view_jabatan")
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_kec != 'Semua':
            filtered_df = filtered_df[filtered_df['KECAMATAN'].astype(str) == selected_kec]
        
        if selected_desa != 'Semua':
            filtered_df = filtered_df[filtered_df['DESA'].astype(str) == selected_desa]
        
        if selected_jabatan != 'Semua':
            filtered_df = filtered_df[filtered_df['JABATAN'].astype(str) == selected_jabatan]
        
        # Search
        search = st.text_input("🔍 Cari Nama", key="search_view")
        if search:
            filtered_df = filtered_df[filtered_df['NAMA_LENGKAP'].str.contains(search, case=False, na=False)]
        
        # Display data
        display_df = filtered_df[['KECAMATAN', 'DESA', 'NO_URUT', 'NAMA_LENGKAP', 'JABATAN', 'NO_HP']].copy()
        display_df.columns = ['Kecamatan', 'Desa', 'No', 'Nama Lengkap', 'Jabatan', 'No HP']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.info(f"📊 Menampilkan {len(filtered_df)} dari {len(df)} data")
    
    # Edit, Add, Delete tabs only for admin
    if user_is_admin:
        with tab_edit:
            st.subheader("✏️ Edit Data Perangkat Desa")
            
            # Info box
            st.markdown("""
            <div style="padding: 10px; background: rgba(52, 152, 219, 0.1); border-radius: 8px; border-left: 3px solid #3498DB; margin-bottom: 20px;">
                <p style="color: #E0E0E0; margin: 0;"><strong>ℹ️ Keterangan:</strong></p>
                <ul style="color: #BDC3C7; margin: 5px 0;">
                    <li><strong>KEPALA DESA/PJ. KEPALA DESA</strong> - 🔄 Data tersinkron otomatis dengan menu Data Camat/Mukim/Geuchik & Data Detail Geuchik</li>
                    <li><strong>Perangkat Inti</strong> (Sekretaris, Kasi, Kaur) - Jabatan sudah default, hanya edit NIK & Nama</li>
                    <li><strong>KADUS</strong> - Dapat diedit sepenuhnya termasuk jabatan</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Select Desa
            desa_list = sorted([str(x) for x in df['DESA'].dropna().unique().tolist()])
            edit_desa = st.selectbox("🔍 Pilih Desa untuk diedit", desa_list, key="edit_desa_select")
            
            if edit_desa:
                # Get all perangkat for this desa
                desa_df = df[df['DESA'].astype(str) == edit_desa].copy()
                desa_df = desa_df.sort_values('NO_URUT')
                
                key_prefix = f"edit_{edit_desa.replace(' ', '_')}"
                
                st.markdown("---")
                st.markdown(f"### 📝 Data Perangkat Desa: **{edit_desa}**")
                
                # Get kode desa (NO_DESA)
                current_kode_desa = str(desa_df.iloc[0]['NO_DESA']) if not desa_df.empty and pd.notna(desa_df.iloc[0]['NO_DESA']) else ''
                
                # Kode Desa (editable for all)
                st.markdown("#### 📍 Kode Desa (Kolom 7)")
                new_kode_desa = st.text_input(
                    "Kode Desa (berlaku untuk semua perangkat di desa ini)",
                    value=current_kode_desa,
                    key=f"{key_prefix}_kode_desa"
                )
                
                st.markdown("---")
                st.markdown("#### 👥 Data Perangkat")
                
                # Store edited data
                edited_data = []
                
                # Use form to capture all inputs properly
                with st.form(key=f"edit_form_{key_prefix}"):
                    for idx, row in desa_df.iterrows():
                        no_urut = row['NO_URUT']
                        jabatan = str(row['JABATAN']) if pd.notna(row['JABATAN']) else ''
                        nama = str(row['NAMA_LENGKAP']) if pd.notna(row['NAMA_LENGKAP']) else ''
                        nik = str(row['NIK']) if pd.notna(row['NIK']) else ''
                        jk = str(row['JENIS_KELAMIN']) if pd.notna(row['JENIS_KELAMIN']) else 'L'
                        no_hp = str(row['NO_HP']) if pd.notna(row['NO_HP']) else ''
                        
                        is_kepala = jabatan.upper() in ['KEPALA DESA', 'PJ. KEPALA DESA']
                        is_kadus = 'KADUS' in jabatan.upper()
                        is_readonly_jabatan = jabatan.upper() in [j.upper() for j in JABATAN_READONLY]
                        
                        # Create unique key for each row using index
                        row_key = f"{key_prefix}_{idx}_{no_urut}"
                        
                        with st.expander(f"**{no_urut}. {nama if nama else '-'}** - {jabatan}", expanded=False):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Nama Lengkap - editable for all including Kepala Desa
                                new_nama = st.text_input("👤 Nama Lengkap", value=nama, key=f"{row_key}_nama",
                                                        help="🔄 Data Kepala Desa tersinkron otomatis" if is_kepala else None)
                                
                                # NIK
                                new_nik = st.text_input("🆔 NIK (Kolom 13)", value=nik, key=f"{row_key}_nik")
                            
                            with col2:
                                # Jenis Kelamin - editable for all including Kepala Desa
                                jk_options = ['L', 'P']
                                jk_idx = jk_options.index(jk) if jk in jk_options else 0
                                new_jk = st.selectbox("⚧ Jenis Kelamin (Kolom 14)", options=jk_options,
                                                     format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan',
                                                     index=jk_idx, key=f"{row_key}_jk",
                                                     help="🔄 Data Kepala Desa tersinkron otomatis" if is_kepala else None)
                                
                                # Jabatan - readonly for Kepala Desa and perangkat inti
                                if is_kepala or (not is_kadus and is_readonly_jabatan):
                                    st.text_input("🏛️ Jabatan", value=jabatan, disabled=True,
                                                 help="Jabatan tidak dapat diubah",
                                                 key=f"{row_key}_jabatan_disabled")
                                    new_jabatan = jabatan  # Keep original
                                else:
                                    # KADUS can edit jabatan
                                    new_jabatan = st.text_input("🏛️ Jabatan (Kolom 15)", value=jabatan, key=f"{row_key}_jabatan")
                                
                                # No HP - editable for all including Kepala Desa
                                new_hp = st.text_input("📱 No HP (Kolom 16)", value=no_hp, key=f"{row_key}_hp",
                                                      help="🔄 Data Kepala Desa tersinkron otomatis" if is_kepala else None)
                            
                            edited_data.append({
                                'NO_URUT': no_urut,
                                'NAMA_LENGKAP': new_nama,
                                'NIK': new_nik,
                                'JENIS_KELAMIN': new_jk,
                                'JABATAN': new_jabatan,
                                'NO_HP': new_hp,
                                'NO_DESA': new_kode_desa
                            })
                    
                    st.markdown("---")
                    
                    # Save button inside form
                    submitted = st.form_submit_button("💾 Simpan Semua Perubahan", type="primary", use_container_width=True)
                    
                    if submitted:
                        result = update_perangkat_desa_all(edit_desa, edited_data)
                        if result.get('success'):
                            st.success("✅ Semua data berhasil diupdate!")
                            st.rerun()
                        else:
                            st.error(f"❌ Gagal: {result.get('error', result.get('message'))}")

    # Indent ADD and DELETE tabs to be under user_is_admin check
    if user_is_admin:
        with tab_add:
            st.subheader("➕ Tambah Data KADUS Baru")
            
            st.markdown("""
            <div style="padding: 10px; background: rgba(46, 204, 113, 0.1); border-radius: 8px; border-left: 3px solid #2ECC71; margin-bottom: 20px;">
                <p style="color: #E0E0E0; margin: 0;"><strong>ℹ️ Tambah KADUS</strong><br>
                <span style="color: #BDC3C7;">Gunakan fitur ini untuk menambahkan Kepala Dusun (KADUS) yang belum terdata.</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Select Desa
            desa_list = sorted([str(x) for x in df['DESA'].dropna().unique().tolist()])
            add_desa = st.selectbox("🔍 Pilih Desa", desa_list, key="add_desa_select")
            
            if add_desa:
                desa_df = df[df['DESA'].astype(str) == add_desa]
                kec = str(desa_df.iloc[0]['KECAMATAN']) if not desa_df.empty else ''
                kode_desa = str(desa_df.iloc[0]['NO_DESA']) if not desa_df.empty and pd.notna(desa_df.iloc[0]['NO_DESA']) else ''
                
                # Get max NO_URUT (convert to numeric to handle mixed int/str types)
                max_urut = pd.to_numeric(desa_df['NO_URUT'], errors='coerce').max() if not desa_df.empty else 0
                next_urut = int(max_urut) + 1 if pd.notna(max_urut) else 1
                
                st.markdown(f"**Kecamatan:** {kec} | **Desa:** {add_desa}")
                st.markdown(f"**No Urut berikutnya:** {next_urut}")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    add_nama = st.text_input("👤 Nama Lengkap KADUS", key="add_nama")
                    add_nik = st.text_input("🆔 NIK", key="add_nik")
                
                with col2:
                    add_jk = st.selectbox("⚧ Jenis Kelamin", options=['L', 'P'],
                                         format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan',
                                         key="add_jk")
                    add_jabatan = st.text_input("🏛️ Jabatan (contoh: KADUS I, KADUS LORONG)", 
                                               value="KADUS", key="add_jabatan")
                    add_hp = st.text_input("📱 No HP", key="add_hp")
                
                if st.button("➕ Tambah KADUS", type="primary"):
                    if add_nama and add_jabatan:
                        kadus_data = {
                            'KECAMATAN': kec,
                            'DESA': add_desa,
                            'NO_DESA': kode_desa,
                            'NO_URUT': next_urut,
                            'NAMA_LENGKAP': add_nama,
                            'NIK': add_nik,
                            'JENIS_KELAMIN': add_jk,
                            'JABATAN': add_jabatan,
                            'NO_HP': add_hp
                        }
                        result = add_kadus(kadus_data)
                        if result.get('success'):
                            st.success("✅ KADUS berhasil ditambahkan!")
                            st.rerun()
                        else:
                            st.error(f"❌ Gagal: {result.get('error', result.get('message'))}")
                    else:
                        st.error("❌ Nama dan Jabatan wajib diisi")
        
        with tab_delete:
            st.subheader("🗑️ Hapus Data KADUS")
            
            st.markdown("""
            <div style="padding: 10px; background: rgba(231, 76, 60, 0.1); border-radius: 8px; border-left: 3px solid #E74C3C; margin-bottom: 20px;">
                <p style="color: #E0E0E0; margin: 0;"><strong>⚠️ Perhatian:</strong><br>
                <span style="color: #BDC3C7;">Fitur ini hanya untuk menghapus data KADUS (Kepala Dusun). Data KEPALA DESA dan perangkat inti tidak dapat dihapus.</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Select Desa
            del_desa = st.selectbox("🔍 Pilih Desa", desa_list, key="del_desa_select")
            
            if del_desa:
                desa_df = df[df['DESA'].astype(str) == del_desa]
                
                # Filter only KADUS
                kadus_df = desa_df[desa_df['JABATAN'].str.contains('KADUS', case=False, na=False)]
                
                if not kadus_df.empty:
                    st.markdown(f"**Daftar KADUS di {del_desa}:**")
                    
                    # Display KADUS list
                    for idx, row in kadus_df.iterrows():
                        no_urut = row['NO_URUT']
                        nama = str(row['NAMA_LENGKAP']) if pd.notna(row['NAMA_LENGKAP']) else '-'
                        jabatan = str(row['JABATAN']) if pd.notna(row['JABATAN']) else '-'
                        
                        with st.expander(f"**{no_urut}. {nama}** - {jabatan}"):
                            st.write(f"👤 Nama: **{nama}**")
                            st.write(f"🏛️ Jabatan: **{jabatan}**")
                            st.write(f"📱 No HP: **{row.get('NO_HP', '-')}**")
                            
                            # Confirmation checkbox
                            confirm_key = f"confirm_del_{del_desa}_{no_urut}"
                            confirm = st.checkbox(f"Saya yakin ingin menghapus {nama}", key=confirm_key)
                            
                            if confirm:
                                if st.button(f"🗑️ Hapus {nama}", type="primary", key=f"btn_del_{del_desa}_{no_urut}"):
                                    result = delete_kadus(del_desa, no_urut)
                                    if result.get('success'):
                                        st.success("✅ KADUS berhasil dihapus!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Gagal: {result.get('error', result.get('message'))}")
                else:
                    st.info("ℹ️ Tidak ada KADUS di desa ini")

else:
    st.warning("⚠️ Tidak dapat memuat data. Pastikan file Excel tersedia.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <p style="color: #7F8C8D; font-size: 0.8em;">Data Perangkat Desa - Sistem Manajemen Data Gampong DPMG Langsa</p>
</div>
""", unsafe_allow_html=True)
