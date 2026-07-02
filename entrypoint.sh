#!/bin/bash

VERSION=$(cat /etc/cloudpanel-version 2>/dev/null || echo "unknown")
echo "CloudPanel v${VERSION} starting..."

mkdir -p data logs

# 等待 Redis 就绪
echo "Waiting for Redis..."
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}
while ! nc -z "$REDIS_HOST" "$REDIS_PORT"; do
  sleep 1
done
echo "Redis is ready!"

# 执行数据库迁移
python manage.py migrate

# 启动 supervisor
/usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
