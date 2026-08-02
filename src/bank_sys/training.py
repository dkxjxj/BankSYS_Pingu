"""离线训练管线:训练 + 评估 + 模型产物 + AUC 质量门禁(US-3)。

设计:纯函数 + 命令行入口。CI/Docker 构建期调用,不达标以非零码退出。
模型产物(含预处理管线)整体序列化,预测时只需加载一个 joblib 文件。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from bank_sys.data_loader import load_data
from bank_sys.preprocessing import build_preprocessor, split_features_target

DEFAULT_AUC_THRESHOLD = 0.85
RANDOM_STATE = 42
MODEL_FILE = "model.joblib"
METRICS_FILE = "metrics.json"

# 默认路径基于包文件定位,与 cwd 无关(在任意目录执行命令都能读到数据/写到项目 models/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "train.csv"


def train_pipeline(
    df: pd.DataFrame, test_size: float = 0.2, random_state: int = RANDOM_STATE
) -> tuple[Pipeline, dict]:
    """训练并返回 (模型管线, 指标 dict)。分层划分保证类别比例一致。"""
    X, y = split_features_target(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    pipeline = Pipeline(
        [
            ("preprocessor", build_preprocessor()),
            ("classifier", HistGradientBoostingClassifier(random_state=random_state)),
        ]
    )
    pipeline.fit(X_train, y_train)
    metrics = evaluate(pipeline, X_test, y_test, random_state)
    return pipeline, metrics


def evaluate(
    pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series, random_state: int
) -> dict:
    """评估并返回指标 dict:AUC/准确率/F1/混淆矩阵/样本数。"""
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    return {
        "auc": round(roc_auc_score(y_test, y_proba), 4),
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "f1": round(f1_score(y_test, y_pred), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "n_samples": int(len(y_test)),
        "random_state": random_state,
    }


def check_auc_gate(metrics: dict, threshold: float = DEFAULT_AUC_THRESHOLD) -> None:
    """AUC 质量门禁(00 文档第 4 节):不达标抛异常,调用方退出码非零。"""
    if metrics["auc"] < threshold:
        raise ValueError(f"AUC {metrics['auc']:.4f} 低于门禁阈值 {threshold}")


def save_artifacts(pipeline: Pipeline, metrics: dict, output_dir: str | Path) -> Path:
    """保存模型产物与指标报告到输出目录,返回目录路径。"""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, out / MODEL_FILE)
    (out / METRICS_FILE).write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="离线训练认购预测模型")
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH), help="训练数据路径")
    parser.add_argument("--output-dir", default="models", help="模型产物输出目录")
    parser.add_argument("--auc-threshold", type=float, default=DEFAULT_AUC_THRESHOLD)
    args = parser.parse_args(argv)

    df = load_data(args.data)
    pipeline, metrics = train_pipeline(df)
    check_auc_gate(metrics, args.auc_threshold)
    out = save_artifacts(pipeline, metrics, args.output_dir)
    print(f"模型产物: {out / MODEL_FILE}")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
