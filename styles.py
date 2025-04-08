import streamlit as st

def apply_global_styles():
    st.set_page_config(
        page_title="Finance App",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
        :root {
            --primary: #04387d;
            --secondary: #ff6b6b;
            --background: #f8f9fa;
            --card: #ffffff;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #04387d, #3a7bf7);
            color: white;
        }
        
        .stMetric {
            background-color: var(--card);
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stButton>button {
            border-radius: 8px;
            border: none;
            background-color: var(--primary);
            color: white;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #3a7bf7;
            transform: translateY(-2px);
        }
        
        .stDataFrame {
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0 20px;
            border-radius: 8px 8px 0 0 !important;
            background-color: #e0e0e0 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--primary) !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)