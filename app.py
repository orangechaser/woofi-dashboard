import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.graph_objects as go

# 页面配置
st.set_page_config(page_title="WOOFi Business Dashboard", layout="wide")
st.title("📊 WOOFi weekly dashboard")

try:
    # 1. 链接数据库
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)

    # 2. 读取数据
    response = supabase.table("weekly_reports").select("*").execute()
    data = pd.DataFrame(response.data)

    if not data.empty:
        # 数据预处理：转换时间并排序
        data['created_at'] = pd.to_datetime(data['created_at'])
        data = data.sort_values('created_at')
        
        # 强制转换数值列，防止计算出错
        num_cols = ['swap_vol', 'pro_vol', 'swap_rev', 'pro_rev', 'kronos_rev', 'rank']
        for col in num_cols:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

        # 3. 顶部指标卡片 (Metrics)
        latest = data.iloc[-1]
        m1, m2, m3, m4 = st.columns(4)
        
        m1.metric("Last week (Swap)", f"${latest['swap_vol']:,.0f}")
        m2.metric("Last week (Pro)", f"${latest['pro_vol']:,.0f}")
        
        # 计算最新一笔的总收入
        latest_total_rev = latest['swap_rev'] + latest['pro_rev'] + latest['kronos_rev']
        m3.metric("Total Revenue", f"${latest_total_rev:,.0f}")
        
        m4.metric("Last Rank", f"{int(latest['rank'])}")

        st.divider()

        # 4. 图表区域：左右分栏
        st.subheader("📈 业务趋势分析")
        col_left, col_right = st.columns(2)

        # --- 左侧：Volume 趋势图 ---
        with col_left:
            fig_vol = go.Figure()
            # Swap Volume 线条
            fig_vol.add_trace(go.Scatter(
                x=data['date_range'], 
                y=data['swap_vol'],
                name='Swap Vol',
                mode='lines+markers',
                line=dict(width=3, color='#00FFA3'),
                hovertemplate="<b>Swap Vol:
