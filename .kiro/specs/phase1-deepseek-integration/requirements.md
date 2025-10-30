# Phase 1: DeepSeek API 集成 - 需求文档

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 1 - DeepSeek API 集成
- **版本**: 1.0
- **创建日期**: 2025-10-30
- **状态**: 待实施

---

## 简介

本文档定义了 Phase 1（DeepSeek API 集成）的功能需求。该阶段的目标是在现有 FastAPI 研究系统中集成 DeepSeek API，以降低运营成本 30-40%，同时保持功能完整性和输出质量。

---

## 术语表

- **System**: FastAPI 研究助手后端系统
- **DeepSeek API**: DeepSeek 提供的大语言模型 API 服务
- **aisuite**: 统一的多模型调用框架
- **Research Agent**: 执行信息检索和学术研究的代理
- **Writer Agent**: 根据研究材料撰写学术报告的代理
- **Editor Agent**: 审阅和改进学术文稿的代理
- **Planner Agent**: 为研究主题生成结构化执行步骤的代理
- **Tool Calling**: 模型调用外部工具（如 Tavily、arXiv）的能力
- **Cost Tracker**: 成本追踪模块
- **Fallback Mechanism**: 降级机制，当主模型失败时切换到备用模型

---

## 需求

### Requirement 1: DeepSeek API 配置

**用户故事**: 作为系统管理员，我希望能够配置 DeepSeek API 密钥，以便系统可以调用 DeepSeek 服务

#### 验收标准

1. WHEN System 启动时，THE System SHALL 从环境变量读取 DEEPSEEK_API_KEY
2. IF DEEPSEEK_API_KEY 不存在，THEN THE System SHALL 记录警告日志并继续运行
3. THE System SHALL 验证 DEEPSEEK_API_KEY 格式符合 "sk-" 前缀规范
4. THE System SHALL 支持通过 .env 文件配置 DEEPSEEK_API_KEY
5. THE System SHALL 不在日志中输出完整的 API Key 值

### Requirement 2: aisuite 框架集成

**用户故事**: 作为开发者，我希望系统使用 aisuite 框架调用 DeepSeek API，以便保持与 OpenAI 的兼容性

#### 验收标准

1. THE System SHALL 使用 aisuite 版本 >= 0.1.12
2. THE System SHALL 通过 aisuite 的统一接口调用 DeepSeek 模型
3. WHEN 调用 DeepSeek 模型时，THE System SHALL 使用格式 "deepseek:deepseek-chat"
4. THE System SHALL 支持 DeepSeek 的所有标准参数（temperature, max_tokens, tools）
5. THE System SHALL 保持与 OpenAI 调用方式的一致性

### Requirement 3: 模型配置管理

**用户故事**: 作为系统管理员，我希望能够灵活配置不同代理使用的模型，以便平衡成本和质量

#### 验收标准

1. THE System SHALL 提供统一的模型配置类 ModelConfig
2. THE System SHALL 支持通过环境变量配置以下模型：
   - PLANNER_MODEL（默认: openai:o1-mini）
   - RESEARCHER_MODEL（默认: deepseek:deepseek-chat）
   - WRITER_MODEL（默认: openai:gpt-4o-mini）
   - EDITOR_MODEL（默认: deepseek:deepseek-chat）
3. WHEN 环境变量未设置时，THE System SHALL 使用默认模型配置
4. THE System SHALL 提供 get_model(agent_type) 方法获取指定代理的模型
5. THE System SHALL 提供 validate() 方法验证必需的 API Key 是否配置

### Requirement 4: Research Agent DeepSeek 集成

**用户故事**: 作为研究用户，我希望研究代理使用 DeepSeek 模型，以便降低研究成本

#### 验收标准

1. THE Research Agent SHALL 默认使用 deepseek:deepseek-chat 模型
2. WHEN Research Agent 调用 DeepSeek 时，THE System SHALL 支持工具调用（Tavily、arXiv、Wikipedia）
3. THE Research Agent SHALL 保持与 OpenAI 版本相同的输出格式
4. THE Research Agent SHALL 支持通过参数覆盖默认模型
5. WHEN 工具调用失败时，THE System SHALL 记录错误并继续执行

### Requirement 5: Editor Agent DeepSeek 集成

**用户故事**: 作为研究用户，我希望编辑代理使用 DeepSeek 模型，以便降低编辑成本

#### 验收标准

1. THE Editor Agent SHALL 默认使用 deepseek:deepseek-chat 模型
2. THE Editor Agent SHALL 保持与 OpenAI 版本相同的编辑质量标准
3. THE Editor Agent SHALL 支持通过参数覆盖默认模型
4. THE Editor Agent SHALL 正确处理中文和英文内容
5. THE Editor Agent SHALL 在 90 秒内完成编辑任务

### Requirement 6: Writer Agent 保持 OpenAI

**用户故事**: 作为研究用户，我希望写作代理继续使用 OpenAI 模型，以便保证报告质量

#### 验收标准

1. THE Writer Agent SHALL 默认使用 openai:gpt-4o-mini 模型
2. THE Writer Agent SHALL 生成结构完整的学术报告
3. THE Writer Agent SHALL 支持最少 2400 字的报告生成
4. THE Writer Agent SHALL 保持现有的输出质量标准
5. THE Writer Agent SHALL 支持通过参数切换到 DeepSeek（用于测试）

### Requirement 7: Planner Agent 保持 OpenAI

**用户故事**: 作为研究用户，我希望规划代理继续使用 OpenAI o1-mini 模型，以便保证规划质量

#### 验收标准

1. THE Planner Agent SHALL 默认使用 openai:o1-mini 模型
2. THE Planner Agent SHALL 生成 3-8 个结构化的研究步骤
3. THE Planner Agent SHALL 每个步骤包含明确的执行指令
4. THE Planner Agent SHALL 保持现有的规划质量标准
5. THE Planner Agent SHALL 支持通过参数切换到 DeepSeek Reasoner（用于测试）

### Requirement 8: 成本追踪

**用户故事**: 作为系统管理员，我希望系统能够追踪 API 调用成本，以便监控和优化支出

#### 验收标准

1. THE System SHALL 提供 CostTracker 类追踪所有 API 调用成本
2. WHEN API 调用完成时，THE System SHALL 记录 input_tokens 和 output_tokens
3. THE System SHALL 根据模型价格表计算每次调用的成本
4. THE System SHALL 累计每个模型的总成本和调用次数
5. THE System SHALL 提供 summary() 方法输出成本摘要报告
6. THE System SHALL 在日志中记录每次调用的成本信息

### Requirement 9: 降级机制

**用户故事**: 作为系统管理员，我希望当 DeepSeek 调用失败时系统能够自动降级到 OpenAI，以便保证服务可用性

#### 验收标准

1. WHEN DeepSeek API 调用失败时，THE System SHALL 自动切换到 OpenAI 模型
2. THE System SHALL 记录降级事件到日志
3. THE System SHALL 在降级后继续正常执行任务
4. THE System SHALL 支持配置降级模型（默认: openai:gpt-4o-mini）
5. THE System SHALL 在降级后的响应中标记使用了降级模型

### Requirement 10: 工具调用兼容性

**用户故事**: 作为开发者，我希望 DeepSeek 模型能够正确调用外部工具，以便保持研究功能完整

#### 验收标准

1. THE System SHALL 支持 DeepSeek 调用 Tavily 搜索工具
2. THE System SHALL 支持 DeepSeek 调用 arXiv 学术搜索工具
3. THE System SHALL 支持 DeepSeek 调用 Wikipedia 查询工具
4. THE System SHALL 保持工具调用格式与 OpenAI 100% 兼容
5. WHEN 工具调用失败时，THE System SHALL 记录错误并返回友好提示

### Requirement 11: 错误处理

**用户故事**: 作为系统管理员，我希望系统能够优雅地处理 API 错误，以便提供稳定的服务

#### 验收标准

1. WHEN DeepSeek API 返回 401 错误时，THE System SHALL 记录 "Invalid API Key" 错误
2. WHEN DeepSeek API 返回 429 错误时，THE System SHALL 记录 "Rate Limit Exceeded" 错误
3. WHEN DeepSeek API 返回 500 错误时，THE System SHALL 记录 "Server Error" 并触发降级
4. WHEN 网络超时时，THE System SHALL 在 90 秒后返回超时错误
5. THE System SHALL 在所有错误情况下返回结构化的错误响应

### Requirement 12: 性能要求

**用户故事**: 作为研究用户，我希望系统响应时间不会因为切换到 DeepSeek 而显著增加

#### 验收标准

1. THE Research Agent SHALL 在 150 秒内完成单次研究任务
2. THE Editor Agent SHALL 在 90 秒内完成编辑任务
3. THE System SHALL 保持 API 调用响应时间 <= OpenAI 的 150%
4. THE System SHALL 支持并发处理至少 5 个研究任务
5. THE System SHALL 在内存使用上不超过 OpenAI 版本的 110%

### Requirement 13: 质量保证

**用户故事**: 作为研究用户，我希望使用 DeepSeek 后的输出质量不会显著下降

#### 验收标准

1. THE Research Agent SHALL 生成的研究结果质量 >= OpenAI 版本的 85%
2. THE Editor Agent SHALL 编辑后的文稿质量 >= OpenAI 版本的 85%
3. THE System SHALL 保持报告结构完整性（标题、摘要、正文、参考文献）
4. THE System SHALL 保持引用准确性 >= 90%
5. THE System SHALL 保持内容连贯性，无明显逻辑错误

### Requirement 14: 成本节省验证

**用户故事**: 作为系统管理员，我希望能够验证使用 DeepSeek 确实降低了成本

#### 验收标准

1. THE System SHALL 提供成本对比报告功能
2. THE System SHALL 计算使用 DeepSeek 后的实际成本节省百分比
3. THE System SHALL 在测试中验证成本降低 >= 25%
4. THE System SHALL 记录每个代理的成本贡献
5. THE System SHALL 提供月度成本预测功能

### Requirement 15: 配置验证

**用户故事**: 作为开发者，我希望系统能够验证配置的正确性，以便快速发现配置问题

#### 验收标准

1. THE System SHALL 提供配置验证脚本
2. WHEN 配置验证运行时，THE System SHALL 检查所有必需的环境变量
3. WHEN 配置验证运行时，THE System SHALL 测试 API Key 的有效性
4. WHEN 配置验证运行时，THE System SHALL 验证 aisuite 版本 >= 0.1.12
5. WHEN 配置验证失败时，THE System SHALL 输出清晰的错误信息和修复建议

---

## 非功能需求

### NFR 1: 可维护性

- 代码应遵循 PEP 8 Python 编码规范
- 所有公共函数应包含 docstring 文档
- 配置应集中管理，避免硬编码
- 应提供清晰的日志输出

### NFR 2: 可测试性

- 所有核心功能应有单元测试
- 测试覆盖率应 >= 80%
- 应提供集成测试验证完整流程
- 应提供性能测试基准

### NFR 3: 安全性

- API Key 不应在代码中硬编码
- API Key 不应在日志中完整输出
- 应使用环境变量管理敏感信息
- 应验证 API Key 格式

### NFR 4: 兼容性

- 应保持与现有 OpenAI 代码的兼容性
- 应支持 Python 3.11+
- 应支持 aisuite >= 0.1.12
- 应保持 API 接口不变

---

## 依赖关系

### 外部依赖

- aisuite >= 0.1.12
- openai SDK
- DeepSeek API 服务
- Tavily API 服务

### 内部依赖

- 无（Phase 1 是基础阶段）

---

## 验收标准总结

Phase 1 完成的标准：

1. ✅ 所有 15 个需求的验收标准都已满足
2. ✅ 单元测试覆盖率 >= 80%
3. ✅ 集成测试通过
4. ✅ 成本降低 >= 25%
5. ✅ 输出质量 >= 85%（相比 OpenAI）
6. ✅ 性能满足要求（响应时间 <= 150% OpenAI）
7. ✅ 配置验证脚本通过
8. ✅ 文档完整

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待实施
