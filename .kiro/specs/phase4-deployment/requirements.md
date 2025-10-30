# Phase 4: 整合部署 - 需求文档

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 4 - 整合部署
- **版本**: 1.0
- **创建日期**: 2025-10-30
- **状态**: 待实施
- **依赖**: Phase 1 + Phase 2 + Phase 3 必须完成

---

## 简介

本文档定义了 Phase 4（整合部署）的功能需求。该阶段的目标是完成项目整合，实现本地联调和生产部署，确保系统稳定运行，预计 1.5-2 周完成。

---

## 术语表

- **System**: 完整的 AI 研究助手系统（前端 + 后端）
- **Monorepo**: 单一代码仓库包含多个项目
- **Local Development**: 本地开发环境
- **Production Deployment**: 生产环境部署
- **Render**: 后端部署平台
- **Vercel**: 前端部署平台
- **Neon**: PostgreSQL 数据库服务
- **Docker Compose**: 容器编排工具
- **CORS**: 跨域资源共享
- **Environment Variables**: 环境变量
- **Health Check**: 健康检查
- **Keep-Alive**: 防休眠机制
- **E2E Testing**: 端到端测试

---

## 需求

### Requirement 1: 项目结构整合

**用户故事**: 作为开发者，我希望项目结构清晰合理，以便维护和协作

#### 验收标准

1. THE System SHALL 采用 monorepo 结构，前后端平级
2. THE System SHALL 将 `achive/ai-chatbot-main` 移动到 `ai-chatbot-main`
3. THE System SHALL 保持 `src/` 和 `main.py` 在根目录
4. THE System SHALL 在根目录提供统一的 README.md
5. THE System SHALL 在根目录提供 docker-compose.yml（可选）
6. THE System SHALL 更新 .gitignore 排除敏感文件

### Requirement 2: 环境变量管理

**用户故事**: 作为开发者，我希望环境变量管理清晰，以便配置不同环境

#### 验收标准

1. THE System SHALL 在根目录提供 .env.example（FastAPI 配置）
2. THE System SHALL 在 ai-chatbot-main/ 提供 .env.example（Next.js 配置）
3. THE System SHALL 在根目录提供 .env.local（本地开发统一配置）
4. THE System SHALL 不提交 .env.local 到 Git
5. THE System SHALL 提供环境变量检查脚本
6. THE System SHALL 在 README 中说明环境变量配置

### Requirement 3: 本地开发环境（直接运行）

**用户故事**: 作为开发者，我希望能够直接运行项目，不依赖 Docker

#### 验收标准

1. THE System SHALL 支持在 Terminal 1 启动 FastAPI
2. THE System SHALL 支持在 Terminal 2 启动 Next.js
3. THE System SHALL 支持在 Terminal 3 启动 PostgreSQL（可选）
4. THE System SHALL 在 README 中提供启动命令
5. THE System SHALL 验证前后端可以通信
6. THE System SHALL 验证数据库连接正常

### Requirement 4: 本地开发环境（Docker Compose）

**用户故事**: 作为开发者，我希望能够使用 Docker Compose 一键启动，以便统一环境

#### 验收标准

1. THE System SHALL 提供 docker-compose.yml 文件
2. THE System SHALL 定义 postgres 服务
3. THE System SHALL 定义 backend 服务
4. THE System SHALL 定义 frontend 服务
5. THE System SHALL 配置服务依赖关系
6. THE System SHALL 配置卷挂载（代码热重载）
7. THE System SHALL 支持 `docker-compose up -d` 一键启动

### Requirement 5: Dockerfile 配置

**用户故事**: 作为运维人员，我希望有标准的 Dockerfile，以便容器化部署

#### 验收标准

1. THE System SHALL 提供 Dockerfile.backend（FastAPI）
2. THE System SHALL 使用 Python 3.11-slim 基础镜像
3. THE System SHALL 安装所有依赖
4. THE System SHALL 暴露 8000 端口
5. THE System SHALL 使用 uvicorn 启动应用
6. THE System SHALL 优化镜像大小（< 500MB）

### Requirement 6: 数据库部署

**用户故事**: 作为运维人员，我希望部署 PostgreSQL 数据库到 Neon

#### 验收标准

1. THE System SHALL 在 Neon 创建项目
2. THE System SHALL 获取数据库连接字符串
3. THE System SHALL 使用 SSL 连接（sslmode=require）
4. THE System SHALL 运行数据库迁移
5. THE System SHALL 验证所有表创建成功
6. THE System SHALL 验证前后端都能连接数据库

### Requirement 7: 后端部署到 Render

**用户故事**: 作为运维人员，我希望部署 FastAPI 后端到 Render

#### 验收标准

1. THE System SHALL 在 Render 创建 Web Service
2. THE System SHALL 连接 GitHub 仓库
3. THE System SHALL 使用 Docker 运行时
4. THE System SHALL 配置所有必需的环境变量
5. THE System SHALL 部署成功并获取 URL
6. THE System SHALL 通过健康检查验证

### Requirement 8: 前端部署到 Vercel

**用户故事**: 作为运维人员，我希望部署 Next.js 前端到 Vercel

#### 验收标准

1. THE System SHALL 使用 Vercel CLI 部署
2. THE System SHALL 配置所有必需的环境变量
3. THE System SHALL 配置 RESEARCH_API_URL 指向 Render
4. THE System SHALL 配置 DATABASE_URL 指向 Neon
5. THE System SHALL 部署成功并获取 URL
6. THE System SHALL 验证前端可以访问

### Requirement 9: CORS 配置

**用户故事**: 作为运维人员，我希望配置正确的 CORS，以便前后端通信

#### 验收标准

1. THE System SHALL 在 FastAPI 配置 CORS 中间件
2. THE System SHALL 允许 localhost:3000（开发环境）
3. THE System SHALL 允许 Vercel 生产域名
4. THE System SHALL 允许 Vercel 预览域名（通配符）
5. THE System SHALL 从环境变量读取 ALLOWED_ORIGINS
6. THE System SHALL 验证跨域请求正常

### Requirement 10: 防休眠配置

**用户故事**: 作为运维人员，我希望配置防休眠机制，以便 Render 免费层不休眠

#### 验收标准

1. THE System SHALL 使用 cron-job.org 服务
2. THE System SHALL 配置每 10 分钟 ping 一次
3. THE System SHALL ping /api/health 接口
4. THE System SHALL 配置失败通知
5. THE System SHALL 验证防休眠工作正常
6. THE System SHALL 测试冷启动时间 < 60 秒

### Requirement 11: 端到端测试

**用户故事**: 作为测试人员，我希望执行完整的端到端测试，以便验证系统功能

#### 验收标准

1. THE System SHALL 测试用户注册和登录
2. THE System SHALL 测试发起研究任务
3. THE System SHALL 测试实时进度显示
4. THE System SHALL 测试报告生成
5. THE System SHALL 测试追问和更新
6. THE System SHALL 测试历史记录查看
7. THE System SHALL 测试错误处理
8. THE System SHALL 测试断线重连

### Requirement 12: 性能测试

**用户故事**: 作为测试人员，我希望验证系统性能满足要求

#### 验收标准

1. THE System SHALL 测试页面加载时间 < 3 秒
2. THE System SHALL 测试 API 响应时间 < 2 秒
3. THE System SHALL 测试 SSE 连接稳定性
4. THE System SHALL 测试并发用户（5-10 人）
5. THE System SHALL 测试长时间运行稳定性（24 小时）
6. THE System SHALL 测试内存使用情况

### Requirement 13: 兼容性测试

**用户故事**: 作为测试人员，我希望验证系统在不同环境下正常工作

#### 验收标准

1. THE System SHALL 在 Chrome 浏览器测试
2. THE System SHALL 在 Safari 浏览器测试
3. THE System SHALL 在 Firefox 浏览器测试
4. THE System SHALL 在桌面端测试
5. THE System SHALL 在移动端测试
6. THE System SHALL 在不同网络环境测试

### Requirement 14: 安全配置

**用户故事**: 作为安全管理员，我希望系统配置安全，以便保护数据

#### 验收标准

1. THE System SHALL 不在代码中硬编码 API Keys
2. THE System SHALL 使用 SSL 连接数据库
3. THE System SHALL 配置正确的 CORS
4. THE System SHALL 使用 HTTPS（Render 和 Vercel 自动提供）
5. THE System SHALL 不在日志中输出敏感信息
6. THE System SHALL 使用足够复杂的认证密钥

### Requirement 15: 监控和日志

**用户故事**: 作为运维人员，我希望能够监控系统运行状态

#### 验收标准

1. THE System SHALL 使用 Render 内置监控
2. THE System SHALL 使用 Vercel Analytics
3. THE System SHALL 使用 Neon 数据库监控
4. THE System SHALL 配置 cron-job.org 监控告警
5. THE System SHALL 记录关键操作日志
6. THE System SHALL 提供日志查看方式

### Requirement 16: 备份策略

**用户故事**: 作为运维人员，我希望有数据备份策略，以便恢复数据

#### 验收标准

1. THE System SHALL 使用 Git 版本控制代码
2. THE System SHALL 使用 Neon 自动备份数据库
3. THE System SHALL 文档化环境变量配置
4. THE System SHALL 提供数据库备份脚本
5. THE System SHALL 提供回滚方案

### Requirement 17: 成本控制

**用户故事**: 作为项目经理，我希望控制运营成本在预算内

#### 验收标准

1. THE System SHALL 使用 Vercel Hobby 计划（$0）
2. THE System SHALL 使用 Render Free 或 Starter 计划（$0-7/月）
3. THE System SHALL 使用 Neon Free 计划（$0）
4. THE System SHALL 监控 API 调用成本
5. THE System SHALL 总成本控制在 $70-80/月
6. THE System SHALL 提供成本优化建议

### Requirement 18: 文档完整性

**用户故事**: 作为开发者，我希望有完整的文档，以便理解和维护系统

#### 验收标准

1. THE System SHALL 提供统一的 README.md
2. THE System SHALL 提供快速开始指南
3. THE System SHALL 提供部署指南
4. THE System SHALL 提供环境变量配置说明
5. THE System SHALL 提供故障排查指南
6. THE System SHALL 提供架构说明

### Requirement 19: 部署自动化

**用户故事**: 作为运维人员，我希望部署过程自动化，以便快速发布

#### 验收标准

1. THE System SHALL 在 GitHub push 时自动触发 Render 部署
2. THE System SHALL 在 GitHub push 时自动触发 Vercel 部署
3. THE System SHALL 在部署失败时发送通知
4. THE System SHALL 提供部署状态查看
5. THE System SHALL 支持回滚到上一版本

### Requirement 20: 验收测试

**用户故事**: 作为项目经理，我希望有明确的验收标准，以便确认项目完成

#### 验收标准

1. THE System SHALL 通过所有功能测试
2. THE System SHALL 通过所有性能测试
3. THE System SHALL 通过所有兼容性测试
4. THE System SHALL 在生产环境稳定运行 24 小时
5. THE System SHALL 成本在预算内
6. THE System SHALL 文档完整

---

## 非功能需求

### NFR 1: 可维护性

- 项目结构清晰
- 配置集中管理
- 文档完整准确
- 代码质量高

### NFR 2: 可部署性

- 支持一键部署
- 支持多环境配置
- 支持快速回滚
- 部署过程自动化

### NFR 3: 可监控性

- 提供健康检查
- 提供日志查看
- 提供性能监控
- 提供告警机制

### NFR 4: 成本效益

- 使用免费层服务
- 优化资源使用
- 控制 API 成本
- 提供成本报告

---

## 依赖关系

### 外部依赖

- Render 平台
- Vercel 平台
- Neon 数据库
- cron-job.org 服务
- GitHub 仓库

### 内部依赖

- Phase 1 (DeepSeek 集成) 必须完成
- Phase 2 (API 标准化) 必须完成
- Phase 3 (Next.js 前端) 必须完成

---

## 验收标准总结

Phase 4 完成的标准：

1. ✅ 所有 20 个需求的验收标准都已满足
2. ✅ 项目结构整合完成
3. ✅ 环境变量配置完整
4. ✅ 本地开发环境正常
5. ✅ 数据库部署成功
6. ✅ 后端部署成功
7. ✅ 前端部署成功
8. ✅ CORS 配置正确
9. ✅ 防休眠配置生效
10. ✅ 端到端测试通过
11. ✅ 性能测试通过
12. ✅ 兼容性测试通过
13. ✅ 安全配置完善
14. ✅ 监控和日志正常
15. ✅ 成本在预算内
16. ✅ 文档完整

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待实施
