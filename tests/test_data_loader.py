"""data_loader 单元测试:正常、边界、异常三类输入(规范 03 第 3 节)。"""

import pandas as pd
import pytest

from bank_sys import data_loader


def _make_csv(path, n_rows=3) -> None:
    """生成含全部必需列的最小 CSV。"""
    df = pd.DataFrame(
        {c: [f"v{i}_{c}"] * n_rows for i, c in enumerate(data_loader.REQUIRED_COLUMNS)}
    )
    df.to_csv(path, index=False)


def test_load_data_ok(tmp_path):
    # Arrange
    path = tmp_path / "train.csv"
    _make_csv(path, n_rows=5)

    # Act
    df = data_loader.load_data(path)

    # Assert
    assert len(df) == 5
    assert set(data_loader.REQUIRED_COLUMNS) <= set(df.columns)


def test_load_data_missing_file(tmp_path):
    # Arrange
    missing = tmp_path / "nope.csv"

    # Act / Assert
    with pytest.raises(FileNotFoundError):
        data_loader.load_data(missing)


def test_load_data_missing_column(tmp_path):
    # Arrange
    path = tmp_path / "bad.csv"
    pd.DataFrame({"id": [1], "age": [30]}).to_csv(path, index=False)

    # Act / Assert
    with pytest.raises(ValueError, match="缺少必需列"):
        data_loader.load_data(path)


def test_load_data_empty(tmp_path):
    # Arrange
    path = tmp_path / "empty.csv"
    pd.DataFrame(columns=data_loader.REQUIRED_COLUMNS).to_csv(path, index=False)

    # Act / Assert
    with pytest.raises(ValueError, match="数据为空"):
        data_loader.load_data(path)


def test_overview_counts_and_missing(tmp_path):
    # Arrange
    path = tmp_path / "train.csv"
    _make_csv(path, n_rows=4)
    df = data_loader.load_data(path)

    # Act
    info = data_loader.overview(df)

    # Assert
    assert info["n_rows"] == 4
    assert info["n_columns"] == len(data_loader.REQUIRED_COLUMNS)
    assert sum(info["missing"].values()) == 0
    assert info["target_counts"] == {df[data_loader.TARGET_COLUMN].iloc[0]: 4}


def test_feature_columns_excludes_id_and_target():
    # Arrange / Act / Assert
    assert data_loader.ID_COLUMN not in data_loader.FEATURE_COLUMNS
    assert data_loader.TARGET_COLUMN not in data_loader.FEATURE_COLUMNS
    assert len(data_loader.FEATURE_COLUMNS) == 20
