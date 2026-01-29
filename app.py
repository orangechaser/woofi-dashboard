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

    response = supabase.table("weekly_reports").select("*").execute()
    data = pd.DataFrame(response.data)

    if not data.empty:
        data['created_at'] = pd.to_datetime(data['created_at'])
        data = data.sort_values('created_at')
        
        # 指标卡片
        latest = data.iloc[-1]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Last week (Swap)", f"${latest['swap_vol']:,.0f}")
        m2.metric("Last week (Pro)", f"${latest['pro_vol']:,.0f}")
        total_rev = float(latest['swap_rev']) + float(latest['pro_rev']) + float(latest['kronos_rev'])
        m3.metric("Total Revenue", f"${total_rev:,.0f}")
        m4.metric("Last Rank", f"{latest['rank']}")

        st.divider()

        st.subheader("📈 Volume & Revenue 趋势")

        # --- 优化的图表部分 ---
        fig = go.Figure()

        # Swap Vol 折线：移除了 Duration，只保留具体数值
        fig.add_trace(go.Scatter(
            x=data['date_range'], 
            y=data['swap_vol'],
            name='Swap Volume',
            mode='lines+markers',
            line=dict(width=3, color='#00FFA3'), # WOOFi 风格的青绿色
            hovertemplate="<b>Swap Vol:</b> $%{y:,.0f}<extra></extra>"
        ))

        # Pro Vol 折线
        fig.add_trace(go.Scatter(
            x=data['date_range'], 
            y=data['pro_vol'],
            name='Pro Volume',
            mode='lines+markers',
            line=dict(width=3, color='#FF4B4B'), # 红色
            hovertemplate="<b>Pro Vol:</b> $%{y:,.0f}<extra></extra>"
        ))

        fig.update_layout(
            hovermode="x unified", # 鼠标移动时，会自动在顶部显示 X 轴的日期
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0),
            height=450,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("查看所有历史数据明细"):
            st.dataframe(data.sort_values('created_at', ascending=False))
            
    else:
        st.info("💡 数据库目前没有数据，请通过 Telegram 发送数据后刷新。")

except Exception as e:
    st.error(f"❌ 运行出错: {e}")
