import sqlite3
import hashlib
import re
import logging
import random
import string
from datetime import datetime, timedelta
import streamlit as st
from database import get_db_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, role="user"):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, hash_password(password), role))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("Username already exists")
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    user = conn.execute("SELECT password FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user and user[0] == hash_password(password)

def get_user_role(username):
    conn = get_db_connection()
    role = conn.execute("SELECT role FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return role[0] if role else None

def is_password_strong(password):
    if len(password) < 8: return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"[0-9]", password): return False
    if not re.search(r"[@$!%*?&]", password): return False
    return True

def send_password_reset_email(email, token):
    st.warning(f"Email functionality not configured. Reset token: {token}")

def request_password_reset(username):
    conn = get_db_connection()
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    expiry = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE username = ?",
                (token, expiry, username))
    conn.commit()
    conn.close()
    send_password_reset_email(username, token)

def reset_password(username, token, new_password):
    conn = get_db_connection()
    user = conn.execute("SELECT reset_token, reset_token_expiry FROM users WHERE username = ?",
                       (username,)).fetchone()
    if user and user[0] == token and datetime.now() < datetime.strptime(user[1], "%Y-%m-%d %H:%M:%S"):
        conn.execute("UPDATE users SET password = ?, reset_token = NULL, reset_token_expiry = NULL WHERE username = ?",
                    (hash_password(new_password), username))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False