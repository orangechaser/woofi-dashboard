import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd

st.set_page_config(page_title="WOOFi 业务看板", layout="wide")

st.title("📊 WOOFi 业务周报数据看板")

# 连接数据库
conn = st.connection("supabase", type=SupabaseConnection)

# 读取数据 (从 weekly_reports 表)
try:
    df = conn.query("*", table="weekly_reports", ttl="0").execute()
    data = pd.DataFrame(df.data)

    if not data.empty:
        # 按创建时间排序
        data['created_at'] = pd.to_datetime(data['created_at'])
        data = data.sort_values('created_at')

        # 第一行：指标卡片
        col1, col2, col3 = st.columns(3)
        latest = data.iloc[-1]
        col1.metric("最新成交量 (Swap)", f"${latest['swap_vol']:,.0f}")
        col2.metric("最新收入 (Kronos)", f"${latest['kronos_rev']:,.0f}")
        col3.metric("最新排名", f"第 {latest['rank']} 名")

        # 第二行：图表
        st.divider()
        tab1, tab2 = st.tabs(["成交量趋势", "收入分布"])
        
        with tab1:
            st.subheader("Volume 趋势图")
            st.line_chart(data, x="date_range", y=["swap_vol", "pro_vol"])
            
        with tab2:
            st.subheader("Revenue 柱状图")
            st.bar_chart(data, x="date_range", y=["swap_rev", "pro_rev", "kronos_rev"])

        # 数据明细
        with st.expander("查看原始数据表"):
            st.dataframe(data)
    else:
        st.info("数据库里目前是空的，请先去 TG 发送数据。")
except Exception as e:
    st.error(f"连接出错啦: {e}")
