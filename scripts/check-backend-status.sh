#!/bin/bash

################################################################################
# AI DeepResearch Agent - 后端状态检查脚本
# 
# 用途：检查腾讯云服务器上的后端部署状态
# 版本：v1.0.0
################################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                                                          ║"
    echo "║        AI DeepResearch Agent - 后端状态检查              ║"
    echo "║                                                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
}

print_section() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

check_service_status() {
    print_section "1. 后端服务状态"
    
    if systemctl is-active --quiet agentic-backend; then
        echo -e "${GREEN}✓${NC} 后端服务: ${GREEN}运行中${NC}"
        echo ""
        systemctl status agentic-backend --no-pager | head -15
    else
        echo -e "${RED}✗${NC} 后端服务: ${RED}未运行${NC}"
        echo ""
        echo "尝试启动服务: sudo systemctl start agentic-backend"
    fi
}

check_cloudflared_status() {
    print_section "2. Cloudflare Tunnel 状态"
    
    if systemctl is-active --quiet cloudflared; then
        echo -e "${GREEN}✓${NC} Cloudflare Tunnel: ${GREEN}运行中${NC}"
        echo ""
        systemctl status cloudflared --no-pager | head -15
    else
        echo -e "${RED}✗${NC} Cloudflare Tunnel: ${RED}未运行${NC}"
        echo ""
        echo "尝试启动服务: sudo systemctl start cloudflared"
    fi
}

check_ports() {
    print_section "3. 端口监听状态"
    
    echo "检查端口 8000 (FastAPI):"
    if netstat -tuln 2>/dev/null | grep -q ":8000 "; then
        echo -e "${GREEN}✓${NC} 端口 8000: ${GREEN}正在监听${NC}"
        netstat -tuln | grep ":8000 "
    elif ss -tuln 2>/dev/null | grep -q ":8000 "; then
        echo -e "${GREEN}✓${NC} 端口 8000: ${GREEN}正在监听${NC}"
        ss -tuln | grep ":8000 "
    else
        echo -e "${RED}✗${NC} 端口 8000: ${RED}未监听${NC}"
    fi
}

check_health() {
    print_section "4. 健康检查"
    
    echo "本地健康检查 (http://localhost:8000/health):"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} 本地访问: ${GREEN}正常${NC}"
        echo ""
        curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health
    else
        echo -e "${RED}✗${NC} 本地访问: ${RED}失败${NC}"
    fi
}

check_logs() {
    print_section "5. 最近日志 (最后 20 行)"
    
    echo -e "${YELLOW}后端服务日志:${NC}"
    journalctl -u agentic-backend -n 20 --no-pager
    
    echo ""
    echo -e "${YELLOW}Cloudflare Tunnel 日志:${NC}"
    journalctl -u cloudflared -n 20 --no-pager 2>/dev/null || echo "Cloudflare Tunnel 未安装或未运行"
}

check_env() {
    print_section "6. 环境配置"
    
    if [ -f /opt/agentic-ai/.env ]; then
        echo -e "${GREEN}✓${NC} 环境文件: ${GREEN}存在${NC}"
        echo ""
        echo "配置项 (隐藏敏感信息):"
        grep -v "^#" /opt/agentic-ai/.env | grep -v "^$" | sed 's/=.*/=***/' | head -20
    else
        echo -e "${RED}✗${NC} 环境文件: ${RED}不存在${NC}"
    fi
}

check_disk_space() {
    print_section "7. 磁盘空间"
    
    df -h /opt/agentic-ai 2>/dev/null || df -h /
}

check_memory() {
    print_section "8. 内存使用"
    
    free -h
}

check_cloudflare_config() {
    print_section "9. Cloudflare Tunnel 配置"
    
    if [ -f ~/.cloudflared/config.yml ]; then
        echo -e "${GREEN}✓${NC} Cloudflare 配置: ${GREEN}存在${NC}"
        echo ""
        cat ~/.cloudflared/config.yml
    else
        echo -e "${RED}✗${NC} Cloudflare 配置: ${RED}不存在${NC}"
    fi
}

show_useful_commands() {
    print_section "10. 常用命令"
    
    echo "服务管理:"
    echo "  sudo systemctl status agentic-backend    # 查看后端状态"
    echo "  sudo systemctl restart agentic-backend   # 重启后端"
    echo "  sudo systemctl stop agentic-backend      # 停止后端"
    echo "  sudo systemctl start agentic-backend     # 启动后端"
    echo ""
    echo "日志查看:"
    echo "  sudo journalctl -u agentic-backend -f    # 实时查看后端日志"
    echo "  sudo journalctl -u cloudflared -f        # 实时查看隧道日志"
    echo "  tail -f /opt/agentic-ai/logs/backend.log # 查看应用日志"
    echo ""
    echo "健康检查:"
    echo "  curl http://localhost:8000/health        # 本地健康检查"
    echo "  curl http://localhost:8000/docs          # API 文档"
    echo ""
    echo "Cloudflare Tunnel:"
    echo "  cloudflared tunnel list                  # 列出所有隧道"
    echo "  cloudflared tunnel info <tunnel-name>    # 查看隧道详情"
}

# 主函数
main() {
    print_header
    
    # 检查是否在服务器上
    if [ ! -d "/opt/agentic-ai" ]; then
        echo -e "${RED}错误:${NC} 未找到项目目录 /opt/agentic-ai"
        echo "此脚本需要在部署了后端的服务器上运行"
        exit 1
    fi
    
    check_service_status
    check_cloudflared_status
    check_ports
    check_health
    check_logs
    check_env
    check_disk_space
    check_memory
    check_cloudflare_config
    show_useful_commands
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}检查完成！${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

main
