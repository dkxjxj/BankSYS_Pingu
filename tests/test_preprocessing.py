"""preprocessing 模块单元测试。"""

import numpy as np
import pytest

from bank_sys.data_loader import FEATURE_COLUMNS
from bank_sys.preprocessing import build_preprocessor, split_features_target


def test_split_features_target(sample_df):
    # Act
    X, y = split_features_target(sample_df)

    # Assert
    assert list(X.columns) == FEATURE_COLUMNS
    assert len(X) == len(sample_df)
    assert set(y) == {0, 1}


def test_split_features_target_missing_column(sample_df):
    # Arrange
    bad = sample_df.drop(columns=["age"])

    # Act / Assert
    with pytest.raises(ValueError, match="缺少特征列"):
        split_features_target(bad)


def test_split_features_target_missing_target(sample_df):
    # Arrange
    bad = sample_df.drop(columns=["subscribe"])

    # Act / Assert
    with pytest.raises(ValueError, match="缺少目标列"):
        split_features_target(bad)


def test_preprocessor_transform_shape(sample_df):
    # Act
    X, y = split_features_target(sample_df)
    pre = build_preprocessor().fit(X, y)
    X_t = pre.transform(X)

    # Assert: 每列至少保留特征,输出为稠密矩阵(sparse_output=False)
    assert X_t.shape[0] == len(sample_df)
    assert X_t.shape[1] >= len(FEATURE_COLUMNS)
    assert isinstance(X_t, np.ndarray)


def test_preprocessor_unknown_category_does_not_crash(sample_df):
    # Arrange: 用 job 列训练,推理时喂入训练时未出现的类别
    X, y = split_features_target(sample_df)
    pre = build_preprocessor().fit(X, y)
    X_new = sample_df.copy()
    X_new.loc[0, "job"] = "mystery_role"  # 训练集从未出现

    # Act: 不应崩溃(handle_unknown="ignore" 兜底为全 0)
    X_t = pre.transform(split_features_target(X_new)[0])

    # Assert
    assert X_t.shape[0] == len(sample_df)
