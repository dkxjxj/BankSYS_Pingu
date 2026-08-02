"""Streamlit 页面级集成测试(AppTest,规范 03 集成层)。

注意:页面渲染 seaborn 图表较慢,统一用 60s 超时(默认 3s 会超)。
"""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app" / "app.py"
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
