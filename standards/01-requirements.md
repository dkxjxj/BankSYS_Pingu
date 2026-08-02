# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 / 老师 / 产品 / 客户 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 项目初始化工程化与 CI/CD · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备基础工程结构(Streamlit 骨架)、测试、CI 与 Docker 化 CD,
以便 后续每次开发都能自动检查并自动部署。

验收标准:
- AC1: 从 `main` 开 feature 分支完成初始化,不直接 push main。
- AC2: 创建公开仓库 `BankSYS_Pingu`,含 `.gitignore`、`README.md`、`LICENSE`(MIT)、`requirements.txt` / `requirements-dev.txt`。
- AC3: PR 触发 CI,至少包含 `ruff format --check .`、`ruff check .`、`pytest --cov --cov-fail-under=80`、`docker build`。
- AC4: CI 全绿后合并 main。
- AC5: 合并 main 自动触发 CD:SSH 同步 → 构建镜像 → 起容器 `BankSYS_Pingu`(主机端口优先 8888,占用则在 8888–8897 回退)→ `curl /_stcore/health` 健康检查通过。
- AC6: 完成后更新 `standards/PROGRESS.md`。

技术备注:
- 容器内端口固定 8501(Streamlit 默认);主机端口优先 8888,可回退。
- 建仓后第一步配置 Secrets:`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`,否则 CD 必失败。

### US-2 数据分析交互页面 · 状态: Backlog

作为 **银行营销分析人员**,
我想要 在 Web 页面上交互式查看数据的分布、缺失与认购率情况,
以便 快速了解客户群体特征,为营销策略提供依据。

验收标准:
- AC1: Given 打开应用首页,Then 展示数据集概览(行数、列数、各列类型、缺失值统计),数据加载失败时给出明确错误提示。
- AC2: Given 数值型特征,When 选择该特征,Then 展示直方图(含按 `subscribe` 分组对比)。
- AC3: Given 分类型特征(job / marital / education / contact / month / day_of_week / default / housing / loan / poutcome),Then 展示类别分布条形图与各类别认购率。
- AC4: Given 侧边栏筛选控件(至少含 job、month、education),When 调整筛选条件,Then 页面图表与统计同步更新。
- AC5: 页面提供特征相关性热力图。
- AC6: 图表与统计计算逻辑抽成可测函数,单元测试覆盖正常与异常输入。

技术备注:
- 使用 Streamlit 多页结构(`app.py` + `pages/`),数据分析与预测分页。
- 图表基于 matplotlib/seaborn 或 plotly(选定后写入 PROGRESS 的 ADR)。

### US-3 离线训练管线与模型质量门禁 · 状态: Backlog

作为 **数据科学家**,
我想要 用历史营销数据离线训练一个认购预测模型并输出指标报告,
以便 评估模型质量,并将可用的模型产物交给在线预测系统使用。

验收标准:
- AC1: Given `data/train.csv`,When 运行训练脚本,Then 输出模型产物(`models/model.joblib`,含预处理管线 + 分类器)与指标报告(`models/metrics.json`),报告含 AUC、准确率、F1、混淆矩阵。
- AC2: 训练完全可复现(固定随机种子),同一数据两次运行指标一致。
- AC3: 验证集 AUC ≥ 0.85;不达标时训练脚本以非零退出码失败(CI 红灯)。
- AC4: 预测时遇到训练中未见过的分类值不崩溃,按兜底策略处理并可在预测接口返回提示。
- AC5: 数据加载、预处理、评估逻辑均有单元测试;`duration` 等敏感特征的处理方式在代码注释与 PROGRESS 中说明。

技术备注:
- 目标列 `subscribe`(yes/no),二分类;`id` 列不参与建模。
- 特征 20 个:age、job、marital、education、default、housing、loan、contact、month、day_of_week、duration、campaign、pdays、previous、poutcome、emp_var_rate、cons_price_index、cons_conf_index、lending_rate3m、nr_employed。

### US-4 在线预测系统 · 状态: Backlog

作为 **银行营销业务人员**,
我想要 通过点选方式录入一位客户的各项特征,即可获得其是否认购定期存款的预测结果,
以便 在电话营销前快速判断客户意向、提高营销效率。

验收标准:
- AC1: Given 预测页面,Then 全部 20 个特征均以点选/下拉/滑块形式输入(分类型用下拉框,数值型用滑块或数字输入),不允许自由文本输入。
- AC2: When 点击「预测」按钮,Then 显示预测结论(认购 / 不认购)与认购概率(0~100%),并展示所用模型版本与训练指标。
- AC3: Given 输入训练集中未出现过的分类选项,Then 页面不崩溃,给出明确提示并仍返回结果。
- AC4: 提供「填入示例客户」按钮,一键填充一条测试数据便于演示。
- AC5: 预测推理逻辑为纯函数(预处理 + 加载模型 + 预测),单元测试覆盖正常、边界(如 pdays=-1)、异常输入;覆盖率计入项目门槛。
- AC6: 页面标注「预测仅供辅助决策,不构成投资建议」。

技术备注:
- 模型产物缺失时(如开发环境未训练),页面提示先运行训练脚本,不抛堆栈异常。

---

## 5. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git。
- **可维护**:一需求一分支一 PR,PR 尽量小于 400 行。
- **可测试**:核心逻辑(数据处理、训练、推理)必须有单元测试,覆盖率 ≥ 80%。
- **可部署**:部署后必须健康检查(`/healthz`);主机端口 8888,占用自动回退。
- **可复现**:训练固定随机种子;数据集与依赖版本锁定(requirements 固定版本)。
- **性能**:单样本预测响应 ≤ 1 秒(本地机器参考值)。
