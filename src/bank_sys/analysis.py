"""数据分析计算与图表生成(纯函数,便于单元测试,规范 02 第 3 节)。

约定:图表内标签用英文(CI/服务器无中文字体,中文会变方块);
页面文字由 Streamlit 负责,不受影响。
"""

from __future__ import annotations

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from bank_sys.data_loader import (
    CATEGORICAL_COLUMNS,
    NUMERIC_COLUMNS,
    TARGET_COLUMN,
)


def describe_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """返回数据集概览表:列名、类型、非空数、缺失数、唯一值数。"""
    return pd.DataFrame(
        {
            "column": df.columns,
            "dtype": df.dtypes.astype(str).values,
            "non_null": df.notna().sum().values,
            "missing": df.isna().sum().values,
            "unique": df.nunique().values,
        }
    )


def categorical_summary(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """分类特征按类别的计数与认购率。

    Raises:
        ValueError: 列不存在或不是分类特征。
    """
    if col not in df.columns:
        raise ValueError(f"列不存在: {col}")
    if col not in CATEGORICAL_COLUMNS:
        raise ValueError(f"不是分类特征: {col}")
    grouped = df.groupby(col)[TARGET_COLUMN]
    summary = pd.DataFrame(
        {
            "count": grouped.size(),
            "subscribed": grouped.apply(lambda s: (s == "yes").sum()),
        }
    )
    summary["rate"] = summary["subscribed"] / summary["count"]
    return summary.reset_index()


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """数值特征的相关性矩阵(只取数据字典中定义的数值列)。"""
    cols = [c for c in NUMERIC_COLUMNS if c in df.columns]
    return df[cols].corr()


def filter_data(df: pd.DataFrame, filters: dict[str, list[str]]) -> pd.DataFrame:
    """按 {列名: 允许值列表} 过滤;值为空列表或 None 表示该列不过滤。"""
    mask = pd.Series(True, index=df.index)
    for col, values in filters.items():
        if values:
            mask &= df[col].isin(values)
    return df[mask]


def plot_numeric_distribution(df: pd.DataFrame, col: str) -> Figure:
    """数值特征直方图,按认购与否分组对比。"""
    fig, ax = _new_figure((8, 4))
    sns.histplot(data=df, x=col, hue=TARGET_COLUMN, multiple="layer", alpha=0.6, ax=ax)
    ax.set_title(f"Distribution of {col} by subscribe")
    return fig


def plot_categorical_distribution(df: pd.DataFrame, col: str) -> Figure:
    """分类特征计数条形图 + 各类别认购率折线(双轴)。"""
    summary = categorical_summary(df, col)
    fig, ax1 = _new_figure((9, 4))
    ax1.bar(summary[col], summary["count"], color="#4C72B0", alpha=0.8)
    ax1.set_ylabel("Count")
    ax2 = ax1.twinx()
    ax2.plot(summary[col], summary["rate"] * 100, "o-", color="#C44E52")
    ax2.set_ylabel("Subscribe rate (%)")
    ax1.set_title(f"Distribution and subscribe rate of {col}")
    return fig


def plot_correlation_heatmap(df: pd.DataFrame) -> Figure:
    """数值特征相关性热力图。"""
    corr = correlation_matrix(df)
    fig, ax = _new_figure((9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Correlation heatmap (numeric features)")
    return fig


def _new_figure(size: tuple[float, float]) -> tuple[Figure, object]:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=size)
    return fig, ax
