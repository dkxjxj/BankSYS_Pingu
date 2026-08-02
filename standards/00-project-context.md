# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。
> **填写方式**:把 `<...>` 替换成真实内容;用不到的行删掉。

---

## 1. 项目是什么

- **项目名称**:`BankSYS_Pingu`
- **一句话目标**:基于银行营销数据集,提供「数据分析交互页面」与「是否认购定期存款」的在线预测系统,并跑通完整 CI + CD。
- **使用者/受益者**:银行营销分析人员、业务决策者、课程评审。
- **核心功能**:
  - 数据分析交互页面:数据概览、单变量分布、目标变量(认购)交叉分析、相关性与筛选联动。
  - 离线训练 + 在线预测:离线训练脚本产出模型与指标报告;在线预测页面以点选/滑块形式输入特征,输出是否认购与认购概率。
- **输入/数据**:`data/train.csv`(22,500 行)、`data/test.csv`(7,500 行),公开教学数据(葡萄牙银行营销数据集结构),共约 3.7MB,**进 Git**(CI/CD 需要,`05` 标准允许公开教学数据入库)。20 个特征 + 目标列 `subscribe`(yes/no);`id` 仅作行号,不参与建模。模型产物 **不进 Git**。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 课程标准版本,数据/ML 生态成熟 |
| Web/API 框架 | Streamlit | 数据分析看板 + 点选式表单天然契合,零前端成本 |
| ML/数据处理 | scikit-learn + pandas | 训练速度快、无原生编译依赖,`HistGradientBoostingClassifier` 开箱即用 |
| 测试 | pytest (+ streamlit.testing.AppTest) | 单元/集成测试 + Streamlit 页面级测试 |
| 格式/静态检查 | ruff (format + check) | 规范 02 推荐 |
| 打包/运行 | Docker | 镜像自包含,训练与推理可在同一容器闭环 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
BankSYS_Pingu/
├── standards/                 # AI 项目记忆与通用规范
├── app/
│   ├── app.py                 # Streamlit 主入口(数据分析页 + 预测页)
│   └── pages/                 # 多页应用拆分(数据分析 / 在线预测)
├── src/bank_sys/
│   ├── data_loader.py         # 数据加载与概览统计
│   ├── preprocessing.py       # 特征编码/清洗(含未知类别兜底)
│   ├── training.py            # 离线训练管线(评估 + 模型产物 + 指标报告)
│   └── predictor.py           # 模型加载 + 单样本推理(纯函数)
├── tests/                     # pytest 测试(单测 + AppTest 集成)
├── data/                      # train.csv / test.csv(公开教学数据,进 Git)
├── models/                    # 模型产物目录(不进 Git,Docker 构建期生成)
├── requirements.txt           # 生产运行依赖
├── requirements-dev.txt       # 本地/CI 检查依赖
├── Dockerfile                 # 容器部署(构建期完成离线训练)
├── .github/workflows/
│   ├── ci.yml
│   └── cd.yml
├── .gitignore
├── LICENSE                    # 开源协议(建议 MIT)
└── README.md
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` |
| 覆盖率 | `pytest --cov --cov-fail-under=80` |
| 构建 | `docker build` 成功(CI 执行,本地不强制) |
| 业务/模型指标 | 训练脚本门禁:验证集 AUC ≥ 0.85,不达标以非零码退出(`--check-auc` 等价物) |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 大文件、数据集、模型产物是否进 Git:数据集进 Git(公开、小);模型产物(`models/`)默认 **不进 Git**,由 Docker 构建期训练生成。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- 预测页面必须「点选式输入」,不允许自由文本输入。

## 6. 部署/CI 占位符取值

> `guides/` 和 workflow 里的通用占位符,在本项目里的真实值只写这里。

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `BankSYS_Pingu` | 镜像名/容器名/仓库名 |
| `<DEPLOY_DIR>` | `/opt/BankSYS_Pingu` | 服务器部署目录 |
| `<PORT>` | `8888` | 主机端口(优先),回退段 `8888`–`8897` |
| `<PORT_IN>` | `8501` | 容器内固定端口(Streamlit 默认) |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `_stcore/health` | Streamlit 内建健康检查端点(注意:旧文档的 `/healthz` 在新版返回 HTML 页面,不可用),`curl -fsS http://localhost:8888/_stcore/health` 返回 `ok` |
| `<SSH_USER>` | 待配 | 部署用户,如 `root` 或 `deploy` |
| `<SSH_HOST>` | 待配 | 服务器公网 IP 或域名 |
