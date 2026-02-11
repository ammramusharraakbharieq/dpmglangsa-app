"""
Sistem Manajemen Data Gampong
Dinas Pemberdayaan Kota Langsa

Main application entry point with Authentication
"""

import streamlit as st
from pathlib import Path
import base64

# Initialize session state BEFORE page config
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None

# Page config - sidebar collapsed when not logged in
st.set_page_config(
    page_title="Sistem Manajemen Data Gampong - DPMG Langsa",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed" if not st.session_state.logged_in else "expanded"
)

# Import auth module
from utils.auth import authenticate, register_user, is_admin

# Load custom CSS
def load_css():
    css_file = Path(__file__).parent / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Function to get base64 image
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

load_css()

# Get logo path
logo_path = Path(__file__).parent / "logolangsa.png"
logo_base64 = get_base64_image(logo_path) if logo_path.exists() else ""

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

def show_login_page():
    """Display login and registration page - standalone without sidebar"""
    
    # Hide sidebar completely on login page
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        .css-1d391kg {
            display: none !important;
        }
        /* Hide the sidebar toggle button */
        button[kind="header"] {
            display: none !important;
        }
        [data-testid="collapsedControl"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and Title
        st.markdown(f"""
        <div style="text-align: center; padding: 30px 0;">
            <img src="data:image/png;base64,{logo_base64}" width="120" style="border-radius: 12px; box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);">
            <h1 style="color: #3498DB; margin-top: 20px;">Sistem Manajemen Data Gampong</h1>
            <p style="color: #BDC3C7;">Dinas Pemberdayaan Masyarakat dan Gampong<br>Kota Langsa</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for Login and Register
        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Daftar Akun Baru"])
        
        with tab_login:
            st.markdown("""
            <div style="padding: 20px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 12px; margin: 20px 0;">
                <h3 style="color: #E0E0E0; margin-bottom: 15px;">🔐 Masuk ke Sistem</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("👤 Username", placeholder="Masukkan username")
                password = st.text_input("🔑 Password", type="password", placeholder="Masukkan password")
                submit = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
                
                if submit:
                    if username and password:
                        result = authenticate(username, password)
                        if result['success']:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.role = result['role']
                            st.success(f"✅ {result['message']}! Selamat datang, {username}!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
                    else:
                        st.warning("⚠️ Mohon isi username dan password")
        
        with tab_register:
            st.markdown("""
            <div style="padding: 20px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 12px; margin: 20px 0;">
                <h3 style="color: #E0E0E0; margin-bottom: 15px;">📝 Buat Akun Viewer</h3>
                <p style="color: #BDC3C7; font-size: 0.9em;">Akun viewer hanya dapat melihat data dan download Excel.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("register_form"):
                new_username = st.text_input("👤 Username Baru", placeholder="Minimal 3 karakter")
                new_password = st.text_input("🔑 Password", type="password", placeholder="Minimal 6 karakter")
                confirm_password = st.text_input("🔑 Konfirmasi Password", type="password", placeholder="Ulangi password")
                register = st.form_submit_button("📝 Daftar", use_container_width=True, type="primary")
                
                if register:
                    result = register_user(new_username, new_password, confirm_password)
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")
        
        # Footer
        st.markdown("""
        <div style="text-align: center; padding: 30px 0; margin-top: 20px; border-top: 1px solid #2C3E50;">
            <p style="color: #7F8C8D; font-size: 0.85em;">© 2026 DPMG Kota Langsa</p>
        </div>
        """, unsafe_allow_html=True)

def show_main_app():
    """Display main application after login"""
    
    # Sidebar with user info and logout
    with st.sidebar:
        # Logo in sidebar
        if logo_base64:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px 0;">
                <img src="data:image/png;base64,{logo_base64}" width="80" style="border-radius: 8px; box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);">
            </div>
            """, unsafe_allow_html=True)
        
        # Title
        st.markdown("""
        <div style="text-align: center; padding: 10px 0; border-bottom: 1px solid #2C3E50; margin-bottom: 20px;">
            <h1 style="color: #3498DB; font-size: 1.1em; margin: 0;">SISTEM MANAJEMEN</h1>
            <h2 style="color: #E0E0E0; font-size: 0.95em; margin: 5px 0;">DATA GAMPONG</h2>
            <p style="color: #BDC3C7; font-size: 0.75em; margin: 5px 0;">DPMG Kota Langsa</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User info
        role_badge = "🔑 Admin" if is_admin(st.session_state.role) else "👤 Viewer"
        role_color = "#27AE60" if is_admin(st.session_state.role) else "#3498DB"
        
        st.markdown(f"""
        <div style="padding: 15px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 8px; border: 1px solid {role_color}; margin-bottom: 15px;">
            <p style="color: #E0E0E0; font-size: 0.9em; margin: 0; text-align: center;">
                <strong>👋 Selamat Datang!</strong><br>
                <span style="color: {role_color};">{st.session_state.username}</span><br>
                <span style="background: {role_color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75em;">{role_badge}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            logout()
        
        st.markdown("---")
        
        # Info
        st.markdown("""
        <div style="padding: 10px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 8px; border: 1px solid #3498DB;">
            <p style="color: #BDC3C7; font-size: 0.8em; margin: 0; text-align: center;">
                📊 Sistem Informasi Terpadu<br>
                Data Pemerintahan Gampong
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content - Hero Section
    st.markdown(f"""
    <style>
    .hero-card {{
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        background: linear-gradient(135deg, #0d2844 0%, #1a3a5c 50%, #0f2d4a 100%);
    }}
    .hero-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255,255,255,0.2) !important;
        border-color: rgba(52, 152, 219, 0.5) !important;
    }}
    .hero-logo {{
        transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    .hero-logo:hover {{
        transform: scale(1.1) rotate(5deg);
        filter: drop-shadow(0 15px 30px rgba(0,0,0,0.6));
    }}
    </style>

    <div class="hero-card" style="
        border-radius: 20px;
        padding: 20px 25px;
        margin: 10px 0 25px 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.1);
        border: 1px solid rgba(52, 152, 219, 0.2);
    ">
        <div style="display: flex; justify-content: flex-start; align-items: center; gap: 20px;">
            <img class="hero-logo" src="data:image/png;base64,{logo_base64}" width="90" style="
                border-radius: 10px; 
                filter: drop-shadow(0 6px 15px rgba(0,0,0,0.4));
                flex-shrink: 0;
            ">
            <div style="text-align: left;">
                <h1 style="
                    color: #FFFFFF; 
                    font-size: 1.6em; 
                    margin: 0; 
                    font-weight: 700;
                    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
                ">
                    🏘️ Sistem Manajemen Data Gampong
                </h1>
                <p style="
                    color: #b8d4e8; 
                    font-size: 0.95em; 
                    margin: 8px 0 5px 0; 
                    font-weight: 400;
                ">
                    Dinas Pemberdayaan Masyarakat dan Gampong Kota Langsa
                </p>
                <p style="
                    color: #7eb8db; 
                    font-size: 0.85em; 
                    font-weight: 500; 
                    margin: 0;
                    font-style: italic;
                ">
                    Provinsi Aceh - Indonesia
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick stats
    from utils.data_loader import get_statistics
    stats = get_statistics()

    # Stats with enhanced design
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h3 style="color: #E0E0E0; font-size: 1.3em; font-weight: 500;">📊 Ringkasan Data</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 16px; border: 2px solid #3498DB; box-shadow: 0 8px 20px rgba(52, 152, 219, 0.2); transition: transform 0.3s;">
            <p style="color: #3498DB; font-size: 3em; font-weight: 700; margin: 0; text-shadow: 0 0 20px rgba(52, 152, 219, 0.5);">{}</p>
            <p style="color: #BDC3C7; font-size: 0.95em; margin: 8px 0 0 0; font-weight: 500;">🏢 Kecamatan</p>
        </div>
        """.format(stats['total_kecamatan']), unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 16px; border: 2px solid #27AE60; box-shadow: 0 8px 20px rgba(39, 174, 96, 0.2); transition: transform 0.3s;">
            <p style="color: #27AE60; font-size: 3em; font-weight: 700; margin: 0; text-shadow: 0 0 20px rgba(39, 174, 96, 0.5);">{}</p>
            <p style="color: #BDC3C7; font-size: 0.95em; margin: 8px 0 0 0; font-weight: 500;">🏠 Kemukiman</p>
        </div>
        """.format(stats['total_kemukiman']), unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 16px; border: 2px solid #E67E22; box-shadow: 0 8px 20px rgba(230, 126, 34, 0.2); transition: transform 0.3s;">
            <p style="color: #E67E22; font-size: 3em; font-weight: 700; margin: 0; text-shadow: 0 0 20px rgba(230, 126, 34, 0.5);">{}</p>
            <p style="color: #BDC3C7; font-size: 0.95em; margin: 8px 0 0 0; font-weight: 500;">🏘️ Gampong</p>
        </div>
        """.format(stats['total_gampong']), unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 16px; border: 2px solid #9B59B6; box-shadow: 0 8px 20px rgba(155, 89, 182, 0.2); transition: transform 0.3s;">
            <p style="color: #9B59B6; font-size: 3em; font-weight: 700; margin: 0; text-shadow: 0 0 20px rgba(155, 89, 182, 0.5);">{}</p>
            <p style="color: #BDC3C7; font-size: 0.95em; margin: 8px 0 0 0; font-weight: 500;">👥 Perangkat</p>
        </div>
        """.format(stats['total_perangkat']), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Additional stats row
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("""
        <div style="text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 16px; border: 2px solid #1ABC9C; box-shadow: 0 8px 20px rgba(26, 188, 156, 0.2);">
            <p style="color: #1ABC9C; font-size: 3em; font-weight: 700; margin: 0; text-shadow: 0 0 20px rgba(26, 188, 156, 0.5);">{}</p>
            <p style="color: #BDC3C7; font-size: 0.95em; margin: 8px 0 0 0; font-weight: 500;">👤 Geuchik / Kepala Desa</p>
        </div>
        """.format(stats['total_geuchik']), unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div style="text-align: center; padding: 25px 15px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 16px; border: 2px solid #F39C12; box-shadow: 0 8px 20px rgba(243, 156, 18, 0.2);">
            <p style="color: #F39C12; font-size: 3em; font-weight: 700; margin: 0; text-shadow: 0 0 20px rgba(243, 156, 18, 0.5);">{}</p>
            <p style="color: #BDC3C7; font-size: 0.95em; margin: 8px 0 0 0; font-weight: 500;">🏛️ Anggota Tuha Peuet</p>
        </div>
        """.format(stats['total_tuha_peuet']), unsafe_allow_html=True)

    st.markdown("---")

    # Access info based on role
    if is_admin(st.session_state.role):
        access_info = """
        <div style="padding: 15px; background: rgba(39, 174, 96, 0.15); border-radius: 12px; border-left: 4px solid #27AE60; margin-bottom: 20px;">
            <p style="color: #27AE60; margin: 0;"><strong>🔑 Akses Admin</strong></p>
            <p style="color: #BDC3C7; margin: 5px 0 0 0; font-size: 0.9em;">Anda memiliki akses penuh: Lihat, Edit, Tambah, Hapus, dan Export data.</p>
        </div>
        """
    else:
        access_info = """
        <div style="padding: 15px; background: rgba(52, 152, 219, 0.15); border-radius: 12px; border-left: 4px solid #3498DB; margin-bottom: 20px;">
            <p style="color: #3498DB; margin: 0;"><strong>👤 Akses Viewer</strong></p>
            <p style="color: #BDC3C7; margin: 5px 0 0 0; font-size: 0.9em;">Anda dapat melihat data dan download Excel. Untuk edit data, hubungi Admin.</p>
        </div>
        """
    st.markdown(access_info, unsafe_allow_html=True)

    # Navigation info with enhanced cards
    st.markdown("""
    <div style="padding: 25px; background: linear-gradient(135deg, #1B2838 0%, #2C3E50 100%); border-radius: 16px; margin-top: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);">
        <h3 style="color: #3498DB; margin-bottom: 20px; font-size: 1.3em; display: flex; align-items: center; gap: 10px;">
            <span style="background: linear-gradient(135deg, #3498DB, #2980B9); padding: 8px 12px; border-radius: 8px;">📌</span>
            Panduan Navigasi
        </h3>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
            <div style="padding: 18px; background: rgba(52, 152, 219, 0.15); border-radius: 12px; border-left: 4px solid #3498DB;">
                <p style="color: #E0E0E0; margin: 0;"><strong>📊 Dashboard</strong><br>
                <span style="color: #BDC3C7; font-size: 0.9em;">Lihat statistik dan ringkasan data lengkap</span></p>
            </div>
            <div style="padding: 18px; background: rgba(46, 204, 113, 0.15); border-radius: 12px; border-left: 4px solid #2ECC71;">
                <p style="color: #E0E0E0; margin: 0;"><strong>👥 Data Camat/Mukim/Geuchik</strong><br>
                <span style="color: #BDC3C7; font-size: 0.9em;">Kelola data pejabat pemerintahan gampong</span></p>
            </div>
            <div style="padding: 18px; background: rgba(155, 89, 182, 0.15); border-radius: 12px; border-left: 4px solid #9B59B6;">
                <p style="color: #E0E0E0; margin: 0;"><strong>🏛️ Data Perangkat Desa</strong><br>
                <span style="color: #BDC3C7; font-size: 0.9em;">Edit, tambah, hapus data perangkat desa</span></p>
            </div>
            <div style="padding: 18px; background: rgba(241, 196, 15, 0.15); border-radius: 12px; border-left: 4px solid #F1C40F;">
                <p style="color: #E0E0E0; margin: 0;"><strong>🏘️ Data Tuha Peuet</strong><br>
                <span style="color: #BDC3C7; font-size: 0.9em;">Kelola anggota BPD gampong</span></p>
            </div>
            <div style="padding: 18px; background: rgba(26, 188, 156, 0.15); border-radius: 12px; border-left: 4px solid #1ABC9C;">
                <p style="color: #E0E0E0; margin: 0;"><strong>✏️ Edit Data</strong><br>
                <span style="color: #BDC3C7; font-size: 0.9em;">Ubah data Geuchik, Camat, dan Mukim</span></p>
            </div>
            <div style="padding: 18px; background: rgba(231, 76, 60, 0.15); border-radius: 12px; border-left: 4px solid #E74C3C;">
                <p style="color: #E0E0E0; margin: 0;"><strong>📥 Export Data</strong><br>
                <span style="color: #BDC3C7; font-size: 0.9em;">Unduh data ke format Excel</span></p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer with logo
    st.markdown(f"""
    <div style="text-align: center; padding: 30px 0; margin-top: 40px; border-top: 2px solid #2C3E50; background: linear-gradient(180deg, transparent 0%, rgba(52, 152, 219, 0.05) 100%);">
        <img src="data:image/png;base64,{logo_base64}" width="50" style="margin-bottom: 10px; opacity: 0.8;">
        <p style="color: #7F8C8D; font-size: 0.9em; margin: 0;">
            © 2026 <strong style="color: #BDC3C7;">Dinas Pemberdayaan Masyarakat dan Gampong</strong><br>
            Kota Langsa - Provinsi Aceh
        </p>
        <p style="color: #566573; font-size: 0.75em; margin: 10px 0 0 0;">
            Sistem Manajemen Data Gampong v1.0 • Built with Ammra
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main app logic
if st.session_state.logged_in:
    show_main_app()
else:
    show_login_page()
