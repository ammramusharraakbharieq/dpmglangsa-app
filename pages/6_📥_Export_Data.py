"""
Export Data Page
Sistem Manajemen Data Gampong - DPMG Langsa
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from io import BytesIO
import zipfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_all_data

# Page config
st.set_page_config(
    page_title="Export Data - DPMG Langsa",
    page_icon="📥",
    layout="wide"
)

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
    <h1 style="color: #3498DB;">📥 Export Data ke Excel</h1>
    <p style="color: #BDC3C7;">Unduh data terbaru dari Database (Google Sheets)</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# File descriptions
file_info = {
    'camat_mukim_geuchik': {
        'title': 'Data Camat, Mukim, dan Geuchik',
        'description': 'Daftar lengkap Camat, Mukim, dan Geuchik per Gampong',
        'icon': '👥',
        'filename': 'Data_Camat_Mukim_Geuchik.xlsx'
    },
    'geuchik_detail': {
        'title': 'Data Detail Geuchik',
        'description': 'Informasi lengkap Geuchik termasuk SK, pendidikan, dan kontak',
        'icon': '📋',
        'filename': 'Data_Detail_Geuchik.xlsx'
    },
    'perangkat_desa': {
        'title': 'Data Kepala Desa & Perangkat Desa',
        'description': 'Data semua perangkat desa termasuk jabatan dan NIK',
        'icon': '🏛️',
        'filename': 'Data_Perangkat_Desa.xlsx'
    },
    'tuha_peuet': {
        'title': 'Data Tuha Peuet Gampong',
        'description': 'Data anggota Badan Permusyawaratan Desa (BPD)',
        'icon': '🏘️',
        'filename': 'Data_Tuha_Peuet.xlsx'
    }
}


from utils.excel_exporter import ExcelExporter

# Initialize exporter with current directory as base path (where templates are)
exporter = ExcelExporter(Path(__file__).parent.parent)

def get_excel_download(key, df):
    """Get Excel file as bytes using template exporter"""
    try:
        if key == 'camat_mukim_geuchik':
            return exporter.export_camat_mukim_geuchik(df)
        elif key == 'geuchik_detail':
            return exporter.export_geuchik_detail(df)
        elif key == 'perangkat_desa':
            return exporter.export_perangkat_desa(df)
        elif key == 'tuha_peuet':
            return exporter.export_tuha_peuet(df)
    except Exception as e:
        st.error(f"Error exporting {key}: {e}")
        return None

# Export section
st.subheader("📂 Pilih File untuk Diunduh")

st.markdown("""
<div style="padding: 15px; background: rgba(52, 152, 219, 0.1); border-radius: 8px; border-left: 3px solid #3498DB; margin-bottom: 20px;">
    <p style="color: #E0E0E0; margin: 0;"><strong>ℹ️ Format Asli</strong><br>
    <span style="color: #BDC3C7;">File yang diunduh menggunakan format Excel asli desa.</span></p>
</div>
""", unsafe_allow_html=True)

# Create download cards in 2 columns
col1, col2 = st.columns(2)

# Load data once
all_data = load_all_data()

for i, (key, info) in enumerate(file_info.items()):
    with col1 if i % 2 == 0 else col2:
        st.markdown(f"""
        <div style="padding: 20px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 12px; border: 1px solid #3498DB; margin-bottom: 15px;">
            <h3 style="color: #3498DB; margin: 0 0 10px 0;">{info['icon']} {info['title']}</h3>
            <p style="color: #BDC3C7; font-size: 0.9em; margin: 0 0 15px 0;">{info['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        df = all_data.get(key)
        
        if df is not None and not df.empty:
            # Generate download button
            # We need to process the export on click or pre-calculate?
            # Streamlit download button requires data to be ready.
            # Calculating on the fly might be slow if data is large but it ensures fresh data.
            # Let's generate it.
            
            excel_data = get_excel_download(key, df)
            
            if excel_data:
                st.download_button(
                    label=f"⬇️ Unduh Excel",
                    data=excel_data,
                    file_name=info['filename'],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_{key}"
                )
        else:
            st.warning(f"⚠️ Data tidak tersedia")

st.markdown("---")

# Download all section
st.subheader("📦 Unduh Semua File")

def create_zip_archive(data_dict):
    """Create ZIP archive containing all Excel files"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for key, info in file_info.items():
            df = data_dict.get(key)
            if df is not None and not df.empty:
                # Create Excel in memory
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                
                # Write to zip
                zip_file.writestr(info['filename'], excel_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

try:
    if any(df is not None and not df.empty for df in all_data.values()):
        zip_data = create_zip_archive(all_data)
        st.download_button(
            label="📦 Unduh Semua File (ZIP)",
            data=zip_data,
            file_name="Data_Gampong_Kota_Langsa.zip",
            mime="application/zip",
            key="download_all"
        )
except Exception as e:
    st.error(f"❌ Gagal membuat arsip: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <p style="color: #7F8C8D; font-size: 0.8em;">Export Data - Sistem Manajemen Data Gampong DPMG Langsa</p>
</div>
""", unsafe_allow_html=True)
