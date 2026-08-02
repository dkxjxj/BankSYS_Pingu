"""predictor 模块单元测试:模型加载/单样本推理/异常兜底(US-4 AC5)。"""

from pathlib import Path

import pandas as pd
import pytest

from bank_sys.data_loader import FEATURE_COLUMNS
from bank_sys.predictor import (
    PROB_THRESHOLD,
    ModelNotAvailableError,
    load_model,
    model_info,
    predict_one,
)
from bank_sys.training import save_artifacts, train_pipeline


@pytest.fixture(scope="module")
def trained_artifacts(tmp_path_factory, real_subset) -> tuple[Path, dict]:
    """真实数据训练一次,产物落临时目录,供预测测试共用。"""
    out = tmp_path_factory.mktemp("models")
    pipeline, metrics = train_pipeline(real_subset)
    save_artifacts(pipeline, metrics, out)
    return out, metrics


def _full_features(real_subset: pd.DataFrame, **overrides) -> dict[str, object]:
    """从真实数据第一行构造完整特征 dict。"""
    row = real_subset.iloc[0]
    features = {c: row[c] for c in FEATURE_COLUMNS}
    features.update(overrides)
    return features


def test_load_model_missing_raises(tmp_path):
    # Act / Assert
    with pytest.raises(ModelNotAvailableError, match="模型产物不存在"):
        load_model(tmp_path / "nope.joblib")


def test_load_model_and_predict_end_to_end(trained_artifacts, real_subset):
    # Arrange
    out, metrics = trained_artifacts
    model = load_model(out / "model.joblib")

    # Act
    result = predict_one(model, _full_features(real_subset))

    # Assert
    assert result["prediction"] in {"yes", "no"}
    assert 0 <= result["probability"] <= 1


def test_predict_one_missing_feature(trained_artifacts, real_subset):
    # Arrange
    model = load_model(trained_artifacts[0] / "model.joblib")
    features = _full_features(real_subset)
    del features["age"]

    # Act / Assert
    with pytest.raises(ValueError, match="缺少特征"):
        predict_one(model, features)


def test_predict_one_unknown_category_no_crash(trained_artifacts, real_subset):
    # Arrange: 分类值取训练集从未出现的值(OneHot handle_unknown 兜底)
    model = load_model(trained_artifacts[0] / "model.joblib")
    features = _full_features(real_subset, job="mystery_role", education="mystery_school")

    # Act: 不应崩溃
    result = predict_one(model, features)

    # Assert
    assert 0 <= result["probability"] <= 1


def test_predict_one_probability_consistency(trained_artifacts, real_subset):
    # Arrange
    model = load_model(trained_artifacts[0] / "model.joblib")
    features = _full_features(real_subset)
    features = {c: features[c] for c in FEATURE_COLUMNS}

    # Act
    result = predict_one(model, features)

    # Assert: 概率阈值与结论一致
    if result["probability"] >= PROB_THRESHOLD:
        assert result["prediction"] == "yes"
    else:
        assert result["prediction"] == "no"


def test_predict_one_probability_is_stable(trained_artifacts, real_subset):
    # Arrange: 同输入两次预测结果必须一致(确定性)
    model = load_model(trained_artifacts[0] / "model.joblib")
    features = _full_features(real_subset)

    # Act
    r1 = predict_one(model, features)
    r2 = predict_one(model, features)

    # Assert
    assert r1 == r2


def test_model_info(trained_artifacts):
    # Arrange
    model = load_model(trained_artifacts[0] / "model.joblib")

    # Act
    info = model_info(model)

    # Assert
    assert info["classifier"] == "HistGradientBoostingClassifier"
    assert len(info["classes"]) == 2
