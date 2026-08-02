"""pytest 共享配置与 fixture。"""

from pathlib import Path

import matplotlib

# 无显示环境下图表测试必须用 Agg 后端,避免弹出窗口/报错
matplotlib.use("Agg")

import pandas as pd
import pytest

from bank_sys.data_loader import NUMERIC_COLUMNS, REQUIRED_COLUMNS, load_data


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """构造接近真实分布的 6 行小样本:4 种职业、2 个月份、混合认购。"""
    n = 6
    data = {col: [f"v{i}_{col}"] * n for i, col in enumerate(REQUIRED_COLUMNS)}
    df = pd.DataFrame(data)
    for i, col in enumerate(NUMERIC_COLUMNS):
        df[col] = [float(i * 10 + j) for j in range(n)]
    df["age"] = [25, 35, 45, 55, 65, 75]
    df["subscribe"] = ["yes", "no", "yes", "no", "yes", "no"]
    df["job"] = ["admin.", "admin.", "services", "services", "student", "student"]
    df["month"] = ["jan", "jan", "feb", "feb", "mar", "mar"]
    df["education"] = ["secondary", "secondary", "tertiary", "tertiary", "primary", "primary"]
    df["duration"] = [100.0, 200.0, 300.0, 400.0, 500.0, 600.0]
    return df


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "train.csv"


@pytest.fixture(scope="module")
def real_subset() -> pd.DataFrame:
    """真实数据前 4000 行(训练/预测端到端测试共用)。

    数据量选择依据:实测 500 行 AUC≈0.71、1500 行≈0.84、3000 行≈0.85,
    4000 行稳定过 0.85 门禁且训练 <1s(2026-08-02 实测)。
    """
    return load_data(DATA_PATH).head(4000)
