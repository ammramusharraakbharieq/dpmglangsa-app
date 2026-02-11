"""
Data Tuha Peuet Gampong Page
Sistem Manajemen Data Gampong - DPMG Langsa
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_tuha_peuet
from utils.data_manager import update_tuha_peuet_all, add_tuha_peuet, delete_tuha_peuet
from utils.auth import is_admin

# Page config
st.set_page_config(
    page_title="Data Tuha Peuet Gampong - DPMG Langsa",
    page_icon="🏘️",
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
    <h1 style="color: #3498DB;">🏘️ Data Tuha Peuet Gampong</h1>
    <p style="color: #BDC3C7;">Badan Permusyawaratan Desa (BPD) Kota Langsa</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Load data
df = load_tuha_peuet()

if not df.empty:
    # Get gampong list for reuse
    gampong_list = sorted([str(x) for x in df['GAMPONG'].dropna().unique().tolist()])
    
    # Tabs - show edit/add/delete only for admin
    if user_is_admin:
        tab_view, tab_edit, tab_edit_sek, tab_add, tab_delete = st.tabs(["📋 Lihat Data", "✏️ Edit Data", "📝 Edit Sekretaris TPG", "➕ Tambah Anggota", "🗑️ Hapus Anggota"])
    else:
        tab_view = st.tabs(["📋 Lihat Data"])[0]
    
    with tab_view:
        st.subheader("📋 Data Anggota Tuha Peuet Gampong")
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Anggota", len(df))
        with col2:
            kec_count = df['KECAMATAN'].nunique()
            st.metric("Kecamatan", kec_count)
        with col3:
            gampong_count = df['GAMPONG'].nunique()
            st.metric("Gampong", gampong_count)
        
        st.markdown("---")
        
        # Filters
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            kecamatan_options = ['Semua'] + sorted([str(x) for x in df['KECAMATAN'].dropna().unique().tolist()])
            selected_kec = st.selectbox("Filter Kecamatan", kecamatan_options, key="view_kec")
        
        with col_f2:
            if selected_kec != 'Semua':
                kemukiman_options = ['Semua'] + sorted([str(x) for x in df[df['KECAMATAN'].astype(str) == selected_kec]['KEMUKIMAN'].dropna().unique().tolist()])
            else:
                kemukiman_options = ['Semua'] + sorted([str(x) for x in df['KEMUKIMAN'].dropna().unique().tolist()])
            selected_kem = st.selectbox("Filter Kemukiman", kemukiman_options, key="view_kem")
        
        with col_f3:
            if selected_kec != 'Semua':
                filtered_for_gampong = df[df['KECAMATAN'].astype(str) == selected_kec]
                if selected_kem != 'Semua':
                    filtered_for_gampong = filtered_for_gampong[filtered_for_gampong['KEMUKIMAN'].astype(str) == selected_kem]
                gampong_options = ['Semua'] + sorted([str(x) for x in filtered_for_gampong['GAMPONG'].dropna().unique().tolist()])
            else:
                gampong_options = ['Semua'] + sorted([str(x) for x in df['GAMPONG'].dropna().unique().tolist()])
            selected_gampong = st.selectbox("Filter Gampong", gampong_options, key="view_gampong")
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_kec != 'Semua':
            filtered_df = filtered_df[filtered_df['KECAMATAN'].astype(str) == selected_kec]
        
        if selected_kem != 'Semua':
            filtered_df = filtered_df[filtered_df['KEMUKIMAN'].astype(str) == selected_kem]
        
        if selected_gampong != 'Semua':
            filtered_df = filtered_df[filtered_df['GAMPONG'].astype(str) == selected_gampong]
        
        # Search
        search = st.text_input("🔍 Cari Nama Anggota", key="search_view")
        if search:
            filtered_df = filtered_df[filtered_df['NAMA_ANGGOTA'].str.contains(search, case=False, na=False)]
        
        # Display data - include JABATAN and SEKRETARIS_TPG to show Sekretaris TPG info
        display_df = filtered_df[['KECAMATAN', 'KEMUKIMAN', 'GAMPONG', 'NO_ANGGOTA', 'NAMA_ANGGOTA', 'JABATAN', 'SEKRETARIS_TPG']].copy()
        display_df.columns = ['Kecamatan', 'Kemukiman', 'Gampong', 'No', 'Nama Anggota', 'Jabatan', 'Sekretaris TPG']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.info(f"📊 Menampilkan {len(filtered_df)} dari {len(df)} data")
    
    # Admin-only tabs
    if user_is_admin:
        with tab_edit:
            st.subheader("✏️ Edit Data Tuha Peuet")
            
            st.markdown("""
            <div style="padding: 10px; background: rgba(52, 152, 219, 0.1); border-radius: 8px; border-left: 3px solid #3498DB; margin-bottom: 20px;">
                <p style="color: #E0E0E0; margin: 0;"><strong>ℹ️ Keterangan:</strong></p>
                <ul style="color: #BDC3C7; margin: 5px 0;">
                    <li><strong>Nama Anggota</strong> - Dapat diedit</li>
                    <li><strong>Jenis Kelamin</strong> - Pilih dari dropdown (akan disimpan sebagai simbol ✓)</li>
                    <li><strong>Keterangan</strong> - Input teks biasa</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Select Gampong
            edit_gampong = st.selectbox("🔍 Pilih Gampong untuk diedit", gampong_list, key="edit_gampong_select")
            
            if edit_gampong:
                # Get all anggota for the selected gampong
                gampong_df = df[df['GAMPONG'].astype(str) == edit_gampong].copy()
                gampong_df = gampong_df.sort_values('NO_ANGGOTA')
                
                key_prefix = f"edit_{edit_gampong.replace(' ', '_')}"
                
                st.markdown(f"### 📝 Data Tuha Peuet: **{edit_gampong}**")
                st.markdown("---")
                
                edited_data = []
                
                # Iterate through each anggota
                for idx, row in gampong_df.iterrows():
                    no_anggota = row['NO_ANGGOTA']
                    nama = str(row['NAMA_ANGGOTA']) if pd.notna(row['NAMA_ANGGOTA']) else ''
                    
                    # Determine current gender from LAKI_LAKI / PEREMPUAN columns
                    laki = row.get('LAKI_LAKI', '')
                    perempuan = row.get('PEREMPUAN', '')
                    if pd.notna(laki) and str(laki).strip():
                        current_jk = 'L'
                    elif pd.notna(perempuan) and str(perempuan).strip():
                        current_jk = 'P'
                    else:
                        current_jk = 'L'  # Default
                    
                    keterangan = str(row.get('KETERANGAN', '')) if pd.notna(row.get('KETERANGAN', '')) else ''
                    
                    row_key = f"{key_prefix}_{idx}_{no_anggota}"
                    
                    with st.expander(f"**{no_anggota}. {nama}**", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_nama = st.text_input("👤 Nama Anggota", value=nama, key=f"{row_key}_nama")
                            
                            jk_options = ['L', 'P']
                            jk_idx = jk_options.index(current_jk) if current_jk in jk_options else 0
                            new_jk = st.selectbox("⚧ Jenis Kelamin", options=jk_options,
                                                 format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan',
                                                 index=jk_idx, key=f"{row_key}_jk")
                        
                        with col2:
                            new_ket = st.text_input("📝 Keterangan", value=keterangan, key=f"{row_key}_ket")
                        
                        edited_data.append({
                            'NO_ANGGOTA': no_anggota,
                            'NAMA_ANGGOTA': new_nama,
                            'JENIS_KELAMIN': new_jk,
                            'KETERANGAN': new_ket
                        })
                
                st.markdown("---")
                
                if st.button("💾 Simpan Semua Perubahan", type="primary", use_container_width=True):
                    result = update_tuha_peuet_all(edit_gampong, edited_data)
                    if result.get('success'):
                        st.success("✅ Semua data berhasil diupdate!")
                        st.rerun()
                    else:
                        st.error(f"❌ Gagal: {result.get('error', result.get('message'))}")
        
        with tab_edit_sek:
            st.subheader("📝 Edit Sekretaris TPG")
            
            st.markdown("""
            <div style="padding: 10px; background: rgba(155, 89, 182, 0.1); border-radius: 8px; border-left: 3px solid #9B59B6; margin-bottom: 20px;">
                <p style="color: #E0E0E0; margin: 0;"><strong>ℹ️ Edit Sekretaris TPG</strong><br>
                <span style="color: #BDC3C7;">Fitur ini untuk mengubah nama dan jabatan Sekretaris TPG per gampong.</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            
            # Get list of unique gampongs
            unique_gampongs_df = df.drop_duplicates(subset=['GAMPONG']).copy()
            unique_gampongs = sorted(unique_gampongs_df['GAMPONG'].dropna().unique().tolist())
            
            if unique_gampongs:
                sek_gampong = st.selectbox("🔍 Pilih Gampong", unique_gampongs, key="sek_gampong_select")
                
                if sek_gampong:
                    # Get info for this gampong (take first row)
                    gampong_rows = df[df['GAMPONG'] == sek_gampong]
                    if not gampong_rows.empty:
                        sek_row = gampong_rows.iloc[0]
                        
                        st.markdown(f"### 📝 Sekretaris TPG: **{sek_gampong}**")
                        st.markdown("---")
                        
                        current_name = str(sek_row.get('SEKRETARIS_TPG', '')) if pd.notna(sek_row.get('SEKRETARIS_TPG')) else ''
                        current_jabatan = str(sek_row.get('SEKRETARIS_JABATAN', 'Sekretaris TPG')) if pd.notna(sek_row.get('SEKRETARIS_JABATAN')) else 'Sekretaris TPG'
                        # No longer using specific row NO_ANGGOTA for secretary as they are separate
                        
                        # Use dynamic keys based on gampong to ensure values update correctly
                        key_prefix = f"sek_{sek_gampong.replace(' ', '_')}"
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_sek_name = st.text_input("👤 Nama Sekretaris TPG", value=current_name, key=f"{key_prefix}_nama")
                        
                        with col2:
                            jabatan_options = ['Sekretaris TPG', 'Anggota TPG merangkap Sekretaris TPG']
                            # Check if current jabatan matches any option
                            if 'merangkap' in current_jabatan.lower():
                                jabatan_idx = 1
                            else:
                                jabatan_idx = 0
                            new_sek_jabatan = st.selectbox("🏛️ Jabatan", options=jabatan_options, 
                                                           index=jabatan_idx, key=f"{key_prefix}_jabatan")
                        
                        st.markdown("---")
                        
                        if st.button("💾 Simpan Perubahan Sekretaris TPG", type="primary", use_container_width=True):
                            from utils.data_manager import update_sekretaris_tpg
                            # We don't need no_anggota anymore for this update
                            result = update_sekretaris_tpg(sek_gampong, None, new_sek_name, new_sek_jabatan)
                            if result.get('success'):
                                st.success("✅ Data Sekretaris TPG berhasil diupdate!")
                                st.rerun()
                            else:
                                st.error(f"❌ Gagal: {result.get('error', result.get('message'))}")
            else:
                st.info("ℹ️ Belum ada data Gampong")
        
        with tab_add:
            st.subheader("➕ Tambah Anggota Tuha Peuet Baru")
            
            st.markdown("""
            <div style="padding: 10px; background: rgba(46, 204, 113, 0.1); border-radius: 8px; border-left: 3px solid #2ECC71; margin-bottom: 20px;">
                <p style="color: #E0E0E0; margin: 0;"><strong>ℹ️ Tambah Anggota</strong><br>
                <span style="color: #BDC3C7;">Gunakan fitur ini untuk menambahkan anggota Tuha Peuet yang belum terdata.</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            add_gampong = st.selectbox("🔍 Pilih Gampong", gampong_list, key="add_gampong_select")
            
            if add_gampong:
                gampong_df = df[df['GAMPONG'].astype(str) == add_gampong]
                kec = str(gampong_df.iloc[0]['KECAMATAN']) if not gampong_df.empty else ''
                kem = str(gampong_df.iloc[0]['KEMUKIMAN']) if not gampong_df.empty else ''
                
                max_anggota = gampong_df['NO_ANGGOTA'].max() if not gampong_df.empty else 0
                try:
                    next_no = int(max_anggota) + 1 if pd.notna(max_anggota) else 1
                except:
                    next_no = 1
                
                st.markdown(f"**Kecamatan:** {kec} | **Kemukiman:** {kem} | **Gampong:** {add_gampong}")
                st.markdown(f"**No Anggota berikutnya:** {next_no}")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    add_nama = st.text_input("👤 Nama Anggota", key="add_nama")
                    add_jk = st.selectbox("⚧ Jenis Kelamin", options=['L', 'P'],
                                         format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan',
                                         key="add_jk")
                
                with col2:
                    add_ket = st.text_input("📝 Keterangan", key="add_ket")
                
                if st.button("➕ Tambah Anggota", type="primary"):
                    if add_nama:
                        anggota_data = {
                            'GAMPONG': add_gampong,
                            'NO_ANGGOTA': next_no,
                            'NAMA_ANGGOTA': add_nama,
                            'JENIS_KELAMIN': add_jk,
                            'KETERANGAN': add_ket
                        }
                        result = add_tuha_peuet(anggota_data)
                        if result.get('success'):
                            st.success("✅ Anggota berhasil ditambahkan!")
                            st.rerun()
                        else:
                            st.error(f"❌ Gagal: {result.get('error', result.get('message'))}")
                    else:
                        st.error("❌ Nama Anggota wajib diisi")
        
        with tab_delete:
            st.subheader("🗑️ Hapus Anggota Tuha Peuet")
            
            st.markdown("""
            <div style="padding: 10px; background: rgba(231, 76, 60, 0.1); border-radius: 8px; border-left: 3px solid #E74C3C; margin-bottom: 20px;">
                <p style="color: #E0E0E0; margin: 0;"><strong>⚠️ Perhatian:</strong><br>
                <span style="color: #BDC3C7;">Data yang dihapus tidak dapat dikembalikan. Pastikan Anda memilih anggota yang benar.</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            del_gampong = st.selectbox("🔍 Pilih Gampong", gampong_list, key="del_gampong_select")
            
            if del_gampong:
                gampong_df = df[df['GAMPONG'].astype(str) == del_gampong]
                
                if not gampong_df.empty:
                    st.markdown(f"**Daftar Anggota Tuha Peuet di {del_gampong}:**")
                    
                    for idx, row in gampong_df.iterrows():
                        no_anggota = row['NO_ANGGOTA']
                        nama = str(row['NAMA_ANGGOTA']) if pd.notna(row['NAMA_ANGGOTA']) else '-'
                        
                        with st.expander(f"**{no_anggota}. {nama}**"):
                            st.write(f"👤 Nama: **{nama}**")
                            
                            # Determine gender
                            laki = row.get('LAKI_LAKI', '')
                            perempuan = row.get('PEREMPUAN', '')
                            if pd.notna(laki) and str(laki).strip():
                                jk = 'Laki-laki'
                            elif pd.notna(perempuan) and str(perempuan).strip():
                                jk = 'Perempuan'
                            else:
                                jk = '-'
                            st.write(f"⚧ Jenis Kelamin: **{jk}**")
                            
                            ket = str(row.get('KETERANGAN', '')) if pd.notna(row.get('KETERANGAN', '')) else '-'
                            st.write(f"📝 Keterangan: **{ket}**")
                            
                            # Confirmation
                            confirm_key = f"confirm_del_{del_gampong}_{no_anggota}"
                            confirm = st.checkbox(f"Saya yakin ingin menghapus {nama}", key=confirm_key)
                            
                            if confirm:
                                if st.button(f"🗑️ Hapus {nama}", type="primary", key=f"btn_del_{del_gampong}_{no_anggota}"):
                                    result = delete_tuha_peuet(del_gampong, no_anggota)
                                    if result.get('success'):
                                        st.success("✅ Anggota berhasil dihapus!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Gagal: {result.get('error', result.get('message'))}")
                else:
                    st.info("ℹ️ Tidak ada anggota di gampong ini")

else:
    st.warning("⚠️ Tidak dapat memuat data. Pastikan file Excel tersedia.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <p style="color: #7F8C8D; font-size: 0.8em;">Data Tuha Peuet Gampong - Sistem Manajemen Data Gampong DPMG Langsa</p>
</div>
""", unsafe_allow_html=True)
