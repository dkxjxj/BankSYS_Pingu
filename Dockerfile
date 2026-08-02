# syntax=docker/dockerfile:1
FROM python:3.11-slim

# 镜像源可配置(国内服务器可用清华源构建,见 05 标准第 4 节)
ARG PIP_INDEX_URL=https://pypi.org/simple
ENV PIP_INDEX_URL=${PIP_INDEX_URL} \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# 依赖层(利用 Docker 缓存,只装生产运行依赖)
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

# 代码与数据(数据进 Git,见 00 文档 ADR)
COPY src/ ./src/
COPY app/ ./app/
COPY data/ ./data/

# 构建期离线训练:产出模型产物与指标报告(不进 Git,AUC 门禁不达标构建失败)
RUN python -m bank_sys.training --data data/train.csv --output-dir /app/models && ls -la /app/models

EXPOSE 8501

# Streamlit 内建健康检查端点 /_stcore/health(注意:/healthz 在新版返回 HTML,不可用)
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=3)"]

CMD ["streamlit", "run", "app/app.py"]
