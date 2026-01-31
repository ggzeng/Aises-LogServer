#!/bin/bash
# Log Server 管理脚本
# 用于后台启动、停止、重启和查看日志

set -e

# 配置变量
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
LOGS_DIR="logs"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印帮助信息
show_help() {
    echo "Log Server 管理脚本"
    echo ""
    echo "用法: $0 <command>"
    echo ""
    echo "命令:"
    echo "  start    后台启动服务器（日志保存到 logs/ 目录）"
    echo "  stop     停止后台运行的服务器"
    echo "  restart  重启服务器"
    echo "  logs     查看最新的日志文件（实时跟踪）"
    echo "  status   查看服务器运行状态"
    echo "  help     显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  HOST    服务器监听地址（默认: 0.0.0.0）"
    echo "  PORT    服务器监听端口（默认: 8000）"
    echo ""
    echo "示例:"
    echo "  $0 start          # 启动服务器"
    echo "  $0 logs           # 查看日志"
    echo "  HOST=127.0.0.1 $0 start  # 在本地启动"
}

# 检查服务器是否运行
is_running() {
    # 使用 ps + grep 替代 pgrep，更加通用
    ps aux 2>/dev/null | grep -v grep | grep "uvicorn main:app" > /dev/null 2>&1
}

# 获取服务器进程 PID 列表
get_pids() {
    # 使用 ps + grep 替代 pgrep，更加通用
    ps aux 2>/dev/null | grep -v grep | grep "uvicorn main:app" | awk '{print $2}'
}

# 启动服务器
start_server() {
    echo -e "${GREEN}后台启动服务器...${NC}"

    if is_running; then
        echo -e "${YELLOW}服务器已在运行中${NC}"
        echo -e "${YELLOW}使用 '$0 restart' 重启服务器${NC}"
        return 1
    fi

    # 创建日志目录
    mkdir -p "$LOGS_DIR"

    # 生成日志文件名
    LOG_FILE="$LOGS_DIR/server-$(date +%Y%m%d-%H%M%S).log"

    # 启动服务器
    nohup uvicorn main:app --host "$HOST" --port "$PORT" > "$LOG_FILE" 2>&1 &
    PID=$!

    # 等待一下确保启动成功
    sleep 1

    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}服务器已在后台启动，PID: $PID${NC}"
        echo -e "${GREEN}日志文件: $LOG_FILE${NC}"
        echo -e "${YELLOW}使用 '$0 stop' 停止服务器${NC}"
        echo -e "${YELLOW}使用 '$0 logs' 查看日志${NC}"
    else
        echo -e "${RED}服务器启动失败，请检查日志: $LOG_FILE${NC}"
        return 1
    fi
}

# 停止服务器
stop_server() {
    echo -e "${YELLOW}停止服务器...${NC}"

    if ! is_running; then
        echo -e "${YELLOW}未找到运行中的服务器${NC}"
        return 0
    fi

    # 查找并终止进程
    PIDS=$(get_pids)
    if [ -n "$PIDS" ]; then
        echo "$PIDS" | xargs kill 2>/dev/null || true
        sleep 1

        # 检查是否还在运行
        if is_running; then
            echo -e "${YELLOW}强制终止服务器...${NC}"
            get_pids | xargs kill -9 2>/dev/null || true
        fi

        echo -e "${GREEN}服务器已停止${NC}"
    else
        echo -e "${YELLOW}未找到运行中的服务器${NC}"
    fi
}

# 重启服务器
restart_server() {
    echo -e "${YELLOW}重启服务器...${NC}"
    stop_server
    sleep 1
    start_server
}

# 查看日志
view_logs() {
    if [ ! -d "$LOGS_DIR" ]; then
        echo -e "${YELLOW}日志目录不存在: $LOGS_DIR${NC}"
        return 1
    fi

    # 查找最新的日志文件
    LATEST_LOG=$(ls -t "$LOGS_DIR"/*.log 2>/dev/null | head -1)

    if [ -z "$LATEST_LOG" ]; then
        echo -e "${YELLOW}未找到日志文件${NC}"
        return 1
    fi

    echo -e "${GREEN}最新日志文件: $LATEST_LOG${NC}"
    echo ""
    echo -e "${GREEN}日志内容（实时跟踪，按 Ctrl+C 退出）:${NC}"
    echo ""
    tail -f "$LATEST_LOG"
}

# 查看状态
show_status() {
    echo -e "${GREEN}服务器状态:${NC}"
    echo ""

    if is_running; then
        echo -e "${GREEN}● 服务器运行中${NC}"
        PIDS=$(get_pids)
        echo "  PID(s): $PIDS"
        echo "  地址: http://$HOST:$PORT"

        # 显示最新的日志文件
        if [ -d "$LOGS_DIR" ]; then
            LATEST_LOG=$(ls -t "$LOGS_DIR"/*.log 2>/dev/null | head -1)
            if [ -n "$LATEST_LOG" ]; then
                echo "  日志: $LATEST_LOG"
            fi
        fi
    else
        echo -e "${RED}○ 服务器未运行${NC}"
    fi
}

# 主逻辑
case "${1:-}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    logs)
        view_logs
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}错误: 未知命令 '${1:-}'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
