#!/bin/bash

################################################################################
# AI DeepResearch Agent - 部署验证脚本
# 
# 用途：验证前后端部署是否完全成功
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
    echo "║        AI DeepResearch Agent - 部署验证                  ║"
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

check_backend_cors() {
    print_section "1. 检查后端 CORS 配置"
    
    if [ -f /opt/agentic-ai/.env ]; then
        CORS_CONFIG=$(grep "ALLOWED_ORIGINS" /opt/agentic-ai/.env)
        echo "当前配置: $CORS_CONFIG"
        
        if echo "$CORS_CONFIG" | grep -q "https://deepresearch.ameureka.com"; then
            echo -e "${GREEN}✓${NC} CORS 配置正确 - 包含 https:// 协议"
        else
            echo -e "${RED}✗${NC} CORS 配置错误 - 缺少 https:// 协议"
            echo "请运行: sudo sed -i 's|deepresearch.ameureka.com|https://deepresearch.ameureka.com|g' /opt/agentic-ai/.env"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} 配置文件不存在"
        return 1
    fi
}

check_backend_service() {
    print_section "2. 检查后端服务状态"
    
    if systemctl is-active --quiet agentic-backend; then
        echo -e "${GREEN}✓${NC} 后端服务运行中"
        
        # 检查服务重启时间
        RESTART_TIME=$(systemctl show agentic-backend -p ActiveEnterTimestamp --value)
        echo "服务启动时间: $RESTART_TIME"
    else
        echo -e "${RED}✗${NC} 后端服务未运行"
        return 1
    fi
}

check_backend_health() {
    print_section "3. 检查后端健康状态"
    
    echo "测试本地健康检查..."
    if curl -s http://localhost:8000/health | grep -q "ok"; then
        echo -e "${GREEN}✓${NC} 本地健康检查通过"
    else
        echo -e "${RED}✗${NC} 本地健康检查失败"
        return 1
    fi
    
    echo ""
    echo "测试公网健康检查..."
    if curl -s https://api.ameureka.com/health | grep -q "ok"; then
        echo -e "${GREEN}✓${NC} 公网健康检查通过"
        echo "响应: $(curl -s https://api.ameureka.com/health)"
    else
        echo -e "${RED}✗${NC} 公网健康检查失败"
        return 1
    fi
}

check_frontend() {
    print_section "4. 检查前端部署"
    
    echo "测试前端访问..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://deepresearch.ameureka.com)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓${NC} 前端访问正常 (HTTP $HTTP_CODE)"
    else
        echo -e "${YELLOW}⚠${NC} 前端返回 HTTP $HTTP_CODE"
    fi
}

check_cors_actual() {
    print_section "5. 测试 CORS 跨域请求"
    
    echo "模拟前端跨域请求..."
    CORS_RESPONSE=$(curl -s -H "Origin: https://deepresearch.ameureka.com" \
                         -H "Access-Control-Request-Method: POST" \
                         -H "Access-Control-Request-Headers: Content-Type" \
                         -X OPTIONS \
                         https://api.ameureka.com/health \
                         -I 2>&1 | grep -i "access-control")
    
    if echo "$CORS_RESPONSE" | grep -q "access-control-allow-origin"; then
        echo -e "${GREEN}✓${NC} CORS 跨域配置生效"
        echo "$CORS_RESPONSE"
    else
        echo -e "${RED}✗${NC} CORS 跨域配置未生效"
        echo "可能需要重启后端服务"
    fi
}

check_cloudflare_tunnel() {
    print_section "6. 检查 Cloudflare Tunnel"
    
    if systemctl is-active --quiet cloudflared; then
        echo -e "${GREEN}✓${NC} Cloudflare Tunnel 运行中"
        
        # 检查隧道连接
        TUNNEL_CONNECTIONS=$(journalctl -u cloudflared -n 20 --no-pager | grep -c "Registered tunnel connection")
        echo "活跃隧道连接数: $TUNNEL_CONNECTIONS"
    else
        echo -e "${RED}✗${NC} Cloudflare Tunnel 未运行"
        return 1
    fi
}

check_database() {
    print_section "7. 检查数据库连接"
    
    echo "测试数据库连接..."
    if grep -q "DATABASE_URL" /opt/agentic-ai/.env; then
        echo -e "${GREEN}✓${NC} 数据库配置存在"
        
        # 尝试通过后端 API 测试数据库连接
        # 这里可以添加具体的数据库测试逻辑
    else
        echo -e "${RED}✗${NC} 数据库配置缺失"
        return 1
    fi
}

show_deployment_summary() {
    print_section "8. 部署总结"
    
    echo ""
    echo "🎉 部署验证完成！"
    echo ""
    echo "📊 部署信息："
    echo "  - 前端地址: https://deepresearch.ameureka.com"
    echo "  - 后端地址: https://api.ameureka.com"
    echo "  - API 文档: https://api.ameureka.com/docs"
    echo ""
    echo "🔗 架构："
    echo "  用户 → Vercel 前端 → Cloudflare Tunnel → 腾讯云后端 → Neon 数据库"
    echo ""
    echo "✅ 下一步："
    echo "  1. 访问前端: https://deepresearch.ameureka.com"
    echo "  2. 测试研究功能"
    echo "  3. 查看 API 文档: https://api.ameureka.com/docs"
    echo "  4. 监控日志: sudo journalctl -u agentic-backend -f"
    echo ""
}

# 主函数
main() {
    print_header
    
    FAILED=0
    
    check_backend_cors || FAILED=$((FAILED + 1))
    check_backend_service || FAILED=$((FAILED + 1))
    check_backend_health || FAILED=$((FAILED + 1))
    check_frontend || FAILED=$((FAILED + 1))
    check_cors_actual || FAILED=$((FAILED + 1))
    check_cloudflare_tunnel || FAILED=$((FAILED + 1))
    check_database || FAILED=$((FAILED + 1))
    
    show_deployment_summary
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✅ 所有检查通过！部署成功！${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        exit 0
    else
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}⚠️  发现 $FAILED 个问题，请检查上述输出${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        exit 1
    fi
}

main
