# CloudPanel

[![Docker Image CI/CD](https://github.com/abai569/new-cloudpanel/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/abai569/new-cloudpanel/actions/workflows/docker-publish.yml)

CloudPanel 是一个强大的多云服务管理平台，支持管理和监控多个主流云服务提供商的资源。通过统一的界面，轻松管理 AWS、Azure、DigitalOcean 和 Linode 等云服务资源。

## 快速开始

### 一键安装（推荐）

只需一行命令，脚本将自动完成 Docker 安装、环境配置、服务启动，并自动创建默认管理员账号。

```bash
bash <(curl -L https://raw.githubusercontent.com/abai569/new-cloudpanel/refs/heads/main/install.sh)
```

**安装完成后：**
*   访问地址: `http://<你的服务器IP>:8086`
*   默认账号: `admin`
*   默认密码: `admin123`

**更多命令：**

一键升级
```bash
bash <(curl -L https://raw.githubusercontent.com/abai569/new-cloudpanel/refs/heads/main/install.sh) update
```
一键卸载
```bash
bash <(curl -L https://raw.githubusercontent.com/abai569/new-cloudpanel/refs/heads/main/install.sh) uninstall
```

### 手动部署

...（保留后续内容）

镜像推送到 GitHub Container Registry (ghcr.io)。

```bash
docker pull ghcr.io/abai569/new-cloudpanel:latest
```

## 功能特点

- 多云服务提供商支持（AWS、Azure、DigitalOcean、Linode）
- 统一的资源管理界面
- 用户权限管理系统
- 容器化部署支持
- 异步任务处理
- RESTful API 接口

## 系统要求

- Docker 19.03+ (支持多架构构建)
- Docker Compose

## 前端页面展示
![页面截图](./web/img/image.jpg)


## 访问前端平台

在浏览器中访问：`http://your-server-ip:8086`

### 管理后台

管理员可以通过以下地址访问管理后台：`http://your-server-ip:8111/api/admin`

管理后台功能包括：
- 用户管理：创建、编辑、删除用户
- 权限管理：分配和管理用户权限
- 云服务管理：管理各云服务提供商的配置
- 系统设置：管理系统全局配置

> 注意：请确保使用管理员账户登录管理后台，普通用户无法访问此页面。

## 多架构部署注意事项

1. **自动架构检测**：
   Docker 会自动检测宿主机架构（AMD64 或 ARM64）并拉取对应镜像，无需手动配置。

2. **性能考虑**：
   - ARM64 架构下某些依赖包可能需要额外的编译时间
   - 适当设置容器资源限制

3. **数据迁移**：
   - 不同架构间的数据文件不能直接迁移
   - 需要通过导出/导入方式迁移数据

4. **健康检查**：
   ```bash
   docker-compose ps
   docker-compose logs
   ```

## 开发说明

### 项目结构

```
.
├── apps/           # 主应用目录
│   ├── aws/       # AWS 服务模块
│   ├── azure/     # Azure 服务模块
│   ├── do/        # DigitalOcean 模块
│   ├── linode/    # Linode 服务模块
│   └── users/     # 用户管理模块
├── libs/          # 公共库
├── config/        # 配置文件
── logs/         # 日志目录
└── panelProject/ # 项目核心目录
```

### 技术栈

- 后端框架：Django 4.2
- 数据库：MySQL 9
- 缓存：Redis
- 任务队列：Celery
- WSGI 服务器：Gunicorn
- 容器化：Docker

## 环境变量配置

项目使用环境变量来管理敏感配置信息，主要包括：

- AWS 配置
  - AWS_ACCESS_KEY_ID：AWS 访问密钥 ID
  - AWS_SECRET_ACCESS_KEY：AWS 密钥
  - AWS_ACCOUNT_EMAIL：AWS 账户邮箱
  - AWS_ACCOUNT_NAME：AWS 账户名称
- 数据库配置
  - MYSQL_HOST/PORT/DATABASE/USER/PASSWORD
- Redis 配置
  - REDIS_HOST/PORT
- Django 配置
  - DJANGO_SETTINGS_MODULE
  - DJANGO_SECRET_KEY
  - ALLOWED_HOSTS
  - CORS_ALLOWED_ORIGINS

## 注意事项

1. 支持 x86_64 和 ARM64 架构的 Docker 部署（Docker 自动检测）
2. 如遇到问题，请在 Issues 中反馈
3. 请确保妥善保管环境变量文件，**不要将其提交到版本控制系统**
4. **生产环境部署前**，请务必：
   - 设置 `DEBUG=0`
   - 生成强 `DJANGO_SECRET_KEY`
   - 设置 `MYSQL_PASSWORD` 为强密码
   - 配置 `ALLOWED_HOSTS` 和 `CORS_ALLOWED_ORIGINS` 为实际域名

## 贡献指南

1. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
2. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
3. 推送到分支并创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 项目主页：[https://github.com/abai569/new-cloudpanel]
- 问题反馈：请使用 GitHub Issues

## 致谢

本项目基于 [cdntip/cloudpanel](https://github.com/cdntip/cloudpanel)
