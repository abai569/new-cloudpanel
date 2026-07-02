#!/bin/bash

VERSION=$(cat /etc/cloudpanel-version 2>/dev/null || echo "unknown")
echo "CloudPanel v${VERSION} starting..."

# 等待 Redis 就绪
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is ready!"

# 执行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py init_user

# 启动 supervisor
/usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf