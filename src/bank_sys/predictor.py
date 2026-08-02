"""在线预测:模型加载 + 单样本推理(纯函数,便于测试,US-4)。

未知分类值由训练时的 OneHotEncoder(handle_unknown="ignore") 兜底为全 0,
推理不会崩溃(见 PROGRESS GOTCHAS)。模型产物缺失时抛 ModelNotAvailableError,
页面捕获后给出友好提示,不抛堆栈异常(US-4 AC6)。
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from bank_sys.data_loader import FEATURE_COLUMNS
from bank_sys.training import MODEL_FILE

DEFAULT_MODEL_PATH = Path("models") / MODEL_FILE
# 认购概率阈值:>= 0.5 判定为认购(与训练时的默认决策一致)
PROB_THRESHOLD = 0.5


class ModelNotAvailableError(RuntimeError):
    """模型产物缺失(尚未训练)时抛出。"""


def load_model(path: str | Path = DEFAULT_MODEL_PATH) -> Pipeline:
    """加载模型管线;缺失时抛 ModelNotAvailableError。"""
    p = Path(path)
    if not p.exists():
        raise ModelNotAvailableError(
            f"模型产物不存在: {p}。请先运行训练脚本: PYTHONPATH=src python -m bank_sys.training"
        )
    return joblib.load(p)


def predict_one(pipeline: Pipeline, features: dict[str, object]) -> dict:
    """单样本推理:返回 {prediction: "yes"|"no", probability: float}。

    Raises:
        ValueError: features 缺少必需特征列。
    """
    missing = [c for c in FEATURE_COLUMNS if c not in features]
    if missing:
        raise ValueError(f"缺少特征: {missing}")
    row = pd.DataFrame([{c: features[c] for c in FEATURE_COLUMNS}])
    proba = float(pipeline.predict_proba(row)[0, 1])
    return {
        "prediction": "yes" if proba >= PROB_THRESHOLD else "no",
        "probability": round(proba, 4),
    }


def model_info(pipeline: Pipeline) -> dict:
    """返回模型基本信息(分类器类型、类别标签),供页面展示。"""
    classifier = pipeline.named_steps["classifier"]
    return {
        "classifier": type(classifier).__name__,
        "classes": [str(c) for c in classifier.classes_],
    }
