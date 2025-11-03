# 更新日志 / Changelog

## [0.3.0] - 2025-11-04

### 🎉 生产部署完成 / Production Deployment Complete

#### 新增 / Added

**部署架构 / Deployment Architecture:**
- ✅ 前端部署到 Vercel（https://deepresearch.ameureka.com）
- ✅ 后端部署到腾讯云 Ubuntu 服务器（https://api.ameureka.com）
- ✅ 使用 Cloudflare Tunnel 提供 HTTPS 访问
- ✅ Neon PostgreSQL 生产环境数据库

**文档 / Documentation:**
- 📊 [后端部署状态文档](./docs/BACKEND_DEPLOYMENT_STATUS.md) - 完整的生产环境配置详情
- ☁️ [腾讯云部署指南](./docs/TENCENT_CLOUD_DEPLOYMENT.md) - 后端部署到腾讯云的完整步骤
- 🔒 [Cloudflare Tunnel 设置](./docs/CLOUDFLARE_TUNNEL_SETUP.md) - HTTPS 隧道配置指南
- 🚀 [Vercel 部署指南](./docs/VERCEL_DEPLOYMENT_GUIDE.md) - 前端部署指南
- 🔍 [环境配置检查](./docs/ENVIRONMENT_CONFIG_CHECK.md) - 配置验证工具

**运维脚本 / Operations Scripts:**
- 🛠️ `scripts/check-backend-status.sh` - 一键检查后端服务状态
- ✅ `scripts/verify-deployment.sh` - 验证完整部署
- 🚀 `scripts/deploy-cloudflare.sh` - 自动化部署到腾讯云
- 🔄 `scripts/update-backend.sh` - 快速更新后端代码

#### 修复 / Fixed

**构建问题 / Build Issues:**
- 🔧 修复 CORS 配置（添加 https:// 协议前缀）
- 🔧 修复 TypeScript 类型错误（route.ts, research-preview/page.tsx）
- 🔧 修复 .gitignore 配置（包含 ai-chatbot-main/lib/ 目录）
- 🔧 清理构建缓存，确保干净构建

**配置优化 / Configuration Optimization:**
- ⚙️ 后端 CORS 配置支持 Vercel 域名
- ⚙️ Cloudflare Tunnel 配置优化
- ⚙️ Systemd 服务自动启动配置
- ⚙️ 环境变量标准化

#### 验证 / Verified

**服务状态 / Service Status:**
- ✅ 后端服务运行正常（4 个 worker 进程）
- ✅ Cloudflare Tunnel 连接稳定（4 个活跃连接）
- ✅ 前端 Vercel 部署成功
- ✅ 数据库连接正常
- ✅ 健康检查通过
- ✅ API 文档可访问

**性能指标 / Performance Metrics:**
- 📊 后端内存使用：335.2 MB
- 📊 Cloudflare Tunnel 内存：14.7 MB
- 📊 磁盘使用：7.9GB / 50GB (17%)
- 📊 系统内存：859MB / 1.9GB

#### 更新 / Updated

**README 文档 / README Documentation:**
- 📝 更新版本号至 0.3.0
- 📝 添加新增文档和脚本的链接
- 📝 更新部署指南章节
- 📝 添加运维脚本章节
- 📝 更新版本历史
- 📝 更新最后更新日期

---

## [0.2.0] - 2025-11-01

### 第 4 阶段部署 / Phase 4 Deployment

#### 新增 / Added
- ✅ Monorepo 结构（前端 + 后端同级）
- ✅ 自动化设置脚本（setup-backend.sh, setup-frontend.sh, dev.sh）
- ✅ 生产环境部署指南
- ✅ 完整的环境变量文档
- ✅ 本地开发指南
- ✅ 更新 .gitignore

---

## [0.1.5] - 2025-10-31

### 第 3 阶段前端集成 / Phase 3 Frontend Integration

#### 新增 / Added
- ✅ ResearchButton, ResearchPanel, ResearchProgress 组件
- ✅ useResearchProgress Hook（POST SSE）
- ✅ Chat 组件集成
- ✅ 研究工具函数
- ✅ 17 个单元测试

---

## [0.1.2] - 2025-10-31

### 第 2 阶段 API 标准化 / Phase 2 API Standardization

#### 新增 / Added
- ✅ 统一 API 响应格式（ApiResponse）
- ✅ SSE 流式接口（/api/research/stream）
- ✅ 5 种 SSE 事件类型
- ✅ 全局错误处理
- ✅ 健康检查端点
- ✅ 模型列表端点
- ✅ CORS 配置

---

## [0.1.0] - 2025-10-31

### 第 1 和 1.5 阶段 / Phase 1 & 1.5

#### 新增 / Added
- ✅ DeepSeek API 集成
- ✅ 智能上下文管理
- ✅ 成本优化（节省约 45%）
- ✅ 64 个后端单元测试

---

## 部署信息 / Deployment Information

### 生产环境 / Production Environment

**前端 / Frontend:**
- 平台：Vercel
- URL：https://deepresearch.ameureka.com
- 状态：✅ 运行中

**后端 / Backend:**
- 平台：腾讯云 Ubuntu
- URL：https://api.ameureka.com
- 隧道：Cloudflare Tunnel
- 状态：✅ 运行中

**数据库 / Database:**
- 平台：Neon PostgreSQL
- 区域：us-east-2
- 状态：✅ 运行中

### 架构图 / Architecture Diagram

```
用户浏览器 / User Browser
    ↓
Vercel 前端 / Vercel Frontend
https://deepresearch.ameureka.com
    ↓
Cloudflare Tunnel
https://api.ameureka.com
    ↓
腾讯云服务器 / Tencent Cloud Server
FastAPI 后端 / FastAPI Backend
localhost:8000
    ↓
Neon PostgreSQL 数据库 / Neon PostgreSQL Database
```

---

## 贡献者 / Contributors

感谢所有为这个项目做出贡献的人！

---

**项目链接 / Project Link:** https://github.com/ameureka/ai-deepresearch-agent
