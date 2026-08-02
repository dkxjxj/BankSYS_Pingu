"""在线预测页面(US-4):20 个特征全点选式输入,输出认购结论与概率。

模型产物在 Docker 构建期训练生成(见 00 文档 ADR);本地开发未训练时
页面给出友好提示,不抛堆栈异常(US-4 AC6)。
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from bank_sys.data_loader import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, load_data
from bank_sys.predictor import ModelNotAvailableError, load_model, model_info, predict_one

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "train.csv"
MODEL_PATH = ROOT / "models" / "model.joblib"
METRICS_PATH = ROOT / "models" / "metrics.json"

st.set_page_config(page_title="在线预测", page_icon="🔮", layout="wide")
st.title("🔮 在线认购预测")
st.caption(
    "基于离线训练的模型,输入客户特征,预测其是否会认购定期存款。预测仅供辅助决策,不构成投资建议。"
)


@st.cache_data
def _cached_load(path: str) -> pd.DataFrame:
    return load_data(path)


@st.cache_resource
def _cached_model(path: str):
    return load_model(path)


def _example_row(df: pd.DataFrame) -> pd.Series | None:
    """示例客户(按钮触发后写入 session_state)。"""
    if st.session_state.get("use_example") and "example_row" not in st.session_state:
        st.session_state["example_row"] = df.sample(1, random_state=42).iloc[0]
    return st.session_state.get("example_row")


def _field_default(example: pd.Series | None, df: pd.DataFrame, col: str):
    """控件默认值:示例行优先,否则分类取众数、数值取中位数。

    注意:必须转成 Python 原生类型(str/float),Streamlit 控件不接受 numpy 类型。
    """
    if example is not None:
        if col in NUMERIC_COLUMNS:
            return float(example[col])
        return str(example[col])
    if col in CATEGORICAL_COLUMNS:
        return str(df[col].mode()[0])
    return float(df[col].median())


def main() -> None:
    try:
        df = _cached_load(str(DATA_PATH))
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"数据加载失败: {exc}")
        st.stop()

    st.button("🎲 填入示例客户", key="use_example")
    example = _example_row(df)

    st.subheader("👤 客户特征输入")
    features: dict[str, object] = {}
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**分类特征**")
        for col in CATEGORICAL_COLUMNS:
            options = sorted(df[col].dropna().unique().tolist())
            default = _field_default(example, df, col)
            features[col] = st.selectbox(
                col, options, index=options.index(default) if default in options else 0
            )

    with col_right:
        st.markdown("**数值特征**")
        for col in NUMERIC_COLUMNS:
            default = _field_default(example, df, col)
            features[col] = st.number_input(col, value=default, step=1.0, format="%.1f")

    st.divider()
    if st.button("🔮 预测是否认购", type="primary"):
        try:
            model = _cached_model(str(MODEL_PATH))
            result = predict_one(model, features)
        except ModelNotAvailableError as exc:
            st.error(str(exc))
            st.stop()

        if result["prediction"] == "yes":
            st.success("预测结论:**会认购** 🎯")
        else:
            st.info("预测结论:**不会认购**")

        c1, c2 = st.columns(2)
        c1.metric("认购概率", f"{result['probability']:.1%}")
        info = model_info(model)
        c2.metric("模型", info["classifier"])

        if METRICS_PATH.exists():
            metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
            st.caption(
                f"模型验证指标:AUC {metrics['auc']:.4f} · 准确率 {metrics['accuracy']:.4f} · "
                f"F1 {metrics['f1']:.4f}({metrics['n_samples']} 个验证样本)"
            )


main()
