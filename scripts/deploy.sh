#!/usr/bin/env bash
# CD 部署脚本:在服务器上执行,幂等可重跑(见 05 标准第 4 节)。
set -e

cd "$(dirname "$0")/.."

APP="BankSYS_Pingu"   # 容器名(可大写)
IMAGE="banksys-pingu" # 镜像名(Docker tag 必须小写,大写会报 invalid tag)
PORT=8888          # 主机端口(优先)
PORT_MAX=8897      # 预留回退区间上界
PORT_IN=8501       # 容器内固定端口(Streamlit 默认)
HEALTHCHECK="_stcore/health"
PIP_INDEX_URL="${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"

echo ">> 构建镜像(镜像源: $PIP_INDEX_URL)"
docker build --build-arg PIP_INDEX_URL="$PIP_INDEX_URL" -t "${IMAGE}:latest" .

# 主机端口优先 8888,被占用则在预留区间自动找空闲端口
port_in_use() {
  ss -ltnH 2>/dev/null | grep -q ":$1 " && return 0
  docker ps --format "{{.Ports}}" 2>/dev/null | grep -q ":$1->" && return 0
  return 1
}
HOST_PORT=""
for p in $(seq "$PORT" "$PORT_MAX"); do
  if ! port_in_use "$p"; then HOST_PORT="$p"; break; fi
done
[ -z "$HOST_PORT" ] && { echo ">> 预留端口区间 $PORT-$PORT_MAX 已全部占用,部署中止"; exit 1; }
echo ">> 部署到主机端口 $HOST_PORT"

# 一步停删自身旧容器,保证幂等可重跑
docker rm -f "${APP}" 2>/dev/null || true
docker run -d --name "${APP}" --restart unless-stopped \
  -p "${HOST_PORT}:${PORT_IN}" "${IMAGE}:latest"

sleep 3
curl -fsS "http://localhost:${HOST_PORT}/${HEALTHCHECK}"
echo ""
echo ">> 部署成功: http://$(hostname -I 2>/dev/null | awk '{print $1}'):${HOST_PORT}"
