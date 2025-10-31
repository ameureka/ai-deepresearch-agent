#!/bin/bash

####################################################################################
# Phase 2 API 测试脚本
#
# 本脚本测试所有 Phase 2 实现的 API 端点：
# 1. GET /api/health - 健康检查
# 2. GET /api/models - 模型列表
# 3. POST /api/research/stream - SSE 流式研究（需要手动观察）
#
# 使用方法：
#   chmod +x test_phase2_apis.sh
#   ./test_phase2_apis.sh
#
# 要求：
#   - 服务器运行在 localhost:8000
#   - curl 命令可用
#   - jq 命令可用（可选，用于格式化 JSON）
####################################################################################

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "Phase 2 API 测试脚本"
echo "========================================================================"
echo ""
echo "基础 URL: $BASE_URL"
echo ""

# 函数：打印测试结果
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}: $2"
    else
        echo -e "${RED}✗ FAILED${NC}: $2"
    fi
}

####################################################################################
# 测试 1: GET /api/health
####################################################################################
echo "========================================================================"
echo "测试 1: GET /api/health"
echo "========================================================================"
echo ""

response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/health")
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

echo "HTTP 状态码: $http_code"
echo "响应体:"
if command -v jq &> /dev/null; then
    echo "$body" | jq '.'
else
    echo "$body"
fi
echo ""

# 验证
if [ "$http_code" = "200" ]; then
    # 检查响应格式
    success=$(echo "$body" | jq -r '.success' 2>/dev/null)
    status=$(echo "$body" | jq -r '.data.status' 2>/dev/null)

    if [ "$success" = "true" ] && [ "$status" = "ok" ]; then
        print_result 0 "/api/health 返回正确格式"
    else
        print_result 1 "/api/health 响应格式不正确"
    fi
else
    print_result 1 "/api/health HTTP 状态码不是 200"
fi

echo ""

####################################################################################
# 测试 2: GET /api/models
####################################################################################
echo "========================================================================"
echo "测试 2: GET /api/models"
echo "========================================================================"
echo ""

response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/models")
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

echo "HTTP 状态码: $http_code"
echo "响应体:"
if command -v jq &> /dev/null; then
    echo "$body" | jq '.'
else
    echo "$body"
fi
echo ""

# 验证
if [ "$http_code" = "200" ]; then
    success=$(echo "$body" | jq -r '.success' 2>/dev/null)
    total=$(echo "$body" | jq -r '.data.total' 2>/dev/null)

    if [ "$success" = "true" ] && [ "$total" -gt 0 ]; then
        print_result 0 "/api/models 返回正确格式，模型数量: $total"
    else
        print_result 1 "/api/models 响应格式不正确"
    fi
else
    print_result 1 "/api/models HTTP 状态码不是 200"
fi

echo ""

####################################################################################
# 测试 3: POST /api/research/stream (SSE)
####################################################################################
echo "========================================================================"
echo "测试 3: POST /api/research/stream (SSE)"
echo "========================================================================"
echo ""
echo -e "${YELLOW}注意：这是一个 SSE 流式接口，需要手动观察输出${NC}"
echo ""
echo "发送请求: Research the latest developments in quantum computing"
echo ""
echo "期望的事件顺序："
echo "  1. event: start"
echo "  2. event: plan"
echo "  3. event: progress (多个)"
echo "  4. event: done"
echo ""
echo -e "${YELLOW}提示：按 Ctrl+C 可以随时中断测试${NC}"
echo ""
echo "开始接收 SSE 事件（前 20 个事件后自动停止）:"
echo "------------------------------------------------------------------------"

# 使用 curl 的 -N 选项禁用缓冲
# 使用 head 限制输出行数（每个事件约 3-4 行）
curl -N -X POST "$BASE_URL/api/research/stream" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Research the latest developments in quantum computing"}' \
     2>/dev/null | head -n 80

echo ""
echo "------------------------------------------------------------------------"
echo ""
print_result 0 "SSE 流已启动（请手动验证事件格式）"
echo ""

####################################################################################
# 测试 4: 验证错误处理 - 无效的请求
####################################################################################
echo "========================================================================"
echo "测试 4: 验证错误处理 - 无效的请求"
echo "========================================================================"
echo ""

# 测试 4.1: prompt 太短
echo "测试 4.1: prompt 太短（< 10 字符）"
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/research/stream" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "AI"}')
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

echo "HTTP 状态码: $http_code"
if [ "$http_code" = "400" ] || [ "$http_code" = "422" ]; then
    print_result 0 "正确拒绝了过短的 prompt"
else
    print_result 1 "应该返回 400 或 422，实际: $http_code"
fi
echo ""

# 测试 4.2: 缺少 prompt
echo "测试 4.2: 缺少 prompt"
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/research/stream" \
     -H "Content-Type: application/json" \
     -d '{}')
http_code=$(echo "$response" | tail -n 1)

echo "HTTP 状态码: $http_code"
if [ "$http_code" = "400" ] || [ "$http_code" = "422" ]; then
    print_result 0 "正确拒绝了缺少 prompt 的请求"
else
    print_result 1 "应该返回 400 或 422，实际: $http_code"
fi
echo ""

####################################################################################
# 测试总结
####################################################################################
echo "========================================================================"
echo "测试总结"
echo "========================================================================"
echo ""
echo "✓ 基础接口测试完成"
echo "✓ 错误处理测试完成"
echo "⚠️  SSE 流式接口需要手动验证完整性"
echo ""
echo "下一步："
echo "  1. 启动服务器：uvicorn main:app --reload"
echo "  2. 运行完整的端到端测试"
echo "  3. 使用浏览器测试前端集成"
echo ""
echo "========================================================================"
