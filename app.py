import streamlit as st
import pandas as pd
import logging
import os
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.colored_header import colored_header
from streamlit_extras.dataframe_explorer import dataframe_explorer

# Import modules
from styles import apply_global_styles
from database import init_db, update_db_schema
from auth import *
from transactions import *
from viz import *

# Initialize app
apply_global_styles()
update_db_schema()
init_db()

# Set up logging
logging.basicConfig(filename='finance_app.log', level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Session state setup
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if not st.session_state.logged_in:
    # Login Page with Enhanced UI
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("app_logo.png", width=300)
        st.markdown("""
        <h2 style='color: #04387d;'>Welcome to Finance Tracker</h2>
        <p>Track your expenses, analyze spending patterns, and achieve your financial goals.</p>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h2 style='color: #333; margin-bottom: 20px;'>Login</h2>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.form_submit_button("Login", use_container_width=True):
                if verify_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Successfully logged in!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Registration Section
        with st.expander("Don't have an account? Register here"):
            with st.form("register_form"):
                new_username = st.text_input("New Username", key="reg_username")
                new_password = st.text_input("New Password", type="password", key="reg_password")
                
                if st.form_submit_button("Create Account", use_container_width=True):
                    if new_username and new_password and is_password_strong(new_password):
                        create_user(new_username, new_password)
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Password must be at least 8 characters with uppercase, lowercase, number, and special character")
        
        # Password Reset
        with st.expander("Forgot Password?"):
            reset_username = st.text_input("Enter your username")
            if st.button("Send Reset Link"):
                request_password_reset(reset_username)
                st.success("Password reset link sent to your email!")

else:
    # Main Application
    st.sidebar.image("app_logo.png", width=150)
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    
    if get_user_role(st.session_state.username) == "admin":
        st.sidebar.success("Admin Privileges")
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    # Main Content
    colored_header(
        label="Finance Dashboard",
        description="Track and analyze your financial data",
        color_name="blue-70"
    )
    
    # Get transaction data
    df = get_transactions(st.session_state.username)
    
    # Summary Metrics
    if not df.empty:
        summary = create_financial_summary(df)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Income", f"KSH {summary['income']:,.2f}")
        col2.metric("Total Expenses", f"KSH {summary['expenses']:,.2f}")
        col3.metric("Net Balance", f"KSH {summary['balance']:,.2f}")
        col4.metric("Savings Rate", f"{summary['savings_rate']:.1f}%")
        
        with stylable_container(
            key="metric_cards",
            css_styles="""
            {
                background-color: #FFFFFF;
                border-left: 3px solid #4b8bff;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            """
        ):
            pass
    else:
        st.info("No transactions found. Add some transactions to see your dashboard.")
    
    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💸 Transactions", "📈 Analytics", "⚙️ Settings"])
    
    with tab1:
        # Dashboard View
        st.subheader("Financial Overview")
        
        if not df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.plotly_chart(create_trend_chart(df), use_container_width=True, key="trend_chart_1")
            
            with col2:
                sunburst = create_category_sunburst(df)
                if sunburst:
                    st.plotly_chart(sunburst, use_container_width=True, key="sunburst_chart")
                else:
                    st.warning("No expense data available for visualization")
            
            # Budget Progress
            st.subheader("Budget Tracking")
            df_budget = get_budget(st.session_state.username)
            
            if not df_budget.empty:
                for index, row in df_budget.iterrows():
                    category = row["category"]
                    budget_amount = row["budget_amount"]
                    expenses = df[(df["category"] == category) & (df["type"] == "Expense")]["amount"].sum()
                    
                    progress = min(expenses / budget_amount, 1) if budget_amount > 0 else 0
                    
                    st.write(f"**{category}** (Budget: KSH {budget_amount:,.2f})")
                    st.progress(progress, text=f"KSH {expenses:,.2f} of KSH {budget_amount:,.2f} ({progress*100:.1f}%)")
        
        else:
            st.info("No transactions found. Add some transactions to see your dashboard.")
    
    with tab2:
        # Transactions Management
        st.subheader("Transaction Management")
        
        with st.expander("➕ Add New Transaction", expanded=False):
            with st.form("transaction_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Transaction Name")
                    category = st.selectbox("Category", ["Food", "Transport", "Bills", "Shopping", "Entertainment", "Other"])
                    amount = st.number_input("Amount (KSH)", min_value=0.0, step=100.0)
                
                with col2:
                    t_type = st.selectbox("Type", ["Income", "Expense"])
                    date = st.date_input("Date", datetime.today())
                    tags = st.multiselect("Tags", ["Essential", "Luxury", "Recurring", "One-time"])
                
                if st.form_submit_button("Add Transaction", use_container_width=True):
                    add_transaction(st.session_state.username, name, category, amount, t_type, date, tags)
                    st.success("Transaction added successfully!")
                    st.rerun()
        
        # Transaction Table with Filters
        if not df.empty:
            filtered_df = dataframe_explorer(df, case=False)
            st.dataframe(filtered_df, use_container_width=True)
            
            # Export options
            st.download_button(
                label="📥 Export to CSV",
                data=export_to_csv(st.session_state.username),
                file_name='transactions.csv',
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.info("No transactions found. Add your first transaction above.")
    
    with tab3:
        # Advanced Analytics
        st.subheader("Financial Analytics")
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Expense by Category (Bar Chart)
                st.write("### Expenses by Category")
                df_expenses = df[df['type'] == 'Expense']
                
                if not df_expenses.empty:
                    category_sum = df_expenses.groupby('category')['amount'].sum().reset_index()
                    fig = px.bar(
                        category_sum,
                        x='category',
                        y='amount',
                        color='category',
                        text='amount',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_traces(texttemplate='KSH %{y:,.0f}', textposition='outside')
                    fig.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig, use_container_width=True, key="bar_chart")
                else:
                    st.warning("No expense data available")
            
            with col2:
                # Income vs Expense Pie Chart
                st.write("### Income vs Expense Distribution")
                type_sum = df.groupby('type')['amount'].sum().reset_index()
                fig = px.pie(
                    type_sum,
                    names='type',
                    values='amount',
                    color='type',
                    color_discrete_map={'Income':'#4CAF50','Expense':'#F44336'}
                )
                fig.update_traces(textinfo='percent+label+value', texttemplate='%{label}<br>KSH %{value:,.0f}<br>(%{percent})')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True, key="pie_chart")
            
            # Monthly Trends
            st.write("### Monthly Trends")
            st.plotly_chart(create_trend_chart(df), use_container_width=True, key="trend_chart_2")
        
        else:
            st.info("No transactions found. Add some transactions to see analytics.")
    
    with tab4:
        # Settings and Configuration
        st.subheader("Settings")
        
        with st.expander("🔐 Account Settings"):
            st.write("Change password")
            current_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm New Password", type="password")
            
            if st.button("Update Password", use_container_width=True):
                if new_pw == confirm_pw and is_password_strong(new_pw):
                    if verify_user(st.session_state.username, current_pw):
                        conn = sqlite3.connect("finance.db")
                        c = conn.cursor()
                        hashed_password = hash_password(new_pw)
                        c.execute("UPDATE users SET password = ? WHERE username = ?", 
                                  (hashed_password, st.session_state.username))
                        conn.commit()
                        conn.close()
                        st.success("Password updated successfully!")
                    else:
                        st.error("Current password is incorrect")
                else:
                    st.error("Passwords don't match or don't meet requirements")
        
        with st.expander("💰 Budget Management"):
            st.write("Set your monthly budgets")
            df_budget = get_budget(st.session_state.username)
            
            # Initialize default categories if no budgets exist
            if df_budget.empty:
                default_categories = ["Food", "Transport", "Bills", "Shopping", "Entertainment", "Other"]
                df_budget = pd.DataFrame({
                    'category': default_categories,
                    'budget_amount': [0.0] * len(default_categories)
                })
            
            # Create a form for budget updates
            with st.form("budget_form"):
                updated_budgets = []
                for index, row in df_budget.iterrows():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{row['category']}**")
                    with col2:
                        # Create input field for each budget
                        new_amount = st.number_input(
                            "Amount (KSH)",
                            value=float(row['budget_amount']),
                            key=f"budget_{row['category']}",
                            min_value=0.0,
                            step=100.0
                        )
                        updated_budgets.append((row['category'], new_amount))
                
                # Submit button for the form
                if st.form_submit_button("Update Budgets", use_container_width=True):
                    conn = sqlite3.connect("finance.db")
                    c = conn.cursor()
                    
                    # Clear existing budgets for this user
                    c.execute("DELETE FROM budgets WHERE username = ?", (st.session_state.username,))
                    
                    # Insert updated budgets
                    for category, amount in updated_budgets:
                        c.execute(
                            "INSERT INTO budgets (username, category, budget_amount) VALUES (?, ?, ?)",
                            (st.session_state.username, category, amount)
                        )
                    
                    conn.commit()
                    conn.close()
                    st.success("Budgets updated successfully!")
                    st.rerun()
        
        if get_user_role(st.session_state.username) == "admin":
            with st.expander("🛠 Admin Tools"):
                st.warning("Administrator Tools")
                if st.button("Export All Data", use_container_width=True):
                    st.info("Feature coming soon!")