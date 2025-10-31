# 腾讯云部署完整指南

**项目**: AI Research Assistant  
**平台**: 腾讯云轻量应用服务器  
**部署方式**: Docker + Nginx  
**预计时间**: 2-3 小时（首次）

---

## 📋 前置准备

### 1. 需要的账号和资源

- [ ] 腾讯云账号（已实名认证）
- [ ] 信用卡或支付宝（用于购买服务器）
- [ ] 域名（可选，推荐）
- [ ] SSH 客户端（Terminal/PuTTY）

### 2. 需要的信息

从你的 `.env` 文件准备：
- DATABASE_URL
- OPENAI_API_KEY
- DEEPSEEK_API_KEY
- TAVILY_API_KEY

---

## 🚀 第一步：购买腾讯云服务器

### 1.1 登录腾讯云控制台

访问：https://cloud.tencent.com/

### 1.2 选择轻量应用服务器

1. 进入产品页面：https://cloud.tencent.com/product/lighthouse
2. 点击"立即选购"

### 1.3 配置选择

**推荐配置**:
```
地域: 
  - 国内用户: 广州/上海/北京
  - 海外用户: 香港/新加坡

镜像:
  - 应用镜像 → Docker CE

套餐:
  - 2核 2GB 3Mbps
  - 50GB SSD
  - 价格: ¥32/月

购买时长:
  - 建议: 3个月（测试）或 1年（优惠）
```

### 1.4 完成购买

1. 设置实例名称：`ai-research-assistant`
2. 设置密码（记住！）
3. 勾选同意协议
4. 点击"立即购买"
5. 完成支付

---

## 🔐 第二步：配置 SSH 访问

### 2.1 获取服务器 IP

1. 进入轻量应用服务器控制台
2. 找到你的实例
3. 记录"公网 IP"

### 2.2 配置防火墙

在控制台 → 防火墙 → 添加规则：

```
规则 1: SSH
  - 协议: TCP
  - 端口: 22
  - 来源: 0.0.0.0/0 (或你的 IP)

规则 2: HTTP
  - 协议: TCP
  - 端口: 80
  - 来源: 0.0.0.0/0

规则 3: HTTPS
  - 协议: TCP
  - 端口: 443
  - 来源: 0.0.0.0/0
```

### 2.3 SSH 连接

```bash
# 使用密码连接
ssh root@你的服务器IP

# 首次连接会提示，输入 yes
# 然后输入购买时设置的密码
```

---

## 🛠️ 第三步：配置服务器环境

### 3.1 更新系统

```bash
# 更新软件包列表
apt update

# 升级已安装的软件包
apt upgrade -y
```

### 3.2 安装必要软件

```bash
# 安装基础工具
apt install -y git curl wget vim htop

# 安装 Docker（如果镜像没有预装）
curl -fsSL https://get.docker.com | sh

# 启动 Docker
systemctl start docker
systemctl enable docker

# 验证 Docker
docker --version
```

### 3.3 安装 Docker Compose

```bash
# 下载 Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
chmod +x /usr/local/bin/docker-compose

# 验证
docker-compose --version
```

### 3.4 安装 Nginx

```bash
# 安装 Nginx
apt install -y nginx

# 启动 Nginx
systemctl start nginx
systemctl enable nginx

# 验证
systemctl status nginx
```

---

## 📦 第四步：部署应用

### 4.1 克隆代码

```bash
# 进入工作目录
cd /opt

# 克隆仓库
git clone https://github.com/ameureka/ai-deepresearch-agent.git

# 进入项目目录
cd ai-deepresearch-agent
```

### 4.2 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

**填入以下内容**:
```bash
# 数据库
DATABASE_URL=postgresql://neondb_owner:npg_xxx@ep-xxx.aws.neon.tech/neondb?sslmode=require

# API Keys
OPENAI_API_KEY=sk-proj-xxx
DEEPSEEK_API_KEY=sk-xxx
TAVILY_API_KEY=tvly-dev-xxx

# 环境配置
ENV=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=*

# 上下文优化
ENABLE_CHUNKING=true
CHUNKING_THRESHOLD=0.8
MAX_CHUNK_SIZE=6000
CHUNK_OVERLAP=200
```

保存并退出（`:wq`）

### 4.3 构建 Docker 镜像

```bash
# 构建镜像
docker build -t ai-research-assistant:latest .

# 查看镜像
docker images
```

### 4.4 运行容器

```bash
# 运行容器
docker run -d \
  --name ai-app \
  --restart always \
  -p 8000:8000 \
  --env-file .env \
  ai-research-assistant:latest

# 查看容器状态
docker ps

# 查看日志
docker logs -f ai-app
```

### 4.5 验证应用

```bash
# 测试健康检查
curl http://localhost:8000/api/health

# 应该返回 JSON 响应
```

---

## 🌐 第五步：配置 Nginx

### 5.1 创建 Nginx 配置

```bash
# 创建配置文件
vim /etc/nginx/sites-available/ai-app
```

**配置内容**:
```nginx
server {
    listen 80;
    server_name 你的域名或IP;  # 例如: ai.example.com 或 123.456.789.0

    # 日志
    access_log /var/log/nginx/ai-app-access.log;
    error_log /var/log/nginx/ai-app-error.log;

    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE 支持（重要！）
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        
        # 超时设置
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # 静态文件
    location /static {
        alias /opt/ai-deepresearch-agent/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

### 5.2 启用配置

```bash
# 创建软链接
ln -s /etc/nginx/sites-available/ai-app /etc/nginx/sites-enabled/

# 测试配置
nginx -t

# 重启 Nginx
systemctl restart nginx
```

### 5.3 验证访问

```bash
# 在浏览器访问
http://你的服务器IP

# 应该能看到应用首页
```

---

## 🔒 第六步：配置 SSL（HTTPS）

### 6.1 安装 Certbot

```bash
# 安装 Certbot
apt install -y certbot python3-certbot-nginx
```

### 6.2 获取 SSL 证书

**前提**: 你需要有一个域名，并将 A 记录指向服务器 IP

```bash
# 获取证书（自动配置 Nginx）
certbot --nginx -d 你的域名

# 例如:
# certbot --nginx -d ai.example.com

# 按提示操作:
# 1. 输入邮箱
# 2. 同意服务条款
# 3. 选择是否重定向 HTTP 到 HTTPS（推荐选择 2）
```

### 6.3 测试自动续期

```bash
# 测试续期
certbot renew --dry-run

# 如果成功，证书会自动续期
```

### 6.4 验证 HTTPS

```bash
# 在浏览器访问
https://你的域名

# 应该看到绿色锁图标
```

---

## 📊 第七步：配置监控和日志

### 7.1 配置日志轮转

```bash
# 创建日志轮转配置
vim /etc/logrotate.d/ai-app
```

**内容**:
```
/var/log/nginx/ai-app-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

### 7.2 配置 Docker 日志限制

```bash
# 停止容器
docker stop ai-app
docker rm ai-app

# 重新运行（带日志限制）
docker run -d \
  --name ai-app \
  --restart always \
  -p 8000:8000 \
  --env-file /opt/ai-deepresearch-agent/.env \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  ai-research-assistant:latest
```

### 7.3 查看日志

```bash
# 查看应用日志
docker logs -f ai-app

# 查看 Nginx 日志
tail -f /var/log/nginx/ai-app-access.log
tail -f /var/log/nginx/ai-app-error.log

# 查看系统资源
htop
```

---

## ✅ 第八步：验证部署

### 8.1 功能测试

```bash
# 1. 健康检查
curl https://你的域名/api/health

# 2. 模型列表
curl https://你的域名/api/models

# 3. 首页
# 在浏览器访问: https://你的域名/
```

### 8.2 性能测试

```bash
# 安装 Apache Bench
apt install -y apache2-utils

# 测试并发性能
ab -n 100 -c 10 https://你的域名/api/health
```

### 8.3 安全检查

```bash
# 检查开放端口
netstat -tulpn | grep LISTEN

# 应该只看到: 22, 80, 443

# 检查防火墙
ufw status

# 检查 SSL 评分
# 访问: https://www.ssllabs.com/ssltest/
```

---

## 🔄 日常运维

### 查看应用状态

```bash
# 查看容器状态
docker ps

# 查看容器日志
docker logs ai-app --tail 100

# 查看资源使用
docker stats ai-app
```

### 重启应用

```bash
# 重启容器
docker restart ai-app

# 重启 Nginx
systemctl restart nginx
```

### 更新应用

```bash
# 进入项目目录
cd /opt/ai-deepresearch-agent

# 拉取最新代码
git pull origin main

# 重新构建镜像
docker build -t ai-research-assistant:latest .

# 停止并删除旧容器
docker stop ai-app
docker rm ai-app

# 运行新容器
docker run -d \
  --name ai-app \
  --restart always \
  -p 8000:8000 \
  --env-file .env \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  ai-research-assistant:latest

# 验证
docker logs -f ai-app
```

### 备份数据

```bash
# 备份环境变量
cp /opt/ai-deepresearch-agent/.env ~/backup/.env.$(date +%Y%m%d)

# 备份 Nginx 配置
cp /etc/nginx/sites-available/ai-app ~/backup/nginx-ai-app.$(date +%Y%m%d)

# 数据库备份（Neon 自动备份，无需手动）
```

---

## 🆘 故障排查

### 问题 1: 容器无法启动

```bash
# 查看详细日志
docker logs ai-app

# 常见原因:
# - 环境变量配置错误
# - 端口被占用
# - 内存不足

# 解决方案:
# 1. 检查 .env 文件
# 2. 检查端口: netstat -tulpn | grep 8000
# 3. 检查内存: free -h
```

### 问题 2: Nginx 502 Bad Gateway

```bash
# 检查容器是否运行
docker ps

# 检查容器日志
docker logs ai-app

# 检查 Nginx 配置
nginx -t

# 检查 Nginx 日志
tail -f /var/log/nginx/ai-app-error.log
```

### 问题 3: SSL 证书问题

```bash
# 检查证书状态
certbot certificates

# 手动续期
certbot renew

# 重启 Nginx
systemctl restart nginx
```

### 问题 4: 内存不足

```bash
# 查看内存使用
free -h

# 查看进程内存
docker stats

# 解决方案:
# 1. 减少 workers 数量
# 2. 清理 Docker 缓存: docker system prune -a
# 3. 升级服务器配置
```

---

## 📈 性能优化

### 1. 启用 HTTP/2

编辑 Nginx 配置:
```nginx
listen 443 ssl http2;
```

### 2. 启用缓存

```nginx
# 在 server 块中添加
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

location / {
    proxy_cache my_cache;
    proxy_cache_valid 200 10m;
    # ...
}
```

### 3. 优化 Docker

```bash
# 限制容器资源
docker run -d \
  --name ai-app \
  --restart always \
  -p 8000:8000 \
  --memory="1.5g" \
  --cpus="1.5" \
  --env-file .env \
  ai-research-assistant:latest
```

---

## 🎉 部署完成检查清单

- [ ] 服务器购买并配置
- [ ] SSH 访问正常
- [ ] Docker 安装并运行
- [ ] 应用容器运行正常
- [ ] Nginx 配置完成
- [ ] SSL 证书配置（如有域名）
- [ ] 防火墙配置正确
- [ ] 日志轮转配置
- [ ] 监控配置
- [ ] 功能测试通过
- [ ] 性能测试通过
- [ ] 安全检查通过
- [ ] 备份策略制定

---

## 📞 获取帮助

如果遇到问题:

1. **查看日志**: `docker logs ai-app`
2. **查看文档**: 本指南的故障排查部分
3. **搜索错误**: Google/Stack Overflow
4. **提交 Issue**: GitHub 仓库

---

**恭喜！你已经成功将 AI Research Assistant 部署到腾讯云！** 🎉
