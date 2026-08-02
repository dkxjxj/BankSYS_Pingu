"""数据加载与概览统计。

核心逻辑与 I/O 分离:纯函数设计,便于单元测试(规范 02 第 3 节)。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# 数据集的 22 列:20 个特征 + id(行号,不参与建模)+ 目标 subscribe
REQUIRED_COLUMNS = [
    "id",
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
    "subscribe",
]
TARGET_COLUMN = "subscribe"
ID_COLUMN = "id"

# 训练特征(不含 id 与目标)
FEATURE_COLUMNS = [c for c in REQUIRED_COLUMNS if c not in (TARGET_COLUMN, ID_COLUMN)]

# 特征类型划分(数据字典固定,不依赖 dtype 推断)
NUMERIC_COLUMNS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]
CATEGORICAL_COLUMNS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]


def load_data(path: str | Path) -> pd.DataFrame:
    """加载 CSV 并做基础校验:文件存在、必需列齐全、非空。

    Raises:
        FileNotFoundError: 文件不存在。
        ValueError: 缺必需列或数据为空。
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"数据文件不存在: {p}")
    df = pd.read_csv(p)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"数据缺少必需列: {missing}")
    if df.empty:
        raise ValueError("数据为空")
    return df


def overview(df: pd.DataFrame) -> dict:
    """返回数据集概览统计:行数、列数、缺失值、目标分布。"""
    return {
        "n_rows": len(df),
        "n_columns": len(df.columns),
        "missing": df.isna().sum().to_dict(),
        "target_counts": df[TARGET_COLUMN].value_counts().to_dict(),
    }
