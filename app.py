import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="WOOFi Business Dashboard", layout="wide")
st.title("📊 WOOFi 业务周报数据看板")

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)

    # 读取数据
    response = supabase.table("weekly_reports").select("*").execute()
    data = pd.DataFrame(response.data)

    if not data.empty:
        # 数据转换与排序
        data['created_at'] = pd.to_datetime(data['created_at'])
        data = data.sort_values('created_at')
        
        # 1. 指标卡片区域
        latest = data.iloc[-1]
        m1, m2, m3, m4 = st.columns(4)
        
        m1.metric("Last week (Swap)", f"${latest['swap_vol']:,.0f}")
        m2.metric("Last week (Pro)", f"${latest['pro_vol']:,.0f}")
        
        # 计算 Total Revenue
        total_rev = float(latest['swap_rev']) + float(latest['pro_rev']) + float(latest['kronos_rev'])
        m3.metric("Total Revenue", f"${total_rev:,.0f}")
        
        m4.metric("Last Rank", f"{latest['rank']}")

        st.divider()

        # 2. 交互式图表 (Plotly)
        st.subheader("📈 Volume & Revenue 趋势 (鼠标悬停查看详情)")

        # 创建一个带有自定义 Tooltip 的图表
        fig = go.Figure()

        # 添加 Swap Vol 折线
        fig.add_trace(go.Scatter(
            x=data['date_range'], 
            y=data['swap_vol'],
            name='Swap Volume',
            mode='lines+markers',
            hovertemplate="<b>Duration:</b> %{x}<br><b>Swap Vol:</b> $%{y:,.0f}<extra></extra>"
        ))

        # 添加 Pro Vol 折线
        fig.add_trace(go.Scatter(
            x=data['date_range'], 
            y=data['pro_vol'],
            name='Pro Volume',
            mode='lines+markers',
            hovertemplate="<b>Duration:</b> %{x}<br><b>Pro Vol:</b> $%{y:,.0f}<extra></extra>"
        ))

        fig.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0),
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

        # 3. 原始数据
        with st.expander("查看所有历史数据明细"):
            st.dataframe(data.sort_values('created_at', ascending=False))
            
    else:
        st.info("💡 数据库目前没有数据，请通过 Telegram 发送数据后刷新。")

except Exception as e:
    st.error(f"❌ 运行出错: {e}")
