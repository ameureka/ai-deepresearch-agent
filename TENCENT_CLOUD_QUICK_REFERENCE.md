# 腾讯云部署快速参考

## 🚀 一键部署

```bash
# 下载并运行部署脚本
curl -fsSL https://raw.githubusercontent.com/ameureka/ai-deepresearch-agent/main/deploy_tencent.sh | sudo bash
```

## 📋 手动部署（5 步）

### 1. 安装 Docker
```bash
curl -fsSL https://get.docker.com | sh
systemctl start docker && systemctl enable docker
```

### 2. 克隆代码
```bash
cd /opt
git clone https://github.com/ameureka/ai-deepresearch-agent.git
cd ai-deepresearch-agent
```

### 3. 配置环境
```bash
cp .env.example .env
vim .env  # 填入 API Keys
```

### 4. 运行应用
```bash
docker build -t ai-research-assistant .
docker run -d --name ai-app --restart always -p 8000:8000 --env-file .env ai-research-assistant
```

### 5. 配置 Nginx
```bash
apt install -y nginx
# 复制配置（见完整指南）
systemctl restart nginx
```

## 🔧 常用命令

### Docker 操作
```bash
# 查看日志
docker logs -f ai-app

# 重启容器
docker restart ai-app

# 停止容器
docker stop ai-app

# 查看状态
docker ps

# 查看资源使用
docker stats ai-app
```

### 应用更新
```bash
cd /opt/ai-deepresearch-agent
git pull origin main
docker build -t ai-research-assistant .
docker stop ai-app && docker rm ai-app
docker run -d --name ai-app --restart always -p 8000:8000 --env-file .env ai-research-assistant
```

### Nginx 操作
```bash
# 测试配置
nginx -t

# 重启
systemctl restart nginx

# 查看日志
tail -f /var/log/nginx/ai-app-error.log
```

### SSL 配置
```bash
# 安装 Certbot
apt install -y certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d your-domain.com

# 测试续期
certbot renew --dry-run
```

## 🆘 故障排查

### 容器无法启动
```bash
docker logs ai-app
# 检查 .env 文件配置
```

### 502 Bad Gateway
```bash
docker ps  # 确认容器运行
docker logs ai-app  # 查看应用日志
nginx -t  # 测试 Nginx 配置
```

### 内存不足
```bash
free -h  # 查看内存
docker stats  # 查看容器资源
# 考虑减少 workers 或升级服务器
```

## 📊 监控

### 查看资源使用
```bash
# 系统资源
htop

# Docker 资源
docker stats

# 磁盘空间
df -h

# 内存使用
free -h
```

### 查看日志
```bash
# 应用日志
docker logs --tail 100 ai-app

# Nginx 访问日志
tail -f /var/log/nginx/ai-app-access.log

# Nginx 错误日志
tail -f /var/log/nginx/ai-app-error.log
```

## 🔗 重要链接

- **完整指南**: TENCENT_CLOUD_DEPLOYMENT_GUIDE.md
- **设计文档**: TENCENT_CLOUD_DEPLOYMENT_DESIGN.md
- **GitHub**: https://github.com/ameureka/ai-deepresearch-agent
- **腾讯云控制台**: https://console.cloud.tencent.com/

## 💰 成本

```
服务器: ¥32/月 (2核2GB)
域名: ¥55/年 (可选)
SSL: 免费 (Let's Encrypt)
数据库: 免费 (Neon)
```

## ✅ 检查清单

- [ ] 服务器购买
- [ ] SSH 连接成功
- [ ] Docker 安装
- [ ] 代码克隆
- [ ] 环境变量配置
- [ ] 容器运行
- [ ] Nginx 配置
- [ ] SSL 配置（如有域名）
- [ ] 防火墙配置
- [ ] 功能测试通过

---

**需要帮助？** 查看完整指南或提交 GitHub Issue
