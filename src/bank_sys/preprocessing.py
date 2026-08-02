"""特征预处理:数值标准化 + 分类 OneHot,含未知类别兜底(US-3 AC4)。

未知类别兜底:OneHotEncoder(handle_unknown="ignore") 在推理时遇到
训练集未出现的类别编码为全 0,不会崩溃(见 PROGRESS GOTCHAS)。
"""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from bank_sys.data_loader import (
    CATEGORICAL_COLUMNS,
    FEATURE_COLUMNS,
    NUMERIC_COLUMNS,
    TARGET_COLUMN,
)


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """划分特征矩阵 X(20 列)与目标序列 y(0/1)。

    Raises:
        ValueError: 缺少必需特征列。
    """
    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"数据缺少特征列: {missing}")
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"数据缺少目标列: {TARGET_COLUMN}")
    X = df[FEATURE_COLUMNS]
    y = (df[TARGET_COLUMN] == "yes").astype(int)
    return X, y


def build_preprocessor() -> ColumnTransformer:
    """数值列标准化 + 分类列 OneHot(未知类别兜底为全 0)。"""
    numeric_pipe = Pipeline([("scaler", StandardScaler())])
    categorical_pipe = Pipeline(
        [("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, NUMERIC_COLUMNS),
            ("cat", categorical_pipe, CATEGORICAL_COLUMNS),
        ]
    )
