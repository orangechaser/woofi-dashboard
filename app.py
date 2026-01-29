import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.graph_objects as go

# 1. 页面配置
st.set_page_config(page_title="WOOFi Business Dashboard", layout="wide")
st.title("📊 WOOFi Weekly Business Dashboard")

try:
    # 2. 数据库连接
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)

    # 3. 获取数据
    response = supabase.table("weekly_reports").select("*").execute()
    data = pd.DataFrame(response.data)

    if not data.empty:
        # 4. 数据预处理
        data['created_at'] = pd.to_datetime(data['created_at'])
        
        # 【重要更新】自动去重：如果日期范围(date_range)重复，只保留最后录入的一条
        data = data.sort_values('created_at', ascending=True)
        data = data.drop_duplicates(subset=['date_range'], keep='last')
        
        # 强制数值转换（增强稳定性）
        num_cols = ['swap_vol', 'pro_vol', 'swap_rev', 'pro_rev', 'kronos_rev', 'rank']
        for col in num_cols:
            if data[col].dtype == 'object':
                data[col] = data[col].str.replace('$', '').str.replace(',', '')
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

        # 5. 顶部核心指标卡片
        latest = data.iloc[-1]
        m1, m2, m3, m4 = st.columns(4)
        
        m1.metric("Last Week Swap Vol", f"${latest['swap_vol']:,.0f}")
        m2.metric("Last Week Pro Vol", f"${latest['pro_vol']:,.0f}")
        
        total_rev = latest['swap_rev'] + latest['pro_rev'] + latest['kronos_rev']
        m3.metric("Total Weekly Revenue", f"${total_rev:,.0f}")
        m4.metric("Current Rank", f"#{int(latest['rank'])}")

        st.divider()

        # 6. 图表行 1：交易量与收入趋势
        st.subheader("📈 Business Growth Trends")
        c1, c2 = st.columns(2)

        with c1:
            fig_v = go.Figure()
            fig_v.add_trace(go.Scatter(x=data['date_range'], y=data['swap_vol'], name='Swap Vol', line=dict(color='#00FFA3', width=3)))
            fig_v.add_trace(go.Scatter(x=data['date_range'], y=data['pro_vol'], name='Pro Vol', line=dict(color='#00E0
