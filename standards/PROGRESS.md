# PROGRESS · BankSYS_Pingu 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by AI)

- **阶段**:`开发中(US-1 已完成并部署,准备 US-2)`
- **上一步完成**:US-1 完整链路跑通 ✅——PR #2 合并 → CD 失败(镜像 tag 大写)→ fix/1-deploy-image-tag PR #3 → 合并 → CD 成功部署到主机端口 **8890**(8888 被占,回退机制实测生效),健康检查 `/_stcore/health` 通过。
- **下一步 (TODO 第一条)**:开 `feature/2-data-analysis` 分支实现 US-2 数据分析交互页面。
- **阻塞项**:无。

---

## 待办清单 (TODO,按优先级)

- [x] **人类确认**:`00-project-context.md` / `01-requirements.md` / 本文件(含 ADR 决策项)
- [x] 六步① 建仓:公开仓库 `https://github.com/dkxjxj/BankSYS_Pingu` 已建,main 含引导提交(commit `84f2fc0`)
- [ ] ✋ 人类配置 GitHub Secrets:`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`(用 `gh secret list` 核对后继续)
- [ ] 六步② 开分支:`feature/1-project-init`(工程初始化,US-1)
- [ ] 工程骨架:`.gitignore`(排除 `models/`、`__pycache__/` 等)、`README.md`、`LICENSE`(MIT)、`requirements.txt` / `requirements-dev.txt`
- [ ] 本地 conda 环境:`conda create -n envproj python=3.11` + 装依赖(国内用清华源;注意 conda ToS 坑见 GOTCHAS)
- [ ] US-2 数据分析页面:数据加载 → 概览/分布/交叉分析/相关性 → 筛选联动(模块开发 + 测试)
- [ ] US-3 离线训练管线:预处理(含未知类别兜底) → 训练 → 评估报告 → AUC 门禁(模块开发 + 测试)
- [ ] US-4 在线预测系统:模型加载 + 点选式表单 + 推理展示(模块开发 + 测试,含 AppTest)
- [ ] Dockerfile:构建期完成离线训练,产物落 `models/`(不提交 Git),运行时只推理
- [ ] 六步④ 本地自检:ruff format/check + pytest --cov(--cov-fail-under=80) + AUC 门禁,全绿
- [ ] 六步⑤ 提交 + push + `gh pr create`,汇报 PR 链接与 CI 状态后停下
- [ ] 六步⑥ 人类 Review + Merge → CD 自动部署 → 汇报落地端口 / `healthz` 结果
- [ ] 会话结束前更新本文件(状态/里程碑/GOTCHAS)

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-08-02 | 数据文件进 Git | 公开教学数据、仅 3.7MB;CI/CD 干净 runner 需要它,避免 `FileNotFoundError` |
| 2026-08-02 | 模型产物不进 Git,由 Dockerfile 构建期训练生成 | 二进制产物不入库;训练 22.5k 行秒级完成,容器自包含 |
| 2026-08-02 | 算法首选 `sklearn.ensemble.HistGradientBoostingClassifier` | 无原生编译依赖,构建快,适合教学与 Docker 场景;如指标不足再换 |
| 2026-08-02 | 健康检查用 Streamlit 内建 `/healthz` 端点 | 无需自写后端;`curl -fsS http://localhost:8888/healthz` 返回 `ok` |
| 2026-08-02 | 端口:容器内固定 8501,主机优先 8888,回退段 8888–8897 | 遵循 05 标准「容器内固定、主机可回退」 |
| 2026-08-02 | 模型质量门禁:验证集 AUC ≥ 0.85 | 经典数据集梯度提升可达 0.90+,0.85 是安全下限 |
| 2026-08-02 | 图表库:matplotlib + seaborn | 轻量、教学主流、无前端运行时;Streamlit 原生支持,渲染快 |
| 2026-08-02 | 镜像名 `banksys-pingu`(小写),容器名 `BankSYS_Pingu` | Docker 镜像 tag 必须小写,容器名可大写;两者解耦 |

---

## 已知坑 (GOTCHAS)

- **conda create 报 ToS 错误**:新版 conda 默认渠道未接受服务条款。解决:`conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main`(r / msys2 同款,共三次)。
- **CI 红 FileNotFoundError 找不到数据**:数据被 .gitignore 排除或未入库,干净 runner 上没有。本项目数据已决策入库(见 ADR),若 CI 仍缺,检查 `.gitignore`。
- **Windows 控制台 GBK 报错**:日志/打印含 `▶` 等特殊符号时报 `UnicodeEncodeError('gbk')`。解决:输出用纯 ASCII,或 `set PYTHONIOENCODING=utf-8`。注意 pytest 会吞输出,必须真跑一次脚本验证。
- **`docker run` 报 `port is already allocated`(exit 125)**:主机端口被占用;按 05 标准自动回退到预留段,`docker rm -f BankSYS_Pingu` 幂等替换自身,不删他人容器。
- **预测遇到训练集未出现的类别**:预处理管线必须含未知类别兜底(如 `handle_unknown='ignore'` / 归入 `unknown`),否则在线预测崩溃。
- **Streamlit 健康检查端点变化**:旧版文档的 `/healthz` 在新版(2026)返回前端 HTML 而非 `ok`;正确端点是 `/_stcore/health`,返回 `ok`。已实测验证并同步修正 deploy.sh / Dockerfile / 00 文档。
- **docker build 报 `invalid tag "BankSYS_Pingu:latest": repository name must be lowercase`**:Docker 镜像 tag 必须全小写,容器名才可大写。CI 的镜像 tag 是 `banksys-pingu:ci`(小写)所以 CI 绿,而 deploy.sh 用了大写 APP 变量导致 CD 红。解决:镜像名 `banksys-pingu`、容器名 `BankSYS_Pingu` 解耦,已修 deploy.sh 并走 fix/1-deploy-image-tag 分支。
- **HTTPS 443 被阻断、git push 失败**:本机直连 `https://github.com` 超时(443 不通),但 **SSH 443 通道正常**。解决:`git remote set-url origin ssh://git@ssh.github.com:443/<账号>/<仓库>.git` 后 push 成功;`gh` 走 HTTPS 建仓/API 不受影响。

---

## 里程碑 (DONE)

- [x] 读取全部 standards(README / 00 / 01 / PROGRESS / 02~06),确认数据结构(train 22.5k 行、test 7.5k 行,21 列 + 目标 `subscribe`)
- [x] 填写 `00-project-context.md` / `01-requirements.md`,初始化本文件;人类确认
- [x] 仓库 `BankSYS_Pingu` 创建并公开(main 引导提交已推送;origin 切 SSH 443)
- [x] Secrets 配置完成(`SSH_PRIVATE_KEY` 曾拼错 `SSH_PRIVATE_KRY`,人类修正)
- [x] 本地环境:uv 安装成功,Python 3.11.15 装入 `.venv`,依赖装齐(清华源)
- [x] US-1 工程骨架:requirements/pyproject/Dockerfile/.dockerignore/.gitattributes/deploy.sh/ci.yml/cd.yml/src 包/app 骨架/测试
- [x] US-1 本地自检:ruff format/check ✅、pytest 6 passed、覆盖率 100%、streamlit + `/_stcore/health` smoke test ✅
- [x] **US-1 工程初始化 + CI/CD 全链路跑通**:PR #2 合并 → CD 首次失败(镜像 tag 大写)→ PR #3 修复 → 部署成功,端口 8890,健康检查通过(2026-08-02)
- [ ] US-2 数据分析交互页面验收通过
- [ ] US-3 离线训练管线验收通过(AUC ≥ 0.85)
- [ ] US-4 在线预测系统验收通过
