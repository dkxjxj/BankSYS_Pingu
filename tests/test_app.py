"""Streamlit 页面级集成测试(AppTest,规范 03 集成层)。

注意:页面渲染 seaborn 图表较慢,统一用 60s 超时(默认 3s 会超)。
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from bank_sys.data_loader import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS

APP_PATH = Path(__file__).resolve().parents[1] / "app" / "app.py"
PREDICT_PAGE_PATH = Path(__file__).resolve().parents[1] / "app" / "pages" / "1_在线预测.py"
RUN_TIMEOUT = 60


def test_app_loads_data_without_exception():
    # Act: 完整跑一遍页面脚本
    at = AppTest.from_file(str(APP_PATH)).run(timeout=RUN_TIMEOUT)

    # Assert: 无异常,概览指标渲染
    assert not at.exception
    assert len(at.dataframe) >= 1
    assert at.metric[0].value == "22,500"


def test_app_sidebar_filter_changes_data():
    # Act: 默认多选全选 → 不筛选;改为只保留两类职业后再跑
    # 注意:Multiselect.select() 是追加语义,默认全选下无变化,须用 set_value 整体替换
    at = AppTest.from_file(str(APP_PATH)).run(timeout=RUN_TIMEOUT)
    at.sidebar.multiselect[0].set_value(["admin.", "student"])
    at.run(timeout=RUN_TIMEOUT)

    # Assert: 筛选后行数小于总数
    assert at.metric[1].value != "22,500"


def test_predict_page_renders_without_exception():
    # Act: 预测页完整渲染(20 个特征控件 + 预测按钮)
    at = AppTest.from_file(str(PREDICT_PAGE_PATH)).run(timeout=RUN_TIMEOUT)

    # Assert: 无异常,表单控件齐全
    assert not at.exception
    assert len(at.selectbox) == len(CATEGORICAL_COLUMNS)
    assert len(at.number_input) == len(NUMERIC_COLUMNS)
    assert len(at.button) >= 2  # 示例填充 + 预测


def test_predict_page_click_predict_no_crash():
    # Act: 点击预测按钮(CI 无模型产物 → 应显示友好错误而非堆栈异常)
    at = AppTest.from_file(str(PREDICT_PAGE_PATH)).run(timeout=RUN_TIMEOUT)
    at.button[1].click()
    at.run(timeout=RUN_TIMEOUT)

    # Assert: 页面不崩溃;有模型则显示结论(success/info 二态),无模型则显示友好提示
    assert not at.exception
    if at.success or at.info:
        result = at.success[0].value if at.success else at.info[0].value
        assert "认购" in result
    elif at.error:
        assert "模型产物不存在" in at.error[0].value
    else:
        pytest.fail("预测按钮点击后既无结果也无友好提示")
