# AI DeepResearch Agent - 后端部署状态与配置文档

> 文档生成时间：2025-11-03  
> 服务器：腾讯云 Ubuntu  
> 部署方式：Cloudflare Tunnel + FastAPI

---

## 📊 部署状态总览

### ✅ 服务运行状态

| 服务 | 状态 | 运行时间 | 资源使用 |
|------|------|----------|----------|
| FastAPI 后端 | ✅ 运行中 | 2h 34min+ | 335.2 MB |
| Cloudflare Tunnel | ✅ 运行中 | 2h 20min+ | 14.7 MB |
| 端口 8000 | ✅ 监听中 | - | - |
| 健康检查 | ✅ 正常 | - | - |

### 🌐 访问地址

- **公网 API**: https://api.ameureka.com
- **API 文档**: https://api.ameureka.com/docs
- **健康检查**: https://api.ameureka.com/health
- **本地访问**: http://localhost:8000

### 🖥️ 系统资源

- **磁盘**: 50GB 总容量，已用 7.9GB (17%)
- **内存**: 1.9GB 总容量，已用 859MB
- **CPU**: 正常
- **Swap**: 1.9GB，已用 61MB

---

## 📁 配置文件位置

### 1. 后端环境配置
```bash
/opt/agentic-ai/.env
```

### 2. Cloudflare Tunnel 配置
```bash
/etc/cloudflared/config.yml
# 或
~/.cloudflared/config.yml
```

### 3. Systemd 服务配置
```bash
/etc/systemd/system/agentic-backend.service
/etc/systemd/system/cloudflared.service
```

### 4. 项目目录
```bash
/opt/agentic-ai/
```

### 5. 日志文件
```bash
/opt/agentic-ai/logs/backend.log
/opt/agentic-ai/logs/backend-error.log
```

---

## ⚙️ 当前配置详情

### 环境变量配置 (`/opt/agentic-ai/.env`)

```bash
# ============================================================================
# API Keys
# ============================================================================
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here

# ============================================================================
# Database (Neon PostgreSQL)
# ============================================================================
DATABASE_URL=postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require

# ============================================================================
# Server Configuration
# ============================================================================
HOST=0.0.0.0
PORT=8000
ENV=production
LOG_LEVEL=INFO

# ============================================================================
# CORS Configuration
# ============================================================================
# ⚠️ 需要修复：缺少 https:// 协议前缀
ALLOWED_ORIGINS=deepresearch.ameureka.com,http://localhost:3000

# ✅ 正确配置应该是：
# ALLOWED_ORIGINS=https://deepresearch.ameureka.com,http://localhost:3000

# ============================================================================
# Uvicorn Workers
# ============================================================================
WORKERS=4

# ============================================================================
# Model Configuration
# ============================================================================
PLANNER_MODEL=deepseek:deepseek-reasoner
RESEARCHER_MODEL=deepseek:deepseek-chat
WRITER_MODEL=deepseek:deepseek-chat
EDITOR_MODEL=deepseek:deepseek-chat
FALLBACK_MODEL=openai:gpt-4o-mini

# ============================================================================
# Context Management
# ============================================================================
ENABLE_CHUNKING=true
CHUNKING_THRESHOLD=0.8
MAX_CHUNK_SIZE=6000
CHUNK_OVERLAP=200
```

### Cloudflare Tunnel 配置

```yaml
tunnel: d92ad662-b564-41b8-91ac-26f785756a70
credentials-file: /root/.cloudflared/d92ad662-b564-41b8-91ac-26f785756a70.json

ingress:
  - hostname: api.ameureka.com
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true
  - service: http_status:404
```

**隧道信息：**
- 隧道 ID: `d92ad662-b564-41b8-91ac-26f785756a70`
- 域名: `api.ameureka.com`
- 目标服务: `http://localhost:8000`
- 连接节点: 新加坡 (sin11, sin17, sin02, sin20)
- 活跃连接: 4 个

---

## 🔧 配置问题与修复

### ❌ 发现的问题

**CORS 配置错误**
```bash
# 当前配置（错误）
ALLOWED_ORIGINS=deepresearch.ameureka.com,http://localhost:3000
```

**问题说明：**
- 缺少 `https://` 协议前缀
- 会导致前端跨域请求被阻止
- 浏览器会报 CORS 错误

### ✅ 修复步骤

#### 方法 1：手动修复

```bash
# 1. SSH 登录到服务器
ssh root@your-server-ip

# 2. 编辑配置文件
sudo nano /opt/agentic-ai/.env

# 3. 找到 ALLOWED_ORIGINS 这一行，修改为：
ALLOWED_ORIGINS=https://deepresearch.ameureka.com,http://localhost:3000

# 4. 保存并退出
# 按 Ctrl+X，然后按 Y，然后按 Enter

# 5. 重启后端服务
sudo systemctl restart agentic-backend

# 6. 验证服务状态
sudo systemctl status agentic-backend

# 7. 测试健康检查
curl http://localhost:8000/health
```

#### 方法 2：使用 sed 命令快速修复

```bash
# 一键修复 CORS 配置
sudo sed -i 's|ALLOWED_ORIGINS=deepresearch.ameureka.com|ALLOWED_ORIGINS=https://deepresearch.ameureka.com|g' /opt/agentic-ai/.env

# 重启服务
sudo systemctl restart agentic-backend

# 验证修改
grep ALLOWED_ORIGINS /opt/agentic-ai/.env
```

---

## 🛠️ 常用运维命令

### 服务管理

```bash
# 查看后端服务状态
sudo systemctl status agentic-backend

# 启动后端服务
sudo systemctl start agentic-backend

# 停止后端服务
sudo systemctl stop agentic-backend

# 重启后端服务
sudo systemctl restart agentic-backend

# 查看 Cloudflare Tunnel 状态
sudo systemctl status cloudflared

# 重启 Cloudflare Tunnel
sudo systemctl restart cloudflared
```

### 日志查看

```bash
# 实时查看后端日志
sudo journalctl -u agentic-backend -f

# 查看最近 100 行后端日志
sudo journalctl -u agentic-backend -n 100

# 实时查看 Cloudflare Tunnel 日志
sudo journalctl -u cloudflared -f

# 查看应用日志文件
tail -f /opt/agentic-ai/logs/backend.log

# 查看错误日志
tail -f /opt/agentic-ai/logs/backend-error.log
```

### 健康检查

```bash
# 本地健康检查
curl http://localhost:8000/health

# 公网健康检查
curl https://api.ameureka.com/health

# 查看 API 文档
curl http://localhost:8000/docs

# 测试端口监听
netstat -tuln | grep 8000
# 或
ss -tuln | grep 8000
```

### Cloudflare Tunnel 管理

```bash
# 列出所有隧道
cloudflared tunnel list

# 查看隧道详情
cloudflared tunnel info d92ad662-b564-41b8-91ac-26f785756a70

# 查看隧道路由
cloudflared tunnel route dns

# 测试隧道连接
cloudflared tunnel run d92ad662-b564-41b8-91ac-26f785756a70
```

### 配置文件管理

```bash
# 查看环境配置
cat /opt/agentic-ai/.env

# 编辑环境配置
sudo nano /opt/agentic-ai/.env

# 查看 Cloudflare 配置
cat /etc/cloudflared/config.yml

# 编辑 Cloudflare 配置
sudo nano /etc/cloudflared/config.yml

# 查看后端服务配置
cat /etc/systemd/system/agentic-backend.service

# 重新加载 systemd 配置（修改服务文件后）
sudo systemctl daemon-reload
```

### 系统监控

```bash
# 查看系统资源使用
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看进程
ps aux | grep uvicorn
ps aux | grep cloudflared

# 查看网络连接
netstat -tuln
```

---

## 🔍 快速诊断脚本

使用我们提供的状态检查脚本：

```bash
# 在服务器上运行
sudo bash /opt/agentic-ai/scripts/check-backend-status.sh

# 或从本地上传并运行
scp scripts/check-backend-status.sh root@your-server-ip:/tmp/
ssh root@your-server-ip "sudo bash /tmp/check-backend-status.sh"
```

---

## 🏗️ 完整部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         Vercel 前端 (Next.js)                               │
│         https://deepresearch.ameureka.com                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         Cloudflare Tunnel                                   │
│         https://api.ameureka.com                            │
│         隧道 ID: d92ad662-b564-41b8-91ac-26f785756a70       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         腾讯云服务器 (Ubuntu)                                │
│         内网 IP: 10.3.4.9                                   │
│         ┌─────────────────────────────────────────┐         │
│         │  FastAPI 后端 (Uvicorn)                 │         │
│         │  http://localhost:8000                  │         │
│         │  Workers: 4                             │         │
│         └─────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         Neon PostgreSQL 数据库                              │
│         ep-divine-forest-ae1b1kxu-pooler                    │
│         us-east-2.aws.neon.tech                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 配置检查清单

### ✅ 已正确配置

- [x] DeepSeek API Key
- [x] OpenAI API Key
- [x] Tavily API Key
- [x] Neon PostgreSQL 数据库连接
- [x] 服务器监听配置 (0.0.0.0:8000)
- [x] 生产环境模式
- [x] Uvicorn Workers (4个)
- [x] 模型配置 (DeepSeek + OpenAI 降级)
- [x] 上下文分块管理
- [x] Cloudflare Tunnel 配置
- [x] Systemd 服务自动启动

### ⚠️ 需要修复

- [ ] **CORS 配置** - 需要添加 `https://` 协议前缀

---

## 🚀 下一步操作建议

### 1. 修复 CORS 配置（必需）

```bash
# 修复 CORS
sudo sed -i 's|ALLOWED_ORIGINS=deepresearch.ameureka.com|ALLOWED_ORIGINS=https://deepresearch.ameureka.com|g' /opt/agentic-ai/.env

# 重启服务
sudo systemctl restart agentic-backend
```

### 2. 更新 Vercel 前端环境变量

在 Vercel 项目设置中添加：

```bash
NEXT_PUBLIC_API_URL=https://api.ameureka.com
```

### 3. 测试前后端连接

```bash
# 测试后端健康检查
curl https://api.ameureka.com/health

# 访问前端并测试功能
# https://deepresearch.ameureka.com
```

### 4. 监控服务运行

```bash
# 实时监控后端日志
sudo journalctl -u agentic-backend -f

# 实时监控隧道日志
sudo journalctl -u cloudflared -f
```

### 5. 配置监控告警（可选）

考虑配置：
- Uptime 监控（如 UptimeRobot）
- 日志聚合（如 Sentry）
- 性能监控（如 New Relic）

---

## 📞 故障排查

### 问题 1：前端无法连接后端

**症状：**
- 浏览器控制台显示 CORS 错误
- API 请求失败

**解决方案：**
1. 检查 CORS 配置是否包含 `https://`
2. 确认 Vercel 域名在 ALLOWED_ORIGINS 中
3. 重启后端服务

### 问题 2：后端服务无法启动

**症状：**
- `systemctl status agentic-backend` 显示 failed

**解决方案：**
```bash
# 查看详细错误日志
sudo journalctl -u agentic-backend -n 50

# 检查端口是否被占用
sudo netstat -tuln | grep 8000

# 检查环境变量是否正确
cat /opt/agentic-ai/.env

# 手动启动测试
cd /opt/agentic-ai
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 问题 3：Cloudflare Tunnel 连接失败

**症状：**
- 无法通过 api.ameureka.com 访问

**解决方案：**
```bash
# 检查隧道状态
sudo systemctl status cloudflared

# 查看隧道日志
sudo journalctl -u cloudflared -n 50

# 测试隧道连接
cloudflared tunnel info d92ad662-b564-41b8-91ac-26f785756a70

# 重启隧道
sudo systemctl restart cloudflared
```

### 问题 4：数据库连接失败

**症状：**
- 后端日志显示数据库连接错误

**解决方案：**
```bash
# 测试数据库连接
psql "postgresql://neondb_owner:npg_mFA8vx4NXoSj@ep-divine-forest-ae1b1kxu-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"

# 检查网络连接
ping ep-divine-forest-ae1b1kxu-pooler.c-2.us-east-2.aws.neon.tech

# 检查防火墙规则
sudo ufw status
```

---

## 📚 相关文档

- [腾讯云部署指南](./TENCENT_CLOUD_DEPLOYMENT.md)
- [Cloudflare Tunnel 设置](./CLOUDFLARE_TUNNEL_SETUP.md)
- [Vercel 部署指南](./VERCEL_DEPLOYMENT_GUIDE.md)
- [环境配置检查](./ENVIRONMENT_CONFIG_CHECK.md)

---

## 📧 联系信息

- GitHub: https://github.com/ameureka/ai-deepresearch-agent
- 项目目录: /opt/agentic-ai

---

**文档版本**: v1.0.0  
**最后更新**: 2025-11-03  
**维护者**: AI DeepResearch Team
