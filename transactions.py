import sqlite3
import pandas as pd
import streamlit as st
from database import get_db_connection

def add_transaction(username, name, category, amount, t_type, date, tags=None):
    if tags is None:
        tags = []
    conn = get_db_connection()
    try:
        conn.execute("""INSERT INTO transactions 
                     (username, name, category, amount, type, date, tags) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                  (username, name, category, amount, t_type, date, ', '.join(tags)))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error adding transaction: {e}")
    finally:
        conn.close()

def get_transactions(username=None):
    conn = get_db_connection()
    try:
        query = "SELECT * FROM transactions" + (" WHERE username = ?" if username else "")
        params = (username,) if username else ()
        df = pd.read_sql_query(query, conn, params=params)
        if not df.empty and 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'])
        return df
    except sqlite3.Error as e:
        st.error(f"Error fetching transactions: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_budget(username=None):
    conn = get_db_connection()
    try:
        query = "SELECT * FROM budgets" + (" WHERE username = ?" if username else "")
        params = (username,) if username else ()
        return pd.read_sql_query(query, conn, params=params)
    except sqlite3.Error as e:
        st.error(f"Error fetching budgets: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def export_to_csv(username):
    df = get_transactions(username)
    return df.to_csv(index=False)