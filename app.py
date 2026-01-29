import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.graph_objects as go

# 1. 页面基本配置
st.set_page_config(page_title="WOOFi Business Dashboard", layout="wide")
st.title("📊 WOOFi Weekly Business Dashboard")

try:
    # 2. 初始化数据库连接
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)

    # 3. 从 Supabase 读取数据
    res = supabase.table("weekly_reports").select("*").execute()
    df = pd.DataFrame(res.data)

    if not df.empty:
        # 4. 数据预处理与去重
        df['created_at'] = pd.to_datetime(df['created_at'])
        # 按时间排序并根据日期范围去重，确保图表不打结
        df = df.sort_values('created_at').drop_duplicates(subset=['date_range'], keep='last')
        
        # 稳健的数字清洗逻辑：剔除 $ 和 ,
        cols = ['swap_vol', 'pro_vol', 'swap_rev', 'pro_rev', 'kronos_rev', 'rank']
        for c in cols:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace('[$,]', '', regex=True), errors='coerce').fillna(0)

        # 5. 顶部核心指标展示
        last = df.iloc[-1]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Last Week Swap Vol", f"${last['swap_vol']:,.0f}")
        m2.metric("Last Week Pro Vol", f"${last['pro_vol']:,.0f}")
        total_rev = last['swap_rev'] + last['pro_rev'] + last['kronos_rev']
        m3.metric("Last Week Revenue(woofi+kronos)", f"${total_rev:,.0f}")
        m4.metric("Current Rank", f"#{int(last['rank'])}")

        st.divider()

        # 6. 第一行图表：业务增长趋势 (Volume & Revenue)
        st.subheader("📈 Business Growth Trends")
        c1, c2 = st.columns(2)

        with c1:
            # 交易量折线图
            fig_v = go.Figure()
            fig_v.add_trace(go.Scatter(x=df['date_range'], y=df['swap_vol'], name='Swap Vol', line=dict(color='#00FFA3', width=3)))
            fig_v.add_trace(go.Scatter(x=df['date_range'], y=df['pro_vol'], name='Pro Vol', line=dict(color='#00E0FF', width=3)))
            fig_v.update_layout(title="Weekly Volume ($)", hovermode="x unified", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_v, use_container_width=True)

        with c2:
            # 收入细分折线图
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatter(x=df['date_range'], y=df['swap_rev'], name='Swap Rev', line=dict(color='#FF4B4B', width=2)))
            fig_r.add_trace(go.Scatter(x=df['date_range'], y=df['pro_rev'], name='Pro Rev', line=dict(color='#FFAA00', width=2)))
            fig_r.add_trace(go.Scatter(x=df['date_range'], y=df['kronos_rev'], name='Kronos Rev', line=dict(dash='dot', color='#AA00FF', width=2)))
            fig_r.update_layout(title="Weekly Revenue Breakdown ($)", hovermode="x unified", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_r, use_container_width=True)

        # 7. 第二行图表：市场排名趋势 (Rank)
        st.subheader("🏆 Market Ranking Trend")
        if not df[df['rank'] > 0].empty:
            fig_rank = go.Figure()
            fig_rank.add_trace(go.Scatter(
                x=df['date_range'], y=df['rank'], mode='lines+markers', 
                name='Market Rank',
                line=dict(color='#FFD700', width=4), 
                marker=dict(size=12, color='#FFD700')
            ))
            fig_rank.update_layout(
                yaxis=dict(autorange="reversed", title="Rank (Lower is Better)"), 
                height=350, 
                hovermode="x unified"
            )
            st.plotly_chart(fig_rank, use_container_width=True)

        # 8. 底部历史明细表
        with st.expander("📂 View Full Historical Data Details"):
            st.dataframe(df.sort_values('created_at', ascending=False), use_container_width=True)
            
    else:
        st.info("💡 暂无数据。请通过 Telegram Bot 发送数据并刷新页面。")

except Exception as e:
    st.error(f"❌ 运行错误: {e}")
