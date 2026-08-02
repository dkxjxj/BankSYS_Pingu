# BankSYS_Pingu

基于银行营销数据(`data/train.csv`,22,500 行)的 Streamlit 应用,包含两大功能:

1. **数据分析交互页面** — 数据概览、单变量分布、认购率交叉分析、相关性热力图、侧边栏筛选联动。
2. **在线预测系统** — 离线训练认购预测模型(AUC 0.8899),点选式输入 20 个客户特征,预测是否会认购定期存款。

技术栈:Python 3.11 · Streamlit · scikit-learn · pytest · ruff · Docker · GitHub Actions(公开仓库,完整 CI + CD)。

---

## 快速开始

### 1. 安装环境(首次)

```bash
# 建议用 uv 或 conda 建 Python 3.11 环境后:
pip install -r requirements.txt -r requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

`requirements.txt` 以可编辑方式安装项目自身(依赖由 `pyproject.toml` 统一管理),安装后**在任意目录**都能运行下述命令。

### 2. 离线训练模型(可选,镜像构建期会自动训练)

```bash
python -m bank_sys.training                 # 读 data/train.csv,产出 models/model.joblib + metrics.json
bank-sys-train                              # 等价命令(console script)
python -m bank_sys.training --data data/test.csv --output-dir /tmp/models   # 自定义数据/输出
```

模型质量门禁:验证集 AUC ≥ 0.85,不达标退出码非零。

### 3. 启动 Web 应用

```bash
streamlit run app/app.py
```

- 数据分析页:数据概览 + 筛选联动 + 分布图 + 相关性
- 在线预测页:点选式输入特征 → 认购结论 + 概率(需先训练,或使用镜像内置模型)

### 4. 测试与代码检查

```bash
ruff format --check .
ruff check .
pytest --cov=bank_sys --cov-fail-under=80
```

---

## 部署(CI + CD)

- **CI**(PR 触发):`ruff format` → `ruff check` → `pytest --cov --cov-fail-under=80` → 模型 AUC 门禁 → `docker build`。
- **CD**(合并 main 触发):SSH 同步到服务器 → 构建镜像(构建期自动训练)→ 起容器 `BankSYS_Pingu` → 健康检查 `/_stcore/health`。
- 端口:主机优先 **8888**,占用则自动回退 `8888`–`8897`;容器内固定 8501。
- 需要 GitHub Secrets:`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`。

## 目录结构

```text
BankSYS_Pingu/
├── standards/             # AI 项目记忆与工程规范(00 项目上下文 / 01 需求 / PROGRESS 进度 / 02~06 规范)
├── app/
│   ├── app.py             # 数据分析页
│   └── pages/1_在线预测.py # 在线预测页
├── src/bank_sys/          # 业务逻辑包(可安装)
│   ├── data_loader.py     # 数据加载与概览
│   ├── analysis.py        # 分析与图表
│   ├── preprocessing.py   # 特征预处理(未知类别兜底)
│   ├── training.py        # 离线训练管线
│   └── predictor.py       # 在线推理
├── tests/                 # 43 个测试,覆盖率 99.4%
├── data/                  # 公开教学数据(进 Git)
├── models/                # 模型产物(不进 Git,构建期生成)
└── .github/workflows/     # ci.yml / cd.yml
```

> 开发规范与项目活记忆见 `standards/`,含需求、进度、踩坑记录(GOTCHAS)。
