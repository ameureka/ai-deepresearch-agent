# 🚀 Claude Code CLI 使用进阶路线图

## 📋 概述

这是一个从基础到企业级部署的 Claude Code CLI 完整学习路径，分为 5 个级别。

---

## 🎯 LEVEL 1: Core CLI（核心 CLI）

### 1.1 Setup（设置）
- **Installation methods** - 安装方法
- **Authentication** - 身份认证
- **Update management** - 更新管理

### 1.2 CLI Reference（CLI 参考）
- **Claude, -p, -c, -f** - 基础命令
- **--add-dir, --add-file** - 添加目录和文件
- **permission-mode** - 权限模式
- **Output formats** - 输出格式

### 1.3 Interactive Mode（交互模式）
- **Keyboard shortcuts** - 键盘快捷键
- **@mentions** - @提及功能
- **Image input** - 图片输入

### 1.4 Common Workflows（常见工作流）
- **Code review** - 代码审查
- **Feature implementation** - 功能实现
- **Git operations** - Git 操作

### 1.5 Permissions（权限）
- **Permission modes** - 权限模式
- **Tool approval system** - 工具审批系统
- **Working directories** - 工作目录

---

## ⚙️ LEVEL 2: Configuration & Customization（配置与自定义）

### 2.1 Settings Files（设置文件）
- **Hierarchy & precedence** - 层级和优先级
- **permissions.json structure** - permissions.json 结构
- **env variables** - 环境变量

### 2.2 Memory CLAUDE.md（记忆文件）
- **File hierarchy** - 文件层级
- **Content structure** - 内容结构
- **Project context** - 项目上下文

### 2.3 Slash Commands（斜杠命令）
- **claude/commands/** - 命令目录
- **$ARGUMENTS usage** - 参数使用
- **Command organization** - 命令组织

### 2.4 Terminal Config（终端配置）
- **Shell integration** - Shell 集成
- **Status line** - 状态行
- **Theme configuration** - 主题配置

### 2.5 Model Config（模型配置）
- **Model selection** - 模型选择
- **Thinking tokens** - 思考令牌
- **Fallback models** - 备用模型

---

## 🔌 LEVEL 3: Extension Systems（扩展系统）

### 3.1 Subagents（子代理）
- **Agent structure YAML** - 代理结构 YAML
- **Tool permissions** - 工具权限
- **Invocation patterns** - 调用模式

### 3.2 MCP Integration（MCP 集成）
- **Transport types: stdio, SSE** - 传输类型：stdio、SSE
- **mcp.json config** - mcp.json 配置
- **OAuth authentication** - OAuth 认证

### 3.3 Hooks（钩子）
- **Lifecycle events** - 生命周期事件
- **Knowledge/PostInclude** - 知识/后包含
- **Permission hooks** - 权限钩子

### 3.4 Output Styles（输出样式）
- **System prompt modification** - 系统提示修改
- **Style creation** - 样式创建
- **Style switching** - 样式切换

### 3.5 Skills System（技能系统）
- **SKILL.md structure** - SKILL.md 结构
- **Progressive disclosure** - 渐进式披露
- **Resource bundling** - 资源打包

---

## 💻 LEVEL 4: Programmatic Usage（编程使用）

### 4.1 Headless Mode（无头模式）
- **--output-format json** - 输出格式 json
- **Stream processing** - 流处理
- **Exit codes** - 退出码

### 4.2 Python SDK（Python SDK）
- **ClaudeSDKClient** - Claude SDK 客户端
- **ClaudeCodeOptions** - Claude Code 选项
- **Async streaming** - 异步流式传输

### 4.3 TypeScript SDK（TypeScript SDK）
- **query function** - 查询函数
- **Message types** - 消息类型
- **SDK MCP servers** - SDK MCP 服务器

### 4.4 GitHub Actions（GitHub Actions）
- **@claude mentions** - @claude 提及
- **Workflow configuration** - 工作流配置
- **Environment setup** - 环境设置

---

## 🏢 LEVEL 5: Enterprise Deployment（企业部署）

### 5.1 IAM（身份和访问管理）
- **Auth methods: API/Bedrock/Vertex** - 认证方法
- **Managed policies** - 托管策略
- **Credential management** - 凭证管理

### 5.2 Cloud Providers（云提供商）
- **Amazon Bedrock setup** - Amazon Bedrock 设置
- **Google Vertex AI setup** - Google Vertex AI 设置
- **Region configuration** - 区域配置

### 5.3 Network Config（网络配置）
- **Corporate proxy** - 企业代理
- **LLM Gateway** - LLM 网关
- **SSL/TLS handling** - SSL/TLS 处理

### 5.4 Security（安全）
- **Permission enforcement** - 权限强制执行
- **File exclusion patterns** - 文件排除模式
- **Audit logging** - 审计日志

### 5.5 Monitoring（监控）
- **Usage tracking** - 使用跟踪
- **Cost analysis** - 成本分析
- **Analytics** - 分析

---

## 🎓 学习路径建议

### 初学者（1-2 周）
1. 完成 Level 1 所有内容
2. 熟悉基础命令和交互模式
3. 掌握常见工作流

### 中级用户（2-4 周）
1. 学习 Level 2 配置和自定义
2. 创建自己的 CLAUDE.md 和斜杠命令
3. 配置个性化终端和模型

### 高级用户（1-2 月）
1. 掌握 Level 3 扩展系统
2. 开发子代理和 MCP 集成
3. 创建自定义技能和钩子

### 专业开发者（2-3 月）
1. 学习 Level 4 编程使用
2. 集成 Python/TypeScript SDK
3. 配置 CI/CD 和 GitHub Actions

### 企业架构师（3-6 月）
1. 实施 Level 5 企业部署
2. 配置 IAM 和云提供商
3. 建立监控和安全体系

---

## 🔑 关键概念

### CLAUDE.md
项目记忆文件，存储项目上下文、规范、最佳实践等信息。

### Slash Commands
自定义命令，通过 `/command` 调用，可以封装常用操作。

### Subagents
子代理，可以创建专门的 AI 助手处理特定任务。

### MCP (Model Context Protocol)
模型上下文协议，用于扩展 Claude 的能力（如连接数据库、API 等）。

### Hooks
生命周期钩子，在特定事件触发时执行自定义逻辑。

---

## 💡 实用技巧

### 1. 快速开始
```bash
# 安装
npm install -g @anthropic-ai/claude-code

# 认证
claude auth login

# 开始使用
claude "帮我审查这段代码"
```

### 2. 创建项目记忆
```bash
# 在项目根目录创建 CLAUDE.md
echo "# 项目规范\n\n- 使用 TypeScript\n- 遵循 ESLint 规则" > CLAUDE.md
```

### 3. 自定义命令
```bash
# 创建命令目录
mkdir -p claude/commands

# 创建自定义命令
echo "分析代码质量并给出改进建议" > claude/commands/review.md
```

### 4. 配置权限
```json
// permissions.json
{
  "allowedDirectories": ["src", "tests"],
  "deniedPatterns": ["*.env", "node_modules"]
}
```

---

## 📚 相关资源

- **官方文档**: https://docs.anthropic.com/claude/docs/claude-code
- **GitHub**: https://github.com/anthropics/claude-code
- **社区**: https://discord.gg/anthropic

---

## ✅ 检查清单

### Level 1 完成标准
- [ ] 成功安装和认证
- [ ] 熟悉基础命令
- [ ] 能够进行代码审查
- [ ] 理解权限系统

### Level 2 完成标准
- [ ] 创建 CLAUDE.md
- [ ] 配置自定义命令
- [ ] 设置终端主题
- [ ] 配置模型选择

### Level 3 完成标准
- [ ] 创建子代理
- [ ] 集成 MCP 服务
- [ ] 实现自定义钩子
- [ ] 开发技能包

### Level 4 完成标准
- [ ] 使用无头模式
- [ ] 集成 Python/TypeScript SDK
- [ ] 配置 GitHub Actions
- [ ] 实现自动化工作流

### Level 5 完成标准
- [ ] 配置企业 IAM
- [ ] 部署到云平台
- [ ] 实施安全策略
- [ ] 建立监控体系

---

**创建日期**: 2025-01-XX  
**版本**: 1.0  
**状态**: ✅ 已完成
