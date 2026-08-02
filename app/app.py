"""BankSYS_Pingu 应用入口:数据分析交互页面(US-2)。"""

from pathlib import Path

import pandas as pd
import streamlit as st

from bank_sys.analysis import (
    CATEGORICAL_COLUMNS,
    NUMERIC_COLUMNS,
    categorical_summary,
    describe_dataset,
    filter_data,
    plot_categorical_distribution,
    plot_correlation_heatmap,
    plot_numeric_distribution,
)
from bank_sys.data_loader import TARGET_COLUMN, load_data

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "train.csv"

st.set_page_config(page_title="BankSYS_Pingu", page_icon="🐧", layout="wide")


@st.cache_data
def _cached_load(path: str) -> pd.DataFrame:
    return load_data(path)


def _sidebar_filters(df: pd.DataFrame) -> dict[str, list[str]]:
    """侧边栏筛选控件,返回 {列名: 选中值列表}(US-2 AC4)。"""
    with st.sidebar:
        st.header("🔍 数据筛选")
        selected = {}
        for col in ("job", "month", "education"):
            options = sorted(df[col].dropna().unique().tolist())
            selected[col] = st.multiselect(f"{col}", options, default=options)
    return selected


def main() -> None:
    st.title("🐧 BankSYS_Pingu")
    st.caption("基于银行营销数据的分析与认购预测系统")
    st.markdown("左侧导航:📊 数据分析看板 · 🔮 在线认购预测")

    try:
        df = _cached_load(str(DATA_PATH))
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"数据加载失败: {exc}")
        st.stop()

    filters = _sidebar_filters(df)
    filtered = filter_data(df, filters)

    st.subheader("📊 数据集概览")
    rate = (filtered[TARGET_COLUMN] == "yes").mean()
    c1, c2, c3 = st.columns(3)
    c1.metric("总行数", f"{len(df):,}")
    c2.metric("筛选后行数", f"{len(filtered):,}")
    c3.metric("认购率", f"{rate:.1%}")
    st.dataframe(describe_dataset(filtered))
    with st.expander("查看原始数据前 100 行"):
        st.dataframe(filtered.head(100))

    if filtered.empty:
        st.warning("当前筛选条件下无数据,请调整筛选条件")
        st.stop()

    st.subheader("📈 单变量分布(按认购分组)")
    mode = st.radio("特征类型", ["数值型", "分类型"], horizontal=True)
    if mode == "数值型":
        col = st.selectbox("数值特征", NUMERIC_COLUMNS, index=0)
        st.pyplot(plot_numeric_distribution(filtered, col))
    else:
        col = st.selectbox("分类特征", CATEGORICAL_COLUMNS, index=0)
        st.pyplot(plot_categorical_distribution(filtered, col))
        st.dataframe(categorical_summary(filtered, col))

    st.subheader("🔗 特征相关性(数值特征)")
    corr = filtered[NUMERIC_COLUMNS].corr()
    if corr.empty:
        st.info("当前数据无可计算的数值特征")
    else:
        st.pyplot(plot_correlation_heatmap(filtered))
        with st.expander("查看相关性数值表"):
            st.dataframe(corr)


main()
