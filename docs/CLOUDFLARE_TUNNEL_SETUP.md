# Cloudflare Tunnel 配置指南

> 使用 Cloudflare Tunnel 为后端 API 提供安全的 HTTPS 访问

## 📋 目录

- [什么是 Cloudflare Tunnel](#什么是-cloudflare-tunnel)
- [为什么使用 Cloudflare Tunnel](#为什么使用-cloudflare-tunnel)
- [前置要求](#前置要求)
- [配置步骤](#配置步骤)
- [验证配置](#验证配置)
- [日常管理](#日常管理)
- [故障排查](#故障排查)

---

## 🌐 什么是 Cloudflare Tunnel

Cloudflare Tunnel（原名 Argo Tunnel）是一个安全的隧道服务，可以：

- 🔒 **无需开放端口**：通过加密隧道连接到 Cloudflare
- 🛡️ **隐藏真实 IP**：服务器 IP 不会暴露给公网
- 🚀 **自动 HTTPS**：免费 SSL 证书，自动续期
- 🌍 **全球 CDN**：接入 Cloudflare 全球网络
- 🔐 **DDoS 防护**：免费基础 DDoS 防护

### 工作原理

```
用户浏览器
    ↓ HTTPS 请求
Cloudflare CDN (全球 300+ 数据中心)
    ↓ 加密隧道
cloudflared (服务器上的隧道客户端)
    ↓ localhost
FastAPI 后端 (127.0.0.1:8000)
```

**关键特点**：
- ✅ 服务器只需要**出站连接**到 Cloudflare
- ✅ 无需开放任何入站端口（除了 SSH）
- ✅ 所有流量经过 Cloudflare 加密和保护

---

## 💡 为什么使用 Cloudflare Tunnel

### 与传统方案对比

| 特性 | Cloudflare Tunnel | Nginx + Certbot | 直接暴露 |
|------|-------------------|-----------------|---------|
| **配置难度** | ⭐⭐ 简单 | ⭐⭐⭐ 中等 | ⭐ 最简单 |
| **HTTPS** | ✅ 自动 | ⚠️ 需配置 | ❌ 不支持 |
| **隐藏 IP** | ✅ 是 | ❌ 否 | ❌ 否 |
| **DDoS 防护** | ✅ 免费 | ❌ 无 | ❌ 无 |
| **CDN 加速** | ✅ 全球 | ❌ 无 | ❌ 无 |
| **证书管理** | ✅ 自动 | ⚠️ 手动 | ❌ 无 |
| **端口要求** | 仅 SSH | 80/443/8000 | 8000 |
| **成本** | 免费 | 免费 | 免费 |

### 适用场景

✅ **推荐使用**：
- 个人项目和中小型应用
- 需要快速上线
- 预算有限
- 需要 DDoS 防护
- 不想暴露服务器 IP

❌ **不推荐使用**：
- 大型企业应用（需完全自主控制）
- 极低延迟要求（< 10ms）
- 严格合规要求（所有流量必须自主控制）

---

## 📝 前置要求

### 必须具备

- [x] **Cloudflare 账号**
  - 免费注册：https://dash.cloudflare.com/sign-up
  
- [x] **域名**
  - 已购买域名（任何服务商）
  - 域名已添加到 Cloudflare
  - Nameservers 已修改为 Cloudflare
  
- [x] **服务器**
  - Ubuntu 20.04+ / 22.04
  - 有 root 或 sudo 权限
  - 后端服务已运行在 localhost:8000

### 需要准备的信息

```bash
# 域名信息
主域名: yourdomain.com
API 子域名: api.yourdomain.com

# 服务器信息
服务器 IP: ___________________
SSH 端口: 22
```

---

## 🚀 配置步骤

### 步骤 1: 添加域名到 Cloudflare

#### 1.1 注册 Cloudflare 账号

1. 访问 https://dash.cloudflare.com/sign-up
2. 使用邮箱注册免费账号
3. 验证邮箱

#### 1.2 添加域名

1. 登录 Cloudflare 控制台
2. 点击 "Add a Site"
3. 输入你的域名（例如：`yourdomain.com`）
4. 选择 "Free" 计划
5. 点击 "Continue"

#### 1.3 修改 Nameservers

Cloudflare 会提供两个 Nameservers，例如：
```
alice.ns.cloudflare.com
bob.ns.cloudflare.com
```

**在你的域名服务商处修改**：

**腾讯云 DNSPod**：
1. 登录腾讯云控制台
2. 进入"域名注册" → 选择域名 → "DNS 管理"
3. 修改 DNS 服务器为 Cloudflare 提供的地址
4. 保存

**阿里云**：
1. 登录阿里云控制台
2. 进入"域名" → 选择域名 → "DNS 修改"
3. 修改 DNS 服务器为 Cloudflare 提供的地址
4. 保存

**GoDaddy**：
1. 登录 GoDaddy 账号
2. 进入"我的产品" → 选择域名 → "管理 DNS"
3. 点击"更改" → "自定义"
4. 输入 Cloudflare 的 Nameservers
5. 保存

#### 1.4 等待 DNS 生效

- ⏱️ 通常需要 5-30 分钟
- 🔍 在 Cloudflare 控制台查看状态
- ✅ 状态变为 "Active" 后即可继续

**验证 DNS 是否生效**：
```bash
# 在本地电脑运行
nslookup yourdomain.com

# 应该看到 Cloudflare 的 IP 地址
```

---

### 步骤 2: 安装 cloudflared

SSH 登录你的服务器：

```bash
ssh root@你的服务器IP
```

#### 2.1 下载 cloudflared

```bash
# 下载最新版本
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# 安装
sudo dpkg -i cloudflared-linux-amd64.deb

# 验证安装
cloudflared --version
```

**应该显示**：
```
cloudflared version 2024.x.x
```

#### 2.2 清理安装包

```bash
rm cloudflared-linux-amd64.deb
```

---

### 步骤 3: 登录 Cloudflare

```bash
cloudflared tunnel login
```

**会输出一个 URL**，类似：
```
Please open the following URL and log in with your Cloudflare account:

https://dash.cloudflare.com/argotunnel?callback=https%3A%2F%2Flogin...

Leave cloudflared running to download the cert automatically.
```

**操作步骤**：
1. **复制这个 URL**
2. **在本地电脑浏览器打开**
3. 登录你的 Cloudflare 账号
4. 选择你的域名（例如：`yourdomain.com`）
5. 点击 "Authorize" 按钮
6. 返回服务器终端

**应该看到**：
```
INF You have successfully logged in.
If you wish to copy your credentials to a server, they have been saved to:
/root/.cloudflared/cert.pem
```

证书已保存到 `~/.cloudflared/cert.pem`

---

### 步骤 4: 创建隧道

```bash
cloudflared tunnel create agentic-backend
```

**会输出**：
```
Tunnel credentials written to /root/.cloudflared/12345678-1234-1234-1234-123456789abc.json
Created tunnel agentic-backend with id 12345678-1234-1234-1234-123456789abc
```

**📝 重要：记下隧道 ID！**

例如：`12345678-1234-1234-1234-123456789abc`

**文件说明**：
- `cert.pem`：Cloudflare 账号凭证
- `隧道ID.json`：隧道凭证文件

---

### 步骤 5: 配置 DNS

```bash
cloudflared tunnel route dns agentic-backend api.yourdomain.com
```

**替换**：
- `agentic-backend`：隧道名称
- `api.yourdomain.com`：你的 API 域名

**会输出**：
```
INF Added CNAME api.yourdomain.com which will route to this tunnel tunnelID=12345678-1234-1234-1234-123456789abc
```

**这会自动在 Cloudflare 创建 DNS 记录**：
```
Type: CNAME
Name: api
Target: 12345678-1234-1234-1234-123456789abc.cfargotunnel.com
Proxy: Enabled (橙色云朵)
```

**验证 DNS 记录**：
1. 登录 Cloudflare 控制台
2. 选择你的域名
3. 进入 "DNS" → "Records"
4. 应该看到新创建的 CNAME 记录

---

### 步骤 6: 创建配置文件

```bash
# 创建配置目录（如果不存在）
mkdir -p ~/.cloudflared

# 编辑配置文件
nano ~/.cloudflared/config.yml
```

**写入以下内容**（**替换隧道 ID 和域名**）：

```yaml
# 隧道 ID（替换为你的隧道 ID）
tunnel: 12345678-1234-1234-1234-123456789abc

# 凭证文件路径（替换隧道 ID）
credentials-file: /root/.cloudflared/12345678-1234-1234-1234-123456789abc.json

# 入口规则
ingress:
  # API 域名（替换为你的域名）
  - hostname: api.yourdomain.com
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
  
  # 默认规则（必须保留）
  - service: http_status:404
```

**配置说明**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `tunnel` | 隧道 ID | `12345678-1234-1234-1234-123456789abc` |
| `credentials-file` | 凭证文件路径 | `/root/.cloudflared/隧道ID.json` |
| `hostname` | API 域名 | `api.yourdomain.com` |
| `service` | 后端服务地址 | `http://localhost:8000` |
| `noTLSVerify` | 跳过 TLS 验证（本地连接） | `true` |
| `connectTimeout` | 连接超时 | `30s` |
| `keepAliveConnections` | 保持连接数 | `100` |

**保存文件**：
- 按 `Ctrl+O` → `Enter` 保存
- 按 `Ctrl+X` 退出

---

### 步骤 7: 测试隧道

在安装为系统服务前，先测试隧道是否正常：

```bash
cloudflared tunnel run agentic-backend
```

**应该看到**：
```
INF Starting tunnel tunnelID=12345678-1234-1234-1234-123456789abc
INF Version 2024.x.x
INF GOOS: Linux, GOVersion: go1.x.x
INF Settings: map[cred-file:/root/.cloudflared/12345678-1234-1234-1234-123456789abc.json ...]
INF Generated Connector ID: a71e7e00-4190-4b0a-97ca-07c21aaedf53
INF Initial protocol quic
INF ICMP proxy will use 10.3.4.9 as source for IPv4
INF ICMP proxy will use fe80::5054:ff:fe27:9ccf in zone eth0 as source for IPv6
INF Starting metrics server on 127.0.0.1:52021/metrics
INF Registered tunnel connection connIndex=0 connection=99bc731f-5197-400b-89f4-c87ec3451c08 event=0 ip=198.41.200.233 location=sin02 protocol=quic
INF Registered tunnel connection connIndex=1 connection=a7e1e6b3-9047-4ebe-b6b4-86f937377013 event=0 ip=198.41.192.37 location=sin08 protocol=quic
INF Registered tunnel connection connIndex=2 connection=e7c76e88-67ba-413b-a04b-e911c049cb78 event=0 ip=198.41.192.57 location=sin20 protocol=quic
INF Registered tunnel connection connIndex=3 connection=99bc731f-5197-400b-89f4-c87ec3451c08 event=0 ip=198.41.200.13 location=sin07 protocol=quic
```

**关键信息**：
- ✅ `Starting tunnel`：隧道已启动
- ✅ `Registered tunnel connection`：4 个连接已建立
- ✅ `protocol=quic`：使用 QUIC 协议

**在本地电脑测试**（打开新终端）：
```bash
curl https://api.yourdomain.com/health
```

**如果返回**：
```json
{"status":"healthy","version":"3.2.0",...}
```

说明隧道工作正常！

**在服务器终端按 `Ctrl+C` 停止测试。**

---

### 步骤 8: 安装为系统服务

```bash
# 安装服务
sudo cloudflared service install

# 启动服务
sudo systemctl start cloudflared

# 设置开机自启
sudo systemctl enable cloudflared
```

**应该看到**：
```
Created symlink /etc/systemd/system/multi-user.target.wants/cloudflared.service → /etc/systemd/system/cloudflared.service.
```

---

### 步骤 9: 检查服务状态

```bash
sudo systemctl status cloudflared
```

**应该显示**：
```
● cloudflared.service - cloudflared
     Loaded: loaded (/etc/systemd/system/cloudflared.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-11-03 15:30:00 UTC; 1min ago
   Main PID: 12345 (cloudflared)
      Tasks: 10 (limit: 4915)
     Memory: 25.0M
        CPU: 500ms
     CGroup: /system.slice/cloudflared.service
             └─12345 /usr/bin/cloudflared --no-autoupdate tunnel run --token=...

Nov 03 15:30:00 VM-4-9-ubuntu systemd[1]: Started cloudflared.
Nov 03 15:30:01 VM-4-9-ubuntu cloudflared[12345]: INF Starting tunnel tunnelID=12345678-1234-1234-1234-123456789abc
Nov 03 15:30:02 VM-4-9-ubuntu cloudflared[12345]: INF Registered tunnel connection connIndex=0
```

**关键状态**：
- ✅ `Loaded: loaded`：服务已加载
- ✅ `Active: active (running)`：服务正在运行
- ✅ `enabled`：开机自启已启用

---

## ✅ 验证配置

### 1. 检查服务状态

```bash
# 检查隧道服务
sudo systemctl status cloudflared

# 检查后端服务
sudo systemctl status agentic-backend
```

### 2. 查看日志

```bash
# 查看隧道日志（实时）
sudo journalctl -u cloudflared -f

# 查看最近 50 行日志
sudo journalctl -u cloudflared -n 50

# 查看错误日志
sudo journalctl -u cloudflared -p err -n 50
```

### 3. 测试本地访问

```bash
# 测试后端
curl http://localhost:8000/health

# 应该返回
# {"status":"healthy","version":"3.2.0",...}
```

### 4. 测试 HTTPS 访问

```bash
# 从服务器测试
curl https://api.yourdomain.com/health

# 从本地电脑测试
curl https://api.yourdomain.com/health

# 应该都返回相同的结果
```

### 5. 浏览器访问

打开浏览器，访问：
- **健康检查**：https://api.yourdomain.com/health
- **API 文档**：https://api.yourdomain.com/docs

应该能看到：
- 健康检查返回 JSON 数据
- API 文档显示 Swagger UI 界面

### 6. 检查 DNS 记录

登录 Cloudflare 控制台：
1. 选择你的域名
2. 进入 "DNS" → "Records"
3. 应该看到：
   ```
   Type: CNAME
   Name: api
   Target: 隧道ID.cfargotunnel.com
   Proxy status: Proxied (橙色云朵)
   TTL: Auto
   ```

### 7. 检查隧道信息

```bash
# 查看隧道列表
cloudflared tunnel list

# 查看隧道详情
cloudflared tunnel info agentic-backend
```

---

## 🔧 日常管理

### 查看服务状态

```bash
# 查看服务状态
sudo systemctl status cloudflared

# 查看服务是否启用
sudo systemctl is-enabled cloudflared

# 查看服务是否运行
sudo systemctl is-active cloudflared
```

### 重启服务

```bash
# 重启隧道服务
sudo systemctl restart cloudflared

# 重新加载配置（无需重启）
sudo systemctl reload cloudflared
```

### 停止服务

```bash
# 停止服务
sudo systemctl stop cloudflared

# 禁用开机自启
sudo systemctl disable cloudflared
```

### 查看日志

```bash
# 实时查看日志
sudo journalctl -u cloudflared -f

# 查看最近 100 行日志
sudo journalctl -u cloudflared -n 100

# 查看今天的日志
sudo journalctl -u cloudflared --since today

# 查看错误日志
sudo journalctl -u cloudflared -p err

# 查看特定时间段的日志
sudo journalctl -u cloudflared --since "2025-11-03 10:00:00" --until "2025-11-03 12:00:00"
```

### 更新 cloudflared

```bash
# 下载最新版本
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# 安装更新
sudo dpkg -i cloudflared-linux-amd64.deb

# 重启服务
sudo systemctl restart cloudflared

# 验证版本
cloudflared --version

# 清理安装包
rm cloudflared-linux-amd64.deb
```

### 修改配置

```bash
# 编辑配置文件
nano ~/.cloudflared/config.yml

# 修改后重启服务
sudo systemctl restart cloudflared

# 查看日志确认配置生效
sudo journalctl -u cloudflared -n 30
```

### 管理隧道

```bash
# 查看所有隧道
cloudflared tunnel list

# 查看隧道详情
cloudflared tunnel info agentic-backend

# 删除隧道（谨慎操作！）
cloudflared tunnel delete agentic-backend

# 清理未使用的隧道
cloudflared tunnel cleanup agentic-backend
```

---

## 🐛 故障排查

### 问题 1: 隧道无法启动

**症状**：
- `systemctl status cloudflared` 显示 `failed`
- 日志显示连接错误

**检查步骤**：

```bash
# 1. 查看详细日志
sudo journalctl -u cloudflared -n 100 --no-pager

# 2. 检查配置文件
cat ~/.cloudflared/config.yml

# 3. 检查凭证文件
ls -la ~/.cloudflared/*.json

# 4. 手动运行隧道
cloudflared tunnel run agentic-backend
```

**常见原因**：
- ❌ 配置文件路径错误
- ❌ 隧道 ID 不匹配
- ❌ 凭证文件丢失
- ❌ 网络连接问题

**解决方案**：

```bash
# 重新创建配置文件
nano ~/.cloudflared/config.yml

# 确保隧道 ID 和凭证文件路径正确
# 重启服务
sudo systemctl restart cloudflared
```

---

### 问题 2: DNS 解析失败

**症状**：
- `ping api.yourdomain.com` 无响应
- `nslookup api.yourdomain.com` 找不到记录

**检查步骤**：

```bash
# 1. 检查 Nameservers 是否已更新
nslookup yourdomain.com

# 2. 检查 DNS 记录
dig api.yourdomain.com

# 3. 在 Cloudflare 控制台检查
# DNS → Records → 查找 api.yourdomain.com
```

**解决方案**：

1. **等待 DNS 生效**（最多 48 小时，通常 5-30 分钟）

2. **重新创建 DNS 记录**：
   ```bash
   cloudflared tunnel route dns agentic-backend api.yourdomain.com
   ```

3. **手动添加 DNS 记录**：
   - 登录 Cloudflare 控制台
   - DNS → Add Record
   - Type: CNAME
   - Name: api
   - Target: `隧道ID.cfargotunnel.com`
   - Proxy status: Proxied (橙色云朵)

---

### 问题 3: 隧道连接不稳定

**症状**：
- 间歇性无法访问
- 日志显示频繁重连

**检查步骤**：

```bash
# 查看隧道日志
sudo journalctl -u cloudflared -n 200 | grep -E "error|disconnect|reconnect"

# 检查网络连接
ping 1.1.1.1

# 检查服务器负载
top
```

**解决方案**：

1. **增加隧道连接数**：
   ```bash
   nano ~/.cloudflared/config.yml
   
   # 添加配置
   protocol: quic
   no-autoupdate: true
   ```

2. **重启隧道**：
   ```bash
   sudo systemctl restart cloudflared
   ```

3. **检查服务器资源**：
   - 如果 CPU/内存不足，考虑升级配置

---

### 问题 4: 后端无法访问

**症状**：
- 隧道正常运行
- 但访问 API 返回 502 错误

**检查步骤**：

```bash
# 1. 检查后端服务
sudo systemctl status agentic-backend

# 2. 测试本地访问
curl http://localhost:8000/health

# 3. 检查端口占用
sudo lsof -i :8000

# 4. 查看后端日志
sudo journalctl -u agentic-backend -n 50
```

**解决方案**：

```bash
# 重启后端服务
sudo systemctl restart agentic-backend

# 检查配置文件中的 service 地址
nano ~/.cloudflared/config.yml

# 确保是 http://localhost:8000
# 重启隧道
sudo systemctl restart cloudflared
```

---

### 问题 5: HTTPS 证书错误

**症状**：
- 浏览器显示证书错误
- curl 返回 SSL 错误

**检查步骤**：

```bash
# 测试 SSL 证书
curl -v https://api.yourdomain.com/health

# 检查 DNS 记录
dig api.yourdomain.com
```

**解决方案**：

1. **确保 DNS 记录的 Proxy 状态为 Proxied**：
   - 登录 Cloudflare 控制台
   - DNS → Records
   - 确保 api 记录的云朵图标是橙色（Proxied）

2. **等待 SSL 证书生效**（通常 1-5 分钟）

3. **清除浏览器缓存**

---

### 问题 6: 权限错误

**症状**：
- 日志显示权限相关警告
- ICMP proxy 警告

**警告示例**：
```
WRN ICMP proxy will use unprivileged datagram-oriented endpoint. You might need to add that user to a group within that range...
```

**解决方案**：

这是一个关于 ICMP 代理权限的警告，**不影响功能**，可以安全忽略。

如果想消除警告：
```bash
# 添加用户到 ping 组
sudo usermod -aG ping root

# 重启服务
sudo systemctl restart cloudflared
```

---

## 📊 性能优化

### 1. 调整连接数

编辑配置文件：
```bash
nano ~/.cloudflared/config.yml
```

添加：
```yaml
protocol: quic
no-autoupdate: true
retries: 5
grace-period: 30s
```

### 2. 启用 Cloudflare 缓存

登录 Cloudflare 控制台：

1. 选择你的域名
2. 进入 "Caching" → "Configuration"
3. 设置 "Browser Cache TTL": 4 hours
4. 启用 "Always Online"

### 3. 配置 Page Rules

1. 进入 "Rules" → "Page Rules"
2. 创建规则：`api.yourdomain.com/docs*`
3. 设置：Cache Level = Cache Everything
4. 保存

### 4. 监控隧道性能

```bash
# 查看隧道指标
curl http://localhost:52021/metrics

# 查看连接数
sudo journalctl -u cloudflared -n 100 | grep "Registered tunnel connection"
```

---

## 🔐 安全建议

### 1. 限制访问来源

在 Cloudflare 控制台配置 WAF 规则：

1. 进入 "Security" → "WAF"
2. 创建规则限制访问来源
3. 例如：只允许特定国家/地区访问

### 2. 启用 Rate Limiting

1. 进入 "Security" → "Rate Limiting"
2. 创建规则限制请求频率
3. 例如：每分钟最多 100 个请求

### 3. 配置 IP Access Rules

1. 进入 "Security" → "WAF" → "Tools"
2. 添加 IP 黑名单或白名单

### 4. 定期更新 cloudflared

```bash
# 检查当前版本
cloudflared --version

# 查看最新版本
curl -s https://api.github.com/repos/cloudflare/cloudflared/releases/latest | grep tag_name

# 更新到最新版本
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
sudo systemctl restart cloudflared
```

---

## 📚 常用命令速查

### 服务管理

```bash
# 启动服务
sudo systemctl start cloudflared

# 停止服务
sudo systemctl stop cloudflared

# 重启服务
sudo systemctl restart cloudflared

# 查看状态
sudo systemctl status cloudflared

# 启用开机自启
sudo systemctl enable cloudflared

# 禁用开机自启
sudo systemctl disable cloudflared
```

### 日志查看

```bash
# 实时日志
sudo journalctl -u cloudflared -f

# 最近 N 行
sudo journalctl -u cloudflared -n 50

# 错误日志
sudo journalctl -u cloudflared -p err

# 今天的日志
sudo journalctl -u cloudflared --since today
```

### 隧道管理

```bash
# 列出所有隧道
cloudflared tunnel list

# 查看隧道详情
cloudflared tunnel info agentic-backend

# 手动运行隧道
cloudflared tunnel run agentic-backend

# 删除隧道
cloudflared tunnel delete agentic-backend
```

### 配置管理

```bash
# 编辑配置
nano ~/.cloudflared/config.yml

# 查看配置
cat ~/.cloudflared/config.yml

# 验证配置
cloudflared tunnel ingress validate
```

### 测试命令

```bash
# 测试本地访问
curl http://localhost:8000/health

# 测试 HTTPS 访问
curl https://api.yourdomain.com/health

# 测试 DNS 解析
nslookup api.yourdomain.com
dig api.yourdomain.com

# 测试 SSL 证书
curl -v https://api.yourdomain.com/health
```

---

## 🎓 进阶配置

### 多域名配置

如果你有多个域名或子域名：

```yaml
tunnel: 你的隧道ID
credentials-file: /root/.cloudflared/你的隧道ID.json

ingress:
  # API 域名
  - hostname: api.yourdomain.com
    service: http://localhost:8000
  
  # 管理后台
  - hostname: admin.yourdomain.com
    service: http://localhost:3000
  
  # 静态文件
  - hostname: static.yourdomain.com
    service: http://localhost:8080
  
  # 默认规则
  - service: http_status:404
```

### 负载均衡配置

如果你有多个后端服务器：

```yaml
tunnel: 你的隧道ID
credentials-file: /root/.cloudflared/你的隧道ID.json

ingress:
  - hostname: api.yourdomain.com
    service: http_status:200
    originRequest:
      httpHostHeader: api.yourdomain.com
      connectTimeout: 30s
      noTLSVerify: true
  
  - service: http_status:404
```

### 自定义响应头

```yaml
tunnel: 你的隧道ID
credentials-file: /root/.cloudflared/你的隧道ID.json

ingress:
  - hostname: api.yourdomain.com
    service: http://localhost:8000
    originRequest:
      httpHostHeader: api.yourdomain.com
      originServerName: api.yourdomain.com
      caPool: /path/to/ca.pem
      noTLSVerify: true
  
  - service: http_status:404
```

---

## 📖 参考资料

### 官方文档

- [Cloudflare Tunnel 官方文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [cloudflared GitHub](https://github.com/cloudflare/cloudflared)
- [Cloudflare Zero Trust](https://developers.cloudflare.com/cloudflare-one/)

### 相关文档

- [腾讯云部署指南](./TENCENT_CLOUD_DEPLOYMENT.md)
- [Vercel 部署指南](./VERCEL_DEPLOYMENT.md)
- [环境变量配置](./ENVIRONMENT_VARIABLES.md)

### 社区资源

- [Cloudflare Community](https://community.cloudflare.com/)
- [GitHub Issues](https://github.com/ameureka/ai-deepresearch-agent/issues)

---

## 💬 获取帮助

如果遇到问题：

1. 查看本文档的"故障排查"部分
2. 检查隧道日志：`sudo journalctl -u cloudflared -f`
3. 查看 Cloudflare 状态页：https://www.cloudflarestatus.com/
4. 在 GitHub 提交 Issue
5. 访问 Cloudflare Community 寻求帮助

---

**文档版本**: v1.0.0  
**最后更新**: 2025-11-03  
**适用版本**: cloudflared 2024.x.x+

---

**Made with ❤️ by the AI DeepResearch Team**
