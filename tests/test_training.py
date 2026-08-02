"""training 模块单元测试:训练/评估/AUC 门禁/产物保存/命令行入口。

端到端测试使用仓库内真实数据前 500 行(路径由测试文件定位,不依赖 cwd)。
"""

import json
from pathlib import Path

import pytest

from bank_sys.training import (
    DEFAULT_AUC_THRESHOLD,
    METRICS_FILE,
    MODEL_FILE,
    check_auc_gate,
    main,
    save_artifacts,
    train_pipeline,
)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "train.csv"


def test_train_pipeline_returns_metrics(real_subset):
    # Act
    pipeline, metrics = train_pipeline(real_subset)

    # Assert
    assert set(metrics) >= {"auc", "accuracy", "f1", "confusion_matrix", "n_samples"}
    assert 0 <= metrics["auc"] <= 1
    assert metrics["n_samples"] == 800  # 4000 行 × 0.2


def test_trained_pipeline_predicts_subset(real_subset):
    # Arrange
    pipeline, _ = train_pipeline(real_subset)

    # Act: 对前 10 行推理
    X = real_subset.head(10).drop(columns=["id", "subscribe"])
    proba = pipeline.predict_proba(X)[:, 1]

    # Assert
    assert len(proba) == 10
    assert ((proba >= 0) & (proba <= 1)).all()


def test_train_pipeline_auc_above_gate(real_subset):
    # Arrange / Act
    pipeline, metrics = train_pipeline(real_subset)

    # Assert: 真实数据 AUC 应远高于门禁(经典数据集梯度提升可达 0.9+)
    assert metrics["auc"] >= DEFAULT_AUC_THRESHOLD


def test_check_auc_gate_fails_below_threshold():
    # Act / Assert
    with pytest.raises(ValueError, match="低于门禁"):
        check_auc_gate({"auc": 0.5})


def test_check_auc_gate_passes_above_threshold():
    # 不应抛异常
    check_auc_gate({"auc": 0.9})


def test_save_artifacts(tmp_path, real_subset):
    # Arrange
    pipeline, metrics = train_pipeline(real_subset)

    # Act
    out = save_artifacts(pipeline, metrics, tmp_path)

    # Assert
    assert (out / MODEL_FILE).exists()
    saved = json.loads((out / METRICS_FILE).read_text(encoding="utf-8"))
    assert saved["auc"] == metrics["auc"]


def test_main_end_to_end(tmp_path, real_subset):
    # Arrange: 用小数据文件走完整命令行入口
    small = DATA_PATH.parent / "train.csv"
    assert small.exists()

    # Act
    code = main(
        [
            "--data",
            str(small),
            "--output-dir",
            str(tmp_path),
        ]
    )

    # Assert: 退出码 0,产物生成
    assert code == 0
    assert (tmp_path / MODEL_FILE).exists()
    assert (tmp_path / METRICS_FILE).exists()
