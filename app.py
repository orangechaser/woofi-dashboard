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
        
        # Numeric conversion
        num_cols = ['swap_vol', 'pro_vol', 'swap_rev', 'pro_rev', 'kronos_rev', 'rank']
        for col in num_cols:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

        # 4. Top Metrics Cards
        latest = data.iloc[-1]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Last Week Swap Vol", f"${latest['swap_vol']:,.0f}")
        m2.metric("Last Week Pro Vol", f"${latest['pro_vol']:,.0f}")
        total_rev = latest['swap_rev'] + latest['pro_rev'] + latest['kronos_rev']
        m3.metric("Total Weekly Revenue", f"${total_rev:,.0f}")
        m4.metric("Current Rank", f"#{int(latest['rank'])}")

        st.divider()

        # 5. Charts Row 1: Volume and Revenue
        st.subheader("📈 Business Growth Trends")
        c1, c2 = st.columns(2)

        with c1:
            fig_v = go.Figure()
            fig_v.add_trace(go.Scatter(x=data['date_range'], y=data['swap_vol'], name='Swap Vol', line=dict(color='#00FFA3', width=3)))
            fig_v.add_trace(go.Scatter(x=data['date_range'], y=data['pro_vol'], name='Pro Vol', line=dict(color='#00E0FF', width=3)))
            fig_v.update_layout(title="Weekly Volume ($)", hovermode="x unified", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_v, use_container_width=True)

        with c2:
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatter(x=data['date_range'], y=data['swap_rev'], name='Swap Rev', line=dict(color='#FF4B4B', width=2)))
            fig_r.add_trace(go.Scatter(x=data['date_range'], y=data['pro_rev'], name='Pro Rev', line=dict(color='#FFAA00', width=2)))
            fig_r.add_trace(go.Scatter(x=data['date_range'], y=data['kronos_rev'], name='Kronos Rev', line=dict(dash='dot', color='#AA00FF', width=2)))
            fig_r.update_layout(title="Weekly Revenue Breakdown ($)", hovermode="x unified", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_r, use_container_width=True)

        # 6. Row 2: Rank Trend (Optimized Visibility)
        st.subheader("🏆 Market Ranking Trend")
        rank_df = data[data['rank'] > 0]
        if not rank_df.empty:
            fig_rank = go.Figure()
            fig_rank.add_trace(go.Scatter(
                x=rank_df['date_range'], 
                y=rank_df['rank'], 
                mode='lines+markers', 
                name='Market Rank',
                line=dict(color='#FFD700', width=4), # 亮金色/黄色
                marker=dict(size=12, color='#FFD700', symbol='circle'),
                fill='tonexty', # 增加填充感
                fillcolor='rgba(255, 215, 0, 0.1)'
            ))
            fig_rank.update_layout(
                yaxis=dict(autorange="reversed", title="Rank (Lower is Better)", gridcolor='rgba(255,255,255,0.1)'),
                xaxis=dict(showgrid=False),
                height=350,
                hovermode="x unified"
            )
            st.plotly_chart(fig_rank, use_container_width=True)
        else:
            st.info("No valid ranking data recorded yet.")

        # 7. Details Table
        with st.expander("📂 Historical Data Details"):
            st.dataframe(data.sort_values('created_at', ascending=False), use_container_width=True)
            
    else:
        st.info("No data found. Send data via Telegram first.")

except Exception as e:
    st.error(f"Error: {str(e)}")
