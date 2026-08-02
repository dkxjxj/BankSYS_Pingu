"""BankSYS_Pingu 应用入口(US-1 最小骨架,US-2/4 起逐步丰富)。"""

from pathlib import Path

import pandas as pd
import streamlit as st

from bank_sys.data_loader import load_data, overview

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "train.csv"

st.set_page_config(page_title="BankSYS_Pingu", page_icon="🐧", layout="wide")


@st.cache_data
def _cached_load(path: str) -> pd.DataFrame:
    return load_data(path)


def main() -> None:
    st.title("🐧 BankSYS_Pingu")
    st.caption("基于银行营销数据的分析与认购预测系统")
    st.markdown("功能规划:数据分析看板 · 认购预测(即将上线)")

    try:
        df = _cached_load(str(DATA_PATH))
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"数据加载失败: {exc}")
        st.stop()

    info = overview(df)
    st.success(f"数据加载成功: {info['n_rows']:,} 行 × {info['n_columns']} 列")
    st.dataframe(df.head(100))


main()
