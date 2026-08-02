"""analysis 模块单元测试:概览、分类汇总、过滤、相关性与图表函数。"""

import numpy as np
import pytest

from bank_sys import analysis
from bank_sys.data_loader import NUMERIC_COLUMNS, TARGET_COLUMN


def test_describe_dataset(sample_df):
    # Act
    info = analysis.describe_dataset(sample_df)

    # Assert
    assert len(info) == len(sample_df.columns)
    assert (info["missing"] == 0).all()
    assert info.loc[info["column"] == "age", "unique"].iloc[0] == 6


def test_categorical_summary_rate(sample_df):
    # Act
    summary = analysis.categorical_summary(sample_df, "job")

    # Assert
    admin = summary[summary["job"] == "admin."].iloc[0]
    assert admin["count"] == 2
    assert admin["subscribed"] == 1
    assert admin["rate"] == pytest.approx(0.5)


def test_categorical_summary_all_subscribed(sample_df):
    # Act
    summary = analysis.categorical_summary(sample_df, "month")

    # Assert: 每类 2 行,各有 1 个 yes
    # 注意:Series == pytest.approx 在 numpy 2.x 下不可靠,用 np.allclose
    assert np.allclose(summary["rate"], 0.5)


def test_categorical_summary_unknown_column(sample_df):
    with pytest.raises(ValueError, match="列不存在"):
        analysis.categorical_summary(sample_df, "not_a_column")


def test_categorical_summary_non_categorical(sample_df):
    with pytest.raises(ValueError, match="不是分类特征"):
        analysis.categorical_summary(sample_df, "age")


def test_filter_data_single_column(sample_df):
    # Act
    result = analysis.filter_data(sample_df, {"job": ["admin.", "services"]})

    # Assert
    assert len(result) == 4
    assert set(result["job"]) == {"admin.", "services"}


def test_filter_data_multiple_columns(sample_df):
    # Act
    result = analysis.filter_data(sample_df, {"job": ["admin.", "services"], "month": ["jan"]})

    # Assert
    assert len(result) == 2
    assert (result["month"] == "jan").all()


def test_filter_data_empty_values_no_filter(sample_df):
    # Act
    result = analysis.filter_data(sample_df, {"job": []})

    # Assert
    assert len(result) == len(sample_df)


def test_filter_data_no_match(sample_df):
    # Act
    result = analysis.filter_data(sample_df, {"job": ["blue-collar"]})

    # Assert
    assert result.empty


def test_correlation_matrix_columns(sample_df):
    # Act
    corr = analysis.correlation_matrix(sample_df)

    # Assert
    assert set(corr.columns) == set(NUMERIC_COLUMNS)
    assert np.allclose(corr.values, corr.values.T)


def test_plot_numeric_distribution(sample_df):
    # Act
    fig = analysis.plot_numeric_distribution(sample_df, "age")

    # Assert
    assert len(fig.axes) >= 1
    assert fig.axes[0].get_title() == "Distribution of age by subscribe"


def test_plot_categorical_distribution(sample_df):
    # Act
    fig = analysis.plot_categorical_distribution(sample_df, "job")

    # Assert: 双轴(计数轴 + 认购率轴)
    assert len(fig.axes) == 2
    assert "subscribe rate" in fig.axes[1].get_ylabel().lower()


def test_plot_correlation_heatmap(sample_df):
    # Act
    fig = analysis.plot_correlation_heatmap(sample_df)

    # Assert
    assert len(fig.axes) >= 1
    assert "correlation" in fig.axes[0].get_title().lower()


def test_target_column_mixed_in_sample(sample_df):
    # Assert: 样本同时含 yes/no,保证分组图测试有效
    assert set(sample_df[TARGET_COLUMN]) == {"yes", "no"}
