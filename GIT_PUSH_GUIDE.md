# Git 推送指南 - v0.1.0

## 📋 准备工作

### 1. 确认当前状态

```bash
# 查看当前分支和标签
git log --oneline -1
git tag -l

# 应该看到:
# a1f8456 (HEAD -> main, tag: v0.1.0) Release v0.1.0: DeepSeek 集成 + 智能上下文管理
# v0.1.0
```

### 2. 检查文件状态

```bash
# 查看已提交的文件
git status

# 应该显示: nothing to commit, working tree clean
```

---

## 🚀 推送到 GitHub

### 方法 1: 推送到新仓库（推荐）

#### Step 1: 在 GitHub 创建新仓库

1. 访问 https://github.com/new
2. 仓库名称: `agentic-ai-public` 或 `ai-research-assistant`
3. 描述: `AI Research Assistant with DeepSeek Integration`
4. 选择 Public 或 Private
5. **不要**初始化 README、.gitignore 或 license
6. 点击 "Create repository"

#### Step 2: 添加远程仓库

```bash
# 添加 GitHub 远程仓库（替换为你的用户名）
git remote add origin https://github.com/YOUR_USERNAME/agentic-ai-public.git

# 或使用 SSH（如果已配置 SSH key）
git remote add origin git@github.com:YOUR_USERNAME/agentic-ai-public.git

# 验证远程仓库
git remote -v
```

#### Step 3: 推送代码和标签

```bash
# 推送主分支
git push -u origin main

# 推送标签
git push origin v0.1.0

# 或一次性推送所有标签
git push origin --tags
```

### 方法 2: 推送到现有仓库

如果你已经有一个 GitHub 仓库：

```bash
# 查看现有远程仓库
git remote -v

# 如果没有，添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 推送（可能需要 force，如果有冲突）
git push -u origin main --force

# 推送标签
git push origin v0.1.0
```

---

## 📝 创建 GitHub Release

### 在 GitHub 网页上创建 Release

1. 访问你的仓库页面
2. 点击右侧的 "Releases"
3. 点击 "Create a new release"
4. 填写以下信息：

**Tag version**: `v0.1.0`

**Release title**: `v0.1.0 - DeepSeek 集成 + 智能上下文管理`

**Description**: 复制以下内容

```markdown
## 🎉 首个正式版本发布

这是 AI Research Assistant 的首个正式版本，实现了 DeepSeek API 集成和智能上下文管理系统。

### ✨ 主要功能

- **DeepSeek API 集成**: 成本节省约 45%
- **智能上下文管理**: 支持任意长度文本处理
- **模型适配层**: 自动参数验证和调整
- **分块处理系统**: 智能语义分块和合并
- **成本追踪**: 实时记录 API 调用成本
- **智能降级**: 自动切换到备用模型

### 📊 性能指标

- **测试覆盖率**: 83% (64/64 测试通过)
- **成本节省**: 45%
- **可处理文本长度**: 无限制
- **参数错误率**: 0%

### 🚀 快速开始

```bash
git clone https://github.com/YOUR_USERNAME/agentic-ai-public.git
cd agentic-ai-public
git checkout v0.1.0
cp .env.example .env
# 编辑 .env 填入 API Keys
docker build -t ai-research-assistant .
docker run --rm -it -p 8000:8000 --env-file .env ai-research-assistant
```

### 📚 文档

- [README](README.md)
- [发布说明](RELEASE_NOTES_v0.1.0.md)
- [Phase 1.5 实施报告](.kiro/specs/context-length-optimization/phase1.5_implementation_report.md)

### 🐛 已知限制

- Token 估算使用启发式方法（计划集成 tiktoken）
- 分块处理为串行（计划实现并行处理）

### 🔮 下一步

- Phase 2: 摘要压缩（减少 50%+ token 使用）
- Phase 3: API 标准化
- Phase 4: 生产部署

**完整的变更详情请查看 [RELEASE_NOTES_v0.1.0.md](RELEASE_NOTES_v0.1.0.md)**
```

5. 选择 "Set as the latest release"
6. 点击 "Publish release"

---

## 🔐 使用 Personal Access Token（如果需要）

如果推送时要求输入密码，GitHub 现在需要使用 Personal Access Token：

### 创建 Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 名称: `AI Research Assistant`
4. 勾选权限: `repo` (完整的仓库访问权限)
5. 点击 "Generate token"
6. **复制 token**（只显示一次！）

### 使用 Token

```bash
# 推送时使用 token 作为密码
git push -u origin main
# Username: YOUR_USERNAME
# Password: ghp_YOUR_TOKEN_HERE

# 或者配置 credential helper 保存 token
git config --global credential.helper store
git push -u origin main
# 输入一次后会保存
```

---

## ✅ 验证推送成功

### 1. 检查 GitHub 仓库

访问 `https://github.com/YOUR_USERNAME/agentic-ai-public`

应该看到：
- ✅ 所有文件已上传
- ✅ README.md 正确显示
- ✅ 提交历史完整
- ✅ 标签 v0.1.0 存在

### 2. 检查 Release

访问 `https://github.com/YOUR_USERNAME/agentic-ai-public/releases`

应该看到：
- ✅ v0.1.0 Release
- ✅ 发布说明完整
- ✅ 标记为 "Latest"

### 3. 克隆测试

```bash
# 在另一个目录测试克隆
cd /tmp
git clone https://github.com/YOUR_USERNAME/agentic-ai-public.git
cd agentic-ai-public
git tag -l
# 应该看到 v0.1.0
```

---

## 🎯 推送检查清单

在推送前确认：

- [ ] 所有测试通过（64/64）
- [ ] README.md 已更新
- [ ] RELEASE_NOTES_v0.1.0.md 已创建
- [ ] Git 提交信息清晰
- [ ] 标签 v0.1.0 已创建
- [ ] .env 文件未包含在提交中
- [ ] 敏感信息已移除

推送后确认：

- [ ] GitHub 仓库可访问
- [ ] 所有文件已上传
- [ ] README 正确显示
- [ ] Release 已创建
- [ ] 标签可见
- [ ] 克隆测试成功

---

## 🐛 常见问题

### 问题 1: 推送被拒绝

```bash
# 错误: ! [rejected] main -> main (fetch first)
```

**解决方案**:
```bash
# 如果确定本地版本正确，强制推送
git push -u origin main --force

# 或者先拉取再推送
git pull origin main --rebase
git push -u origin main
```

### 问题 2: 认证失败

```bash
# 错误: Authentication failed
```

**解决方案**:
- 使用 Personal Access Token 而非密码
- 检查 token 权限是否包含 `repo`
- 确认用户名正确

### 问题 3: 标签已存在

```bash
# 错误: tag 'v0.1.0' already exists
```

**解决方案**:
```bash
# 删除本地标签
git tag -d v0.1.0

# 删除远程标签
git push origin :refs/tags/v0.1.0

# 重新创建并推送
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

### 问题 4: 文件太大

```bash
# 错误: file size exceeds GitHub's file size limit
```

**解决方案**:
```bash
# 检查大文件
find . -type f -size +50M

# 添加到 .gitignore
echo "large_file.bin" >> .gitignore

# 从历史中移除（如果已提交）
git filter-branch --tree-filter 'rm -f large_file.bin' HEAD
```

---

## 📞 需要帮助？

如果遇到问题：

1. 查看 GitHub 文档: https://docs.github.com/
2. 检查 Git 状态: `git status`
3. 查看 Git 日志: `git log --oneline`
4. 检查远程仓库: `git remote -v`

---

## 🎉 完成！

推送成功后，你的 v0.1.0 版本就正式发布了！

下一步：
1. 分享你的仓库链接
2. 邀请其他人测试
3. 收集反馈
4. 开始 Phase 2 开发

**祝贺你完成了 v0.1.0 的发布！** 🚀
