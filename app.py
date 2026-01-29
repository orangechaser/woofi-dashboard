import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="WOOFi Business Dashboard", layout="wide")
st.title("📊 WOOFi Weekly Business Dashboard")

try:
    # 2. Database Connection
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)

    # 3. Fetch Data
    response = supabase.table("weekly_reports").select("*").execute()
    data = pd.DataFrame(response.data)

    if not data.empty:
        # Data Pre-processing
        data['created_at'] = pd.to_datetime(data['created_at'])
        data = data.sort_values('created_at')
        
        # Force numeric conversion for plotting and metrics
        num_cols = ['swap_vol', 'pro_vol', 'swap_rev', 'pro_rev', 'kronos_rev', 'rank']
        for col in num_cols:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

        # 4. Top Metrics Cards
        latest = data.iloc[-1]
        m1, m2, m3, m4 = st.columns(4)
        
        m1.metric("Last Week Swap Vol", f"${latest['swap_vol']:,.0f}")
        m2.metric("Last Week Pro Vol", f"${latest['pro_vol']:,.0f}")
        
        latest_total_rev = latest['swap_rev'] + latest['pro_rev'] + latest['kronos_rev']
        m3.metric("Total Weekly Revenue", f"${latest_total_rev:,.0f}")
        m4.metric("Current Rank", f"#{int(latest['rank'])}")

        st.divider()

        # 5. Charts Row 1: Volume and Revenue Breakdown
        st.subheader("📈 Business Growth Trends")
        col_left, col_right = st.columns(2)

        # --- Left: Volume Trend ---
        with col_left:
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Scatter(
                x=data['date_range'], y=data['swap_vol'],
                name='Swap Vol', mode='lines+markers',
                line=dict(width=3, color='#00FFA3'),
                hovertemplate="Swap Vol: $%{y:,.0f}<extra></extra>"
            ))
            fig_vol.add_trace(go.Scatter(
                x=data['date_range'], y=data['pro_vol'],
                name='Pro Vol', mode='lines+markers',
                line=dict(width=3, color='#00E0FF'),
                hovertemplate="Pro Vol: $%{y:,.0f}<extra></extra>"
            ))
            fig_vol.update_layout(
                title="Weekly Volume ($)",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=50, b=20),
                height=400,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig_vol, use_container_width=True)

        # --- Right: Revenue Breakdown ---
        with col_right:
            fig_rev = go.Figure()
            fig_rev.add_trace(go.Scatter(
                x=data['date_range'], y=data['swap_rev'],
                name='Swap Rev', mode='lines+markers',
                line=dict(width=2, color='#FF4B4B'),
                hovertemplate="Swap Rev: $%{y:,.0f}<extra></extra>"
            ))
            fig_rev.add_trace(go.Scatter(
                x=data['date_range'], y=data['pro_rev'],
                name='Pro Rev', mode='lines+markers',
                line=dict(width=2, color='#FFAA00'),
                hovertemplate="Pro Rev: $%{y:,.0f}<extra></extra>"
            ))
            fig_rev.add_trace(go.Scatter(
                x=data['date_range'], y=data['kronos_rev'],
                name='Kronos Rev', mode='lines+markers',
                line=dict(width=2, color='#AA00FF', dash='dot'),
                hovertemplate="Kronos Rev: $%{y:,.0f}<extra></extra>"
            ))
            fig_rev.update_layout(
                title="Weekly Revenue Breakdown ($)",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
