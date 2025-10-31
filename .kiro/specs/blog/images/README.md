# 博客图表资源

本目录包含博客文章所需的 SVG 图表文件。

## 图表列表

### 1. 问题演进图 (problem-evolution.svg)
展示从表层问题到根本原因的分析过程：
- 表层问题：max_tokens 超限
- 参数管理问题
- 上下文管理缺失
- 根本原因：架构设计问题

**使用位置**：第二章节 "问题分析：从表象到本质"

### 2. 架构演进对比图 (architecture-evolution.svg)
对比 Before 和 After 的架构设计：
- Before: Agent 直连 API
- After: 引入 ModelAdapter 和 ContextManager

**使用位置**：第三章节 "解决方案设计"

### 3. 分阶段实施路线图 (phased-implementation-roadmap.svg)
展示三个阶段的实施计划：
- Phase 1: 止血求生（2-3天）
- Phase 2: 强身健体（1-2周）
- Phase 3+: 终极进化（3-4周）

**使用位置**：第四章节 "实施路线图"

## 在 Markdown 中使用

### 方式 1：直接嵌入 SVG（推荐）
```markdown
![问题演进图](images/problem-evolution.svg)
```

### 方式 2：使用 HTML img 标签
```html
<img src="images/problem-evolution.svg" alt="问题演进图" width="800">
```

### 方式 3：在支持的平台上直接显示
某些 Markdown 渲染器支持直接显示 SVG 内容。

## Mermaid 图表

如果你的博客平台支持 Mermaid，可以使用 `docs/blog/diagrams/mermaid/` 目录下的 `.mmd` 文件。

参考 `docs/blog/diagrams/insertion-guide.md` 了解详细的插入指南。

## 生成图片格式

如果需要 PNG 格式，可以使用以下工具转换：

### 使用 Inkscape（命令行）
```bash
inkscape problem-evolution.svg --export-png=problem-evolution.png --export-width=1600
```

### 使用在线工具
- https://cloudconvert.com/svg-to-png
- https://svgtopng.com/

### 使用 Node.js 脚本
参考 `docs/blog/diagrams/generate-images.sh` 脚本。
