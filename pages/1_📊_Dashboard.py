"""
Dashboard Page
Sistem Manajemen Data Gampong - DPMG Langsa
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_all_data, get_statistics, get_kecamatan_list, 
    get_data_by_kecamatan, load_camat_mukim_geuchik
)

# Page config
st.set_page_config(
    page_title="Dashboard - DPMG Langsa",
    page_icon="📊",
    layout="wide"
)

# Check authentication
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Anda harus login terlebih dahulu untuk mengakses halaman ini.")
    st.markdown("[🔐 Kembali ke Halaman Login](/)")
    st.stop()

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
    <h1 style="color: #3498DB;">📊 Dashboard</h1>
    <p style="color: #BDC3C7;">Ringkasan Data Pemerintahan Gampong Kota Langsa</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Get statistics
stats = get_statistics()

# Metrics row 1
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🏢 Kecamatan", stats['total_kecamatan'])

with col2:
    st.metric("🏘️ Kemukiman", stats['total_kemukiman'])

with col3:
    st.metric("🏠 Gampong", stats['total_gampong'])

with col4:
    st.metric("👤 Geuchik", stats['total_geuchik'])

# Metrics row 2
col5, col6 = st.columns(2)

with col5:
    st.metric("👥 Total Perangkat Desa", stats['total_perangkat'])

with col6:
    st.metric("🏛️ Anggota Tuha Peuet", stats['total_tuha_peuet'])

st.markdown("---")

# Charts section
st.subheader("📈 Visualisasi Data")

# Get data for charts
df_main = load_camat_mukim_geuchik()

if not df_main.empty:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Bar chart - Gampong per Kecamatan
        gampong_per_kec = df_main.groupby('KECAMATAN').size().reset_index(name='Jumlah Gampong')
        
        fig1 = px.bar(
            gampong_per_kec, 
            x='KECAMATAN', 
            y='Jumlah Gampong',
            title='Jumlah Gampong per Kecamatan',
            color='Jumlah Gampong',
            color_continuous_scale='Blues'
        )
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#E0E0E0',
            title_font_color='#3498DB',
            xaxis=dict(tickangle=45)
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        # Pie chart - Distribusi Kemukiman per Kecamatan
        kemukiman_per_kec = df_main.groupby('KECAMATAN')['KEMUKIMAN'].nunique().reset_index(name='Jumlah Kemukiman')
        
        fig2 = px.pie(
            kemukiman_per_kec,
            values='Jumlah Kemukiman',
            names='KECAMATAN',
            title='Distribusi Kemukiman per Kecamatan',
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#E0E0E0',
            title_font_color='#3498DB'
        )
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Filter section
st.subheader("🔍 Filter Data")

col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    kecamatan_list = ['Semua'] + get_kecamatan_list()
    selected_kecamatan = st.selectbox("Pilih Kecamatan", kecamatan_list)

# Show filtered data
if selected_kecamatan != 'Semua':
    filtered_df = df_main[df_main['KECAMATAN'] == selected_kecamatan]
else:
    filtered_df = df_main

st.markdown("### 📋 Data Gampong")

# Display dataframe with styling
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "NO": st.column_config.NumberColumn("No", width="small"),
        "KECAMATAN": st.column_config.TextColumn("Kecamatan", width="medium"),
        "NAMA CAMAT": st.column_config.TextColumn("Nama Camat", width="medium"),
        "KEMUKIMAN": st.column_config.TextColumn("Kemukiman", width="medium"),
        "NAMA MUKIM": st.column_config.TextColumn("Nama Mukim", width="medium"),
        "GAMPONG": st.column_config.TextColumn("Gampong", width="medium"),
        "NAMA GEUCHIK": st.column_config.TextColumn("Nama Geuchik", width="medium"),
    }
)

# Stats for filtered data
if selected_kecamatan != 'Semua':
    st.info(f"📊 Total {len(filtered_df)} gampong di Kecamatan {selected_kecamatan}")
else:
    st.info(f"📊 Total {len(filtered_df)} gampong di Kota Langsa")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <p style="color: #7F8C8D; font-size: 0.8em;">Dashboard - Sistem Manajemen Data Gampong DPMG Langsa</p>
</div>
""", unsafe_allow_html=True)
