# 博客文章配图 - Mermaid 图表

本文件包含博客文章中使用的所有图表的 Mermaid 代码。

---

## 1. 问题演进图

**用途**: 展示从表层问题到根本原因的分析过程

```mermaid
graph TD
    A[简单的参数错误<br/>max_tokens=15000] -->|深入分析| B[模型适配缺失<br/>没有参数验证]
    B -->|继续深入| C[上下文管理缺失<br/>无法处理长文本]
    C -->|根本原因| D[架构设计问题<br/>Agent 直连 API]
    
    style A fill:#ffcccc
    style B fill:#ffddaa
    style C fill:#ffffaa
    style D fill:#ffaaaa
```

---

## 2. 当前架构 vs 目标架构对比

**用途**: 对比 Phase 1 和 Phase 1.5 的架构差异

```mermaid
graph LR
    subgraph "Before (Phase 1)"
        A1[Agent] -->|直接调用| A2[API]
        A2 --> A3[模型]
    end
    
    subgraph "After (Phase 1.5)"
        B1[Agent] --> B2[ModelAdapter<br/>参数验证/调整]
        B2 --> B3[ContextManager<br/>分块/合并]
        B3 --> B4[API]
        B4 --> B5[模型]
    end
    
    style A1 fill:#ffcccc
    style B1 fill:#ccffcc
    style B2 fill:#ccffcc
    style B3 fill:#ccffcc
```

---

## 3. 数据流分析图

**用途**: 展示数据在 Agent 间的传递和累积

```mermaid
sequenceDiagram
    participant User as 用户
    participant Planner as Planner Agent
    participant Research as Research Agent
    participant Writer as Writer Agent
    participant Editor as Editor Agent
    
    User->>Planner: 研究主题
    Note over Planner: 生成执行步骤
    
    Planner->>Research: 执行研究
    Note over Research: 收集信息<br/>输出: 20K tokens
    
    Research->>Writer: 传递研究数据
    Note over Writer: 生成草稿<br/>输出: 8K tokens
    
    Writer->>Editor: 传递完整草稿
    Note over Editor: 处理全文<br/>输入: 28K+ tokens
    Note right of Editor: ❌ 超过上下文窗口<br/>❌ max_tokens 错误
```

---

## 4. 三种方案对比雷达图

**用途**: 可视化三种方案的优劣势

```mermaid
graph TD
    subgraph "方案对比维度"
        A[实现难度]
        B[风险程度]
        C[见效速度]
        D[长期价值]
        E[成本投入]
    end
    
    subgraph "分块处理"
        A1[⭐⭐ 简单]
        B1[⭐ 低风险]
        C1[⭐⭐⭐ 快速]
        D1[⭐⭐ 中等]
        E1[⭐ 低成本]
    end
    
    subgraph "摘要压缩"
        A2[⭐⭐⭐ 中等]
        B2[⭐⭐ 中风险]
        C2[⭐⭐ 中等]
        D2[⭐⭐⭐ 较高]
        E2[⭐⭐ 中成本]
    end
    
    subgraph "外部记忆 RAG"
        A3[⭐⭐⭐⭐⭐ 复杂]
        B3[⭐⭐⭐ 高风险]
        C3[⭐ 慢]
        D3[⭐⭐⭐⭐⭐ 最高]
        E3[⭐⭐⭐⭐ 高成本]
    end
```

---

## 5. 分阶段实施路线图

**用途**: 展示渐进式改进的策略

```mermaid
timeline
    title 分阶段实施路线图
    
    section Phase 1
        立即修复 : ModelAdapter
              : 参数验证
              : 自动调整
              : 2-3 天
    
    section Phase 1.5
        分块处理 : ChunkingProcessor
              : 语义分割
              : 上下文保持
              : 3-5 天
    
    section Phase 2
        摘要压缩 : Summarization
              : 结构化提取
              : Token 减少 50%
              : 1-2 周
    
    section Phase 3+
        外部记忆 : RAG 系统
              : 向量数据库
              : 智能检索
              : 3-4 周
```

---

## 6. ModelAdapter 工作流程

**用途**: 展示 ModelAdapter 的参数验证和调整流程

```mermaid
flowchart TD
    Start([Agent 调用 API]) --> Check{检查 max_tokens}
    Check -->|在限制内| Direct[直接调用 API]
    Check -->|超过限制| Adjust[自动调整为模型限制值]
    
    Adjust --> Log[记录警告日志]
    Log --> Try1[第一次尝试]
    
    Try1 -->|成功| Success([返回结果])
    Try1 -->|失败| Retry{是否参数错误?}
    
    Retry -->|是| Halve[max_tokens 减半]
    Retry -->|否| Fallback[降级到备用模型]
    
    Halve --> Try2[第二次尝试]
    Try2 -->|成功| Success
    Try2 -->|失败| Fallback
    
    Fallback --> Try3[使用 OpenAI]
    Try3 --> Success
    
    Direct --> Success
    
    style Start fill:#e1f5ff
    style Success fill:#c8e6c9
    style Adjust fill:#fff9c4
    style Fallback fill:#ffccbc
```

---

## 7. ChunkingProcessor 处理流程

**用途**: 展示分块处理的完整流程

```mermaid
flowchart TD
    Input[输入长文本] --> CheckLen{检查长度}
    CheckLen -->|< 6K tokens| Direct[直接处理]
    CheckLen -->|> 6K tokens| Split[语义分块]
    
    Split --> Chunk1[块 1<br/>+ 前后文]
    Split --> Chunk2[块 2<br/>+ 前后文]
    Split --> Chunk3[块 3<br/>+ 前后文]
    Split --> ChunkN[块 N<br/>+ 前后文]
    
    Chunk1 --> Process1[处理块 1]
    Chunk2 --> Process2[处理块 2]
    Chunk3 --> Process3[处理块 3]
    ChunkN --> ProcessN[处理块 N]
    
    Process1 --> Result1[结果 1]
    Process2 --> Result2[结果 2]
    Process3 --> Result3[结果 3]
    ProcessN --> ResultN[结果 N]
    
    Result1 --> Merge[智能合并]
    Result2 --> Merge
    Result3 --> Merge
    ResultN --> Merge
    
    Direct --> Output[输出结果]
    Merge --> Output
    
    style Input fill:#e1f5ff
    style Output fill:#c8e6c9
    style Split fill:#fff9c4
    style Merge fill:#fff9c4
```

---

## 8. 成本对比柱状图

**用途**: 可视化成本节省效果

```mermaid
graph LR
    subgraph "典型研究任务成本对比"
        A[OpenAI<br/>$0.0238] 
        B[DeepSeek<br/>$0.0129]
        C[节省<br/>45.8%]
    end
    
    style A fill:#ffcccc
    style B fill:#ccffcc
    style C fill:#ffffcc
```

---

## 9. 测试覆盖率进化

**用途**: 展示测试覆盖率的提升

```mermaid
graph LR
    A[Phase 1<br/>22 测试<br/>70% 覆盖率] -->|新增 42 测试| B[Phase 1.5<br/>64 测试<br/>83% 覆盖率]
    
    style A fill:#ffddaa
    style B fill:#ccffcc
```

---

## 10. 错误恢复机制流程

**用途**: 展示增强的降级机制

```mermaid
stateDiagram-v2
    [*] --> 调用API
    调用API --> 检查结果
    
    检查结果 --> 成功: API 调用成功
    检查结果 --> 参数错误: 400 错误
    检查结果 --> 速率限制: 429 错误
    检查结果 --> 模型错误: 500 错误
    
    参数错误 --> 调整参数: max_tokens 减半
    调整参数 --> 重试1: 第 1 次重试
    
    重试1 --> 成功: 成功
    重试1 --> 降级模型: 失败
    
    速率限制 --> 等待重试: 指数退避
    等待重试 --> 重试2: 第 2 次重试
    
    重试2 --> 成功: 成功
    重试2 --> 降级模型: 失败
    
    模型错误 --> 降级模型: 直接降级
    
    降级模型 --> 使用OpenAI: 切换到备用模型
    使用OpenAI --> 成功
    
    成功 --> [*]
```

---

## 11. 上下文管理分层架构

**用途**: 展示未来的分层上下文管理设计

```mermaid
graph TD
    subgraph "短期上下文 (Short-term)"
        A1[最近 3 轮对话]
        A2[直接传递给 LLM]
    end
    
    subgraph "工作上下文 (Working)"
        B1[当前任务关键信息]
        B2[分块/摘要压缩]
    end
    
    subgraph "长期上下文 (Long-term)"
        C1[历史信息和知识库]
        C2[RAG 检索]
    end
    
    A1 --> A2
    B1 --> B2
    C1 --> C2
    
    A2 --> LLM[LLM 处理]
    B2 --> LLM
    C2 --> LLM
    
    style A1 fill:#e3f2fd
    style B1 fill:#fff9c4
    style C1 fill:#f3e5f5
    style LLM fill:#c8e6c9
```

---

## 12. 处理时间对比

**用途**: 展示不同文本长度的处理时间开销

```mermaid
graph TD
    subgraph "短文本 < 6K tokens"
        A1[直接处理]
        A2[时间开销: 0%]
        A3[API 调用: 1 次]
    end
    
    subgraph "中等文本 6K-20K tokens"
        B1[分块处理 2-3 块]
        B2[时间开销: 20-30%]
        B3[API 调用: 2-3 次]
    end
    
    subgraph "长文本 > 20K tokens"
        C1[分块处理 4+ 块]
        C2[时间开销: 40-50%]
        C3[API 调用: 4+ 次]
    end
    
    style A1 fill:#c8e6c9
    style B1 fill:#fff9c4
    style C1 fill:#ffccbc
```

---

## 使用说明

### 在 Markdown 中使用

直接将 Mermaid 代码块复制到 Markdown 文件中：

\`\`\`mermaid
[Mermaid 代码]
\`\`\`

### 生成 SVG 图片

使用 Mermaid CLI 或在线工具：

1. **Mermaid Live Editor**: https://mermaid.live/
2. **Mermaid CLI**:
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   mmdc -i diagram.mmd -o diagram.svg
   ```

### 支持的平台

- GitHub (原生支持)
- GitLab (原生支持)
- 掘金 (支持)
- 知乎 (需要转换为图片)
- CSDN (需要转换为图片)

---

**创建日期**: 2025-10-31  
**维护者**: AI Research Assistant Team
