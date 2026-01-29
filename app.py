import streamlit as st
from supabase import create_client
import pandas as pd

st.set_page_config(page_title="WOOFi 业务看板", layout="wide")
st.title("📊 WOOFi 业务周报数据看板")

# 直接从 Streamlit 的 Secrets 中读取
# 请确保你在 Streamlit 控制台的 Secrets 框里只填了这两行：
# SUPABASE_URL = "你的URL"
# SUPABASE_KEY = "你的KEY"

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)

    # 读取数据
    response = supabase.table("weekly_reports").select("*").execute()
    data = pd.DataFrame(response.data)

    if not data.empty:
        # 数据处理：确保创建时间是时间格式
        data['created_at'] = pd.to_datetime(data['created_at'])
        data = data.sort_values('created_at')

        # 指标卡片
        col1, col2, col3 = st.columns(3)
        latest = data.iloc[-1]
        col1.metric("最新成交量 (Swap)", f"${float(latest['swap_vol']):,.0f}")
        col2.metric("最新收入 (Kronos)", f"${float(latest['kronos_rev']):,.0f}")
        col3.metric("最新排名", f"第 {latest['rank']} 名")

        st.divider()
        
        # 图表展示
        tab1, tab2 = st.tabs(["成交量趋势", "收入分布"])
        with tab1:
            st.line_chart(data, x="date_range", y=["swap_vol", "pro_vol"])
        with tab2:
            st.bar_chart(data, x="date_range", y=["swap_rev", "pro_rev", "kronos_rev"])

        with st.expander("查看原始数据表"):
            st.dataframe(data)
    else:
        st.info("数据库里目前是空的，请先去 TG 发送数据。")
except Exception as e:
    st.error(f"连接出错啦，请检查 Secrets 配置。错误详情: {e}")
