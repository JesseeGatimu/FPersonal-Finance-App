import sqlite3
import logging
import streamlit as st

def update_db_schema():
    """Update database schema if needed"""
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    try:
        # Try to add role column if it doesn't exist
        c.execute('''ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';''')
        conn.commit()
    except sqlite3.OperationalError as e:
        logging.warning(f"Schema update warning: {e}")
    finally:
        conn.close()

def init_db():
    """Initialize database with all tables"""
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()

    # Create users table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, 
                username TEXT UNIQUE, 
                password TEXT,
                role TEXT DEFAULT 'user',
                reset_token TEXT,
                reset_token_expiry TEXT)''')

    # Check if transactions table exists and has username column
    c.execute("PRAGMA table_info(transactions)")
    columns = [col[1] for col in c.fetchall()]
    
    # Create transactions table (will do nothing if exists)
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY, 
                username TEXT DEFAULT 'default_user',
                name TEXT, 
                category TEXT, 
                amount REAL, 
                type TEXT, 
                date TEXT, 
                tags TEXT)''')

    # Only attempt migration if old table exists without username
    if columns and 'username' not in columns:
        try:
            c.execute('''CREATE TABLE transactions_new (
                        id INTEGER PRIMARY KEY, 
                        username TEXT DEFAULT 'default_user',
                        name TEXT, 
                        category TEXT, 
                        amount REAL, 
                        type TEXT, 
                        date TEXT, 
                        tags TEXT)''')
            c.execute('''INSERT INTO transactions_new 
                        (id, name, category, amount, type, date, tags)
                        SELECT id, name, category, amount, type, date, tags 
                        FROM transactions''')
            c.execute('DROP TABLE transactions')
            c.execute('ALTER TABLE transactions_new RENAME TO transactions')
            st.success("Transactions table migrated successfully!")
        except sqlite3.Error as e:
            st.error(f"Transaction migration error: {e}")

    # Create budgets table
    c.execute('''CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY,
                username TEXT DEFAULT 'default_user',
                category TEXT,
                budget_amount REAL)''')

    # Create recurring transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER PRIMARY KEY,
                username TEXT DEFAULT 'default_user',
                name TEXT,
                category TEXT,
                amount REAL,
                type TEXT,
                frequency TEXT,
                next_due_date TEXT)''')

    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection"""
    return sqlite3.connect("finance.db")