import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def create_financial_summary(df):
    if df.empty:
        return {
            'income': 0,
            'expenses': 0,
            'balance': 0,
            'savings_rate': 0
        }
    
    try:
        total_income = df[df['type'] == 'Income']['amount'].sum()
        total_expenses = df[df['type'] == 'Expense']['amount'].sum()
        net_balance = total_income - total_expenses
        
        return {
            'income': total_income,
            'expenses': total_expenses,
            'balance': net_balance,
            'savings_rate': (net_balance / total_income * 100) if total_income > 0 else 0
        }
    except KeyError:
        return {
            'income': 0,
            'expenses': 0,
            'balance': 0,
            'savings_rate': 0
        }

def create_trend_chart(df):
    if df.empty:
        return go.Figure()
    
    try:
        df['date'] = pd.to_datetime(df['date'], format='mixed')
        df['month'] = df['date'].dt.to_period('M').astype(str)
        
        monthly_data = df.groupby(['month', 'type'])['amount'].sum().unstack().fillna(0)
        monthly_data['Net'] = monthly_data.get('Income', 0) - monthly_data.get('Expense', 0)
        
        fig = go.Figure()
        
        if 'Income' in monthly_data.columns:
            fig.add_trace(go.Scatter(
                x=monthly_data.index,
                y=monthly_data['Income'],
                name='Income',
                line=dict(color='#4CAF50', width=3),
                stackgroup='one'
            ))
        
        if 'Expense' in monthly_data.columns:
            fig.add_trace(go.Scatter(
                x=monthly_data.index,
                y=monthly_data['Expense'],
                name='Expenses',
                line=dict(color='#F44336', width=3),
                stackgroup='one'
            ))
        
        fig.add_trace(go.Scatter(
            x=monthly_data.index,
            y=monthly_data['Net'],
            name='Net Balance',
            line=dict(color='#2196F3', width=3, dash='dot')
        ))
        
        fig.update_layout(
            title='Monthly Financial Trends',
            xaxis_title='Month',
            yaxis_title='Amount (KSH)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating trend chart: {e}")
        return go.Figure()

def create_category_sunburst(df):
    if df.empty:
        return None
    
    try:
        df_expenses = df[df['type'] == 'Expense']
        if df_expenses.empty:
            return None
        
        fig = px.sunburst(
            df_expenses,
            path=['category', 'name'],
            values='amount',
            color='category',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title='Expense Breakdown'
        )
        
        fig.update_layout(
            margin=dict(t=40, l=0, r=0, b=0),
            height=500
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating sunburst chart: {e}")
        return None