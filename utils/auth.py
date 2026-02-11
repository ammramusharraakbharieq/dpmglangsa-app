"""
Authentication Module for Sistem Manajemen Data Gampong
Handles user authentication, registration, and role management via Google Sheets
"""

import hashlib
import streamlit as st
import pandas as pd
from utils.data_loader import get_gspread_client, SPREADSHEET_NAME

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_users_worksheet():
    """Helper to get Users worksheet"""
    client = get_gspread_client()
    if not client:
        return None
    try:
        sh = client.open(SPREADSHEET_NAME)
        return sh.worksheet("Users")
    except Exception as e:
        print(f"Error accessing Users sheet: {e}")
        return None

def load_users() -> dict:
    """Load users from Google Sheets and return as dict"""
    ws = get_users_worksheet()
    if not ws:
        return {}
    
    try:
        records = ws.get_all_records()
        users = {}
        for record in records:
            # Check if record has necessary keys (handle potential empty rows or bad data)
            if 'username' in record and record['username']:
                uname = str(record['username'])
                users[uname] = {
                    'password': str(record['password']),
                    'role': str(record['role'])
                }
        return users
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def authenticate(username: str, password: str) -> dict:
    """
    Authenticate user with username and password
    Returns: {'success': bool, 'role': str, 'message': str}
    """
    users = load_users()
    
    if username not in users:
        return {'success': False, 'role': None, 'message': 'Username tidak ditemukan'}
    
    stored_hash = users[username]['password']
    
    # Check if stored password is hashed (simple length check for sha256 hex digest = 64 chars)
    # If legacy plain text (from manual entry), hash comparison won't work directly but we want to fail secure?
    # Actually, we should hash the input and compare. 
    # But if the DB has plain text "dpmglangsa01", hash("dpmglangsa01") != "dpmglangsa01".
    # User manually entered plain text.
    # We should support auto-hashing on first login if possible, OR just compare hash(input) == stored.
    # If stored is plain text, login will fail.
    # WE NEED TO HANDLE THIS. 
    # Scenario: User entered "admin1", "dpmglangsa01" in sheet.
    # User inputs "dpmglangsa01".
    # We hash input: "5e884..."
    # "5e884..." != "dpmglangsa01".
    # So we should check: if stored == input (plain text match) -> Update to hash?
    
    input_hash = hash_password(password)
    
    match = False
    
    if stored_hash == input_hash:
        match = True
    elif stored_hash == password: 
        # Fallback for plain text in DB (First time login after manual entry)
        # We should update the DB to be hashed for security
        match = True
        try:
           update_user_password(username, input_hash) 
        except:
            pass # Non-blocking update

    if match:
        return {
            'success': True, 
            'role': users[username]['role'],
            'message': 'Login berhasil'
        }
    else:
        return {'success': False, 'role': None, 'message': 'Password salah'}

def update_user_password(username, new_hash):
    """Helper to update password hash in DB"""
    ws = get_users_worksheet()
    cell = ws.find(username)
    if cell:
        # Password is column 2
        ws.update_cell(cell.row, 2, new_hash)

def register_user(username: str, password: str, confirm_password: str) -> dict:
    """
    Register a new viewer user
    Returns: {'success': bool, 'message': str}
    """
    # Validation
    if not username or not password:
        return {'success': False, 'message': 'Username dan password harus diisi'}
    
    if len(username) < 3:
        return {'success': False, 'message': 'Username minimal 3 karakter'}
    
    if len(password) < 6:
        return {'success': False, 'message': 'Password minimal 6 karakter'}
    
    if password != confirm_password:
        return {'success': False, 'message': 'Password tidak cocok'}
    
    users = load_users()
    
    # Check if username exists
    if username in users:
        return {'success': False, 'message': 'Username sudah digunakan'}
    
    # Check if username starts with 'admin' (reserved)
    if username.lower().startswith('admin'):
        return {'success': False, 'message': 'Username tidak boleh dimulai dengan "admin"'}
    
    try:
        ws = get_users_worksheet()
        # Append new user
        # Header: username, password, role
        hashed_pw = hash_password(password)
        ws.append_row([username, hashed_pw, 'viewer'])
        
        # Clear cache in data_loader if it caches users? Not currently caching users in data_loader.
        # But we might need to clear any auth cache if we added it.
        
        return {'success': True, 'message': 'Registrasi berhasil! Silakan login.'}
    except Exception as e:
        return {'success': False, 'message': f'Gagal menyimpan data: {e}'}

def get_user_role(username: str) -> str:
    """Get user role by username"""
    users = load_users()
    if username in users:
        return users[username].get('role', 'viewer')
    return None

def is_admin(role: str) -> bool:
    """Check if role is admin"""
    return role == 'admin'

def is_viewer(role: str) -> bool:
    """Check if role is viewer"""
    return role == 'viewer'

def get_all_users() -> dict:
    """Get all users (for admin management)"""
    return load_users()

def delete_user(username: str) -> dict:
    """Delete a user (admin only, cannot delete other admins)"""
    users = load_users()
    
    if username not in users:
        return {'success': False, 'message': 'User tidak ditemukan'}
    
    if users[username]['role'] == 'admin':
        return {'success': False, 'message': 'Tidak dapat menghapus akun admin'}
    
    try:
        ws = get_users_worksheet()
        cell = ws.find(username)
        if cell and cell.col == 1: # Confirm it's in username column
             ws.delete_rows(cell.row)
             return {'success': True, 'message': 'User berhasil dihapus'}
        return {'success': False, 'message': 'User tidak ditemukan di database'}
    except Exception as e:
        return {'success': False, 'message': f'Gagal menghapus user: {e}'}
