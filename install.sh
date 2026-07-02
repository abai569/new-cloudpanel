#!/bin/bash
#
# CloudPanel 一键安装脚本
# 支持: Ubuntu/Debian/CentOS/RHEL
# 功能: 自动安装 Docker、Docker Compose、部署 CloudPanel
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
INSTALL_DIR="/opt/cloudpanel"
FRONTEND_PORT=8086
BACKEND_PORT=8111
GITHUB_REPO="Nodewebzsz/cloudpanel"
BRANCH="main"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查 root 权限
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 root 用户运行此脚本"
        exit 1
    fi
}

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        log_error "无法检测操作系统"
        exit 1
    fi
    log_info "检测到操作系统: $OS $VERSION"
}

# 安装 Docker
install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker 已安装: $(docker --version)"
        return
    fi

    log_step "安装 Docker..."

    case $OS in
        ubuntu|debian)
            apt update -y
            apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://get.docker.com | bash -s docker
            ;;
        centos|rhel|rocky|almalinux)
            yum install -y yum-utils
            yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            yum install -y docker-ce docker-ce-cli containerd.io
            systemctl start docker
            systemctl enable docker
            ;;
        *)
            log_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac

    docker --version
    log_info "Docker 安装完成"
}

# 安装 Docker Compose
install_compose() {
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1; then
        if command -v docker-compose &> /dev/null; then
            log_info "Docker Compose 已安装: $(docker-compose --version)"
        else
            log_info "Docker Compose 已安装: $(docker compose version)"
        fi
        COMPOSE_CMD="docker compose"
        if command -v docker-compose &> /dev/null; then
            COMPOSE_CMD="docker-compose"
        fi
        return
    fi

    log_step "安装 Docker Compose..."

    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | sed -E 's/.*"v([^"]+)".*/\1/')
    curl -L "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    COMPOSE_CMD="docker-compose"
    docker-compose --version
    log_info "Docker Compose 安装完成"
}

# 生成随机密钥
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || \
    openssl rand -base64 48
}

# 生成随机密码
generate_password() {
    openssl rand -base64 12 | tr -d "=+/" | cut -c1-16
}

# 创建目录
create_directories() {
    log_step "创建目录: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/data/mysql"
    mkdir -p "$INSTALL_DIR/data/redis"
    mkdir -p "$INSTALL_DIR/logs"
}

# 下载配置文件
download_configs() {
    log_step "下载配置文件..."

    local BASE_URL="https://raw.githubusercontent.com/${GITHUB_REPO}/refs/heads/${BRANCH}"

    curl -fsSL "${BASE_URL}/docker-compose.yml" -o "$INSTALL_DIR/docker-compose.yml" || {
        log_error "下载 docker-compose.yml 失败"
        exit 1
    }

    curl -fsSL "${BASE_URL}/.env.example" -o "$INSTALL_DIR/.env.example" || {
        log_warn "下载 .env.example 失败，将自动生成 .env"
    }

    log_info "配置文件下载完成"
}

# 生成 .env 文件
generate_env() {
    log_step "生成 .env 配置文件..."

    local SECRET_KEY=$(generate_secret_key)
    local MYSQL_PASSWORD=$(generate_password)

    cat > "$INSTALL_DIR/.env" << EOF
# CloudPanel 自动生成的配置文件
# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')

# 调试模式 (0 关闭, 1 开启)
DEBUG=0
DJANGO_SETTINGS_MODULE=panelProject.settings

# MySQL配置
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=panel
MYSQL_USER=root
MYSQL_PASSWORD=${MYSQL_PASSWORD}

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379

# 时区设置
TZ=Asia/Shanghai

# 安全设置
DJANGO_SECRET_KEY=${SECRET_KEY}
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=http://localhost:${FRONTEND_PORT},http://127.0.0.1:${FRONTEND_PORT}

# 端口设置
FRONTENDPORT=${FRONTEND_PORT}
BACKENDPORT=${BACKEND_PORT}
EOF

    log_info ".env 文件已生成"
    echo ""
    log_warn "请妥善保管以下信息:"
    echo -e "  ${YELLOW}MySQL Root 密码:${NC} ${MYSQL_PASSWORD}"
    echo -e "  ${YELLOW}Django SECRET_KEY:${NC} ${SECRET_KEY}"
    echo ""
}

# 交互式配置
interactive_config() {
    echo ""
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  CloudPanel 安装配置${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
    echo -e "端口配置:"
    echo -e "  前端访问端口: ${GREEN}${FRONTEND_PORT}${NC}"
    echo -e "  后端 API 端口: ${GREEN}${BACKEND_PORT}${NC}"
    echo ""
    echo -e "MySQL Root 密码: ${GREEN}${MYSQL_PASSWORD}${NC}"
    echo ""
    read -p "是否继续安装? (Y/n): " confirm
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        log_info "安装已取消"
        exit 0
    fi
}

# 部署 CloudPanel
deploy() {
    cd "$INSTALL_DIR"

    log_step "启动 CloudPanel..."
    $COMPOSE_CMD up -d

    echo ""
    log_info "等待服务启动..."
    sleep 15

    # 检查服务状态
    echo ""
    log_step "服务状态:"
    $COMPOSE_CMD ps
}

# 显示安装信息
show_info() {
    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  CloudPanel 安装完成!${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo -e "访问地址:"
    echo -e "  ${BLUE}前端:${NC} http://<你的服务器IP>:${FRONTEND_PORT}"
    echo -e "  ${BLUE}管理后台:${NC} http://<你的服务器IP>:${BACKEND_PORT}/api/admin"
    echo ""
    echo -e "管理命令:"
    echo -e "  ${BLUE}创建管理员:${NC}"
    echo -e "    cd ${INSTALL_DIR}"
    echo -e "    docker exec -it cloudpanel-api python manage.py createsuperuser"
    echo ""
    echo -e "  ${BLUE}查看日志:${NC}"
    echo -e "    cd ${INSTALL_DIR}"
    echo -e "    $COMPOSE_CMD logs -f api"
    echo ""
    echo -e "  ${BLUE}重启服务:${NC}"
    echo -e "    cd ${INSTALL_DIR}"
    echo -e "    $COMPOSE_CMD restart"
    echo ""
    echo -e "  ${BLUE}更新服务:${NC}"
    echo -e "    cd ${INSTALL_DIR}"
    echo -e "    $COMPOSE_CMD pull && $COMPOSE_CMD up -d"
    echo ""
    echo -e "  ${BLUE}停止服务:${NC}"
    echo -e "    cd ${INSTALL_DIR}"
    echo -e "    $COMPOSE_CMD down"
    echo ""
    echo -e "${YELLOW}提示:${NC} 首次访问请创建管理员账户"
    echo ""
}

# 主函数
main() {
    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  CloudPanel 一键安装脚本${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""

    check_root
    detect_os
    install_docker
    install_compose
    create_directories
    download_configs
    generate_env
    interactive_config
    deploy
    show_info
}

# 帮助
show_help() {
    echo "CloudPanel 一键安装脚本"
    echo ""
    echo "用法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help        显示此帮助信息"
    echo "  -d, --dir DIR     指定安装目录 (默认: /opt/cloudpanel)"
    echo "  -f, --frontend PORT  前端端口 (默认: 8086)"
    echo "  -b, --backend PORT   后端端口 (默认: 8111)"
    echo ""
    echo "示例:"
    echo "  $0                    # 默认安装"
    echo "  $0 -d /my/cloudpanel  # 自定义安装目录"
    echo "  $0 -f 80 -b 443       # 自定义端口"
    echo ""
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        -f|--frontend)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        -b|--backend)
            BACKEND_PORT="$2"
            shift 2
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

main
