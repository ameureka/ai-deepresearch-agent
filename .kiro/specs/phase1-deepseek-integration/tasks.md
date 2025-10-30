# Phase 1: DeepSeek API 集成 - 任务清单

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 1 - DeepSeek API 集成
- **版本**: 1.1
- **创建日期**: 2025-10-30
- **最后更新**: 2025-10-30
- **预计时间**: 1.5-2 天（12-16 小时）
- **状态**: 待执行

---

## 任务概览

本阶段包含 **40 个任务**，分为 **6 个主要模块**：

1. **环境准备** (4 个任务，2 小时)
2. **配置管理** (6 个任务，3 小时)
3. **成本追踪** (5 个任务，2.5 小时)
4. **代理集成** (12 个任务，8 小时)
5. **测试验证** (10 个任务，6 小时)
6. **文档和部署** (3 个任务，2.5 小时)

**标记说明**:
- `[ ]` 未完成
- `[x]` 已完成
- `*` 可选任务（文档编写）

---

## 实施任务

### 模块 1: 环境准备（2 小时）

#### - [ ] 1.1 申请 DeepSeek API Key
- 访问 https://platform.deepseek.com/
- 注册账号并申请 API Key
- 验证 API Key 格式（sk- 前缀）
- 保存到安全位置
- _需求: Requirement 1_
- _预计时间: 15 分钟_

#### - [ ] 1.2 验证 aisuite 版本
- 检查当前 aisuite 版本: `pip show aisuite`
- 如果版本 < 0.1.12，升级: `pip install --upgrade aisuite`
- 验证 DeepSeek provider 存在
- 测试基础导入: `from aisuite.providers import deepseek_provider`
- _需求: Requirement 2_
- _预计时间: 15 分钟_

#### - [ ] 1.3 配置环境变量
- 复制 `.env.example` 到 `.env`
- 添加 `DEEPSEEK_API_KEY=your-key-here`
- 验证其他必需的环境变量（OPENAI_API_KEY, TAVILY_API_KEY）
- 更新 `.gitignore` 确保 `.env` 不被提交
- _需求: Requirement 1_
- _预计时间: 10 分钟_

#### - [ ] 1.4 修复现有代码问题
- 修复 `src/agents.py` 中的模型名称: `gpt-4.1-mini` → `gpt-4o-mini`
- 修复 `src/planning_agent.py` 中的模型名称: `o4-mini` → `o1-mini`
- 验证修复: `python -c "from src.agents import research_agent"`
- 验证修复: `python -c "from src.planning_agent import planner_agent"`
- _需求: Requirement 2_
- _预计时间: 20 分钟_

---

### 模块 2: 配置管理（3 小时）

#### - [ ] 2.1 创建 ModelConfig 类
- 创建文件 `src/config.py`
- 实现 `ModelConfig` 类
- 定义类属性: PLANNER_MODEL, RESEARCHER_MODEL, WRITER_MODEL, EDITOR_MODEL
- 从环境变量读取配置，提供默认值
- _需求: Requirement 3_
- _预计时间: 30 分钟_

#### - [ ] 2.2 实现 get_model() 方法
- 实现 `get_model(agent_type: str) -> str` 方法
- 支持的 agent_type: "planner", "researcher", "writer", "editor"
- 返回对应的模型配置
- 添加类型提示和 docstring
- _需求: Requirement 3_
- _预计时间: 15 分钟_

#### - [ ] 2.3 实现 validate() 方法
- 实现 `validate() -> bool` 方法
- 检查必需的环境变量: DEEPSEEK_API_KEY, OPENAI_API_KEY
- 验证 API Key 格式（sk- 前缀）
- 失败时抛出 ValueError 并提供清晰的错误信息
- _需求: Requirement 15_
- _预计时间: 20 分钟_

#### - [ ] 2.4 更新 .env.example
- 添加所有模型配置的示例
- 添加注释说明每个配置的用途
- 提供推荐的配置值
- 添加可选配置（REQUEST_TIMEOUT, FALLBACK_MODEL）
- _需求: Requirement 3_
- _预计时间: 15 分钟_

#### - [ ] 2.5 编写配置单元测试
- 创建 `tests/test_config.py`
- 测试默认值加载
- 测试环境变量覆盖
- 测试 get_model() 方法
- 测试 validate() 方法
- _需求: Requirement 15_
- _预计时间: 45 分钟_

#### - [ ] 2.6 创建配置验证脚本
- 创建 `scripts/check_config.py`
- 验证所有必需的环境变量
- 测试 API Key 有效性（可选）
- 输出清晰的验证结果
- 提供修复建议
- _需求: Requirement 15_
- _预计时间: 30 分钟_

---

### 模块 3: 成本追踪（2.5 小时）

#### - [ ] 3.1 创建 CostTracker 类
- 创建文件 `src/cost_tracker.py`
- 实现 `CostTracker` 类
- 定义价格表 PRICES
- 初始化成本、调用次数、token 统计
- _需求: Requirement 8_
- _预计时间: 30 分钟_

#### - [ ] 3.2 实现 track() 方法
- 实现 `track(model, input_tokens, output_tokens) -> float` 方法
- 根据价格表计算成本
- 累计统计数据
- 记录日志
- 返回本次调用成本
- _需求: Requirement 8_
- _预计时间: 30 分钟_

#### - [ ] 3.3 实现 summary() 方法
- 实现 `summary() -> Dict` 方法
- 生成成本摘要报告
- 按模型分组统计
- 计算总成本和总调用次数
- 格式化输出
- _需求: Requirement 8, 14_
- _预计时间: 20 分钟_

#### - [ ] 3.4 实现 compare() 方法
- 实现 `compare(baseline) -> Dict` 方法
- 对比当前成本与基准成本
- 计算节省百分比
- 生成对比报告
- _需求: Requirement 14_
- _预计时间: 20 分钟_

#### - [ ] 3.5 编写成本追踪单元测试
- 创建 `tests/test_cost_tracker.py`
- 测试成本计算准确性
- 测试累计统计
- 测试摘要生成
- 测试对比功能
- _需求: Requirement 8, 14_
- _预计时间: 45 分钟_

---

### 模块 4: 代理集成（8 小时）

#### - [ ] 4.1 更新 Research Agent 使用 DeepSeek
- 修改 `src/agents.py` 中的 `research_agent()` 函数
- 添加 `model` 参数（默认 None）
- 如果 model 为 None，使用 `ModelConfig.RESEARCHER_MODEL`
- 保持其他逻辑不变
- _需求: Requirement 4_
- _预计时间: 30 分钟_

#### - [ ] 4.2 集成成本追踪到 Research Agent
- 在 `research_agent()` 中导入 `tracker`
- 在 API 调用后记录成本: `tracker.track(model, input_tokens, output_tokens)`
- 验证 token 使用信息可用: `resp.usage`
- 添加日志输出
- _需求: Requirement 4, 8_
- _预计时间: 20 分钟_

#### - [ ] 4.3 测试 Research Agent 工具调用
- 创建测试脚本 `tests/test_research_deepseek.py`
- 测试 Tavily 搜索工具调用
- 测试 arXiv 搜索工具调用
- 测试 Wikipedia 查询工具调用
- 验证工具调用格式兼容性
- _需求: Requirement 4, 10_
- _预计时间: 1 小时_

#### - [ ] 4.4 更新 Editor Agent 使用 DeepSeek
- 修改 `src/agents.py` 中的 `editor_agent()` 函数
- 添加 `model` 参数（默认 None）
- 如果 model 为 None，使用 `ModelConfig.EDITOR_MODEL`
- 保持其他逻辑不变
- _需求: Requirement 5_
- _预计时间: 30 分钟_

#### - [ ] 4.5 集成成本追踪到 Editor Agent
- 在 `editor_agent()` 中导入 `tracker`
- 在 API 调用后记录成本
- 添加日志输出
- _需求: Requirement 5, 8_
- _预计时间: 15 分钟_

#### - [ ] 4.6 更新 Writer Agent 使用 DeepSeek
- 修改 `src/agents.py` 中的 `writer_agent()` 函数
- 添加 `model` 参数（默认 None）
- 如果 model 为 None，使用 `ModelConfig.WRITER_MODEL` (deepseek:deepseek-chat)
- 集成成本追踪
- 保持其他逻辑不变
- _需求: Requirement 6_
- _预计时间: 30 分钟_

#### - [ ] 4.7 更新 Planner Agent 使用 DeepSeek
- 修改 `src/planning_agent.py` 中的 `planner_agent()` 函数
- 添加 `model` 参数（默认 None）
- 如果 model 为 None，使用 `ModelConfig.PLANNER_MODEL` (deepseek:deepseek-reasoner)
- 集成成本追踪
- 保持其他逻辑不变
- _需求: Requirement 7_
- _预计时间: 30 分钟_

#### - [ ] 4.8 实现降级机制装饰器
- 创建 `src/fallback.py`
- 实现 `with_fallback()` 装饰器
- 捕获 API 错误并降级
- 记录降级事件到日志
- _需求: Requirement 9_
- _预计时间: 45 分钟_

#### - [ ] 4.9 应用降级机制到所有 Agent
- 使用 `@with_fallback` 装饰所有 Agent 函数
- Research Agent: 降级到 `ModelConfig.FALLBACK_MODEL`
- Editor Agent: 降级到 `ModelConfig.FALLBACK_MODEL`
- Writer Agent: 降级到 `ModelConfig.FALLBACK_MODEL`
- Planner Agent: 降级到 `ModelConfig.FALLBACK_MODEL`
- _需求: Requirement 9_
- _预计时间: 30 分钟_

#### - [ ] 4.10 测试降级机制
- 模拟 DeepSeek API 失败
- 测试所有 Agent 的降级触发
- 验证降级后任务继续执行
- 验证降级日志记录
- _需求: Requirement 9_
- _预计时间: 20 分钟_

#### - [ ] 4.11 实现错误处理
- 在所有代理中添加统一的错误处理
- 处理 401 (Invalid API Key)
- 处理 429 (Rate Limit)
- 处理 500 (Server Error)
- 处理 Timeout
- _需求: Requirement 11_
- _预计时间: 1 小时_

#### - [ ] 4.12 编写代理集成单元测试
- 创建 `tests/test_agents_integration.py`
- 测试所有代理的模型配置
- 测试成本追踪集成
- 测试降级机制
- 测试错误处理
- _需求: Requirement 4, 5, 6, 7, 9, 11_
- _预计时间: 1.5 小时_

---

### 模块 5: 测试验证（6 小时）

#### - [ ] 5.1 创建兼容性测试脚本
- 创建 `tests/test_deepseek_compatibility.py`
- 测试 OpenAI SDK + DeepSeek 基础连接
- 测试 aisuite + DeepSeek 工具调用
- 测试当前项目工具格式兼容性
- _需求: Requirement 2, 10_
- _预计时间: 1 小时_

#### - [ ] 5.2 执行完整研究流程测试
- 创建测试脚本 `tests/test_full_research_flow.py`
- 测试: 规划 → 研究 → 写作 → 编辑
- 验证所有 Agent 都使用 DeepSeek
- 验证 Planner 使用 deepseek-reasoner
- 验证其他 Agent 使用 deepseek-chat
- 验证工具调用正常
- 验证成本追踪正常
- _需求: Requirement 4, 5, 6, 7, 8, 10_
- _预计时间: 1.5 小时_

#### - [ ] 5.3 执行降级场景测试
- 创建测试脚本 `tests/test_fallback_scenarios.py`
- 模拟 DeepSeek API 失败
- 验证自动降级到 OpenAI
- 验证任务继续执行
- 验证降级日志记录
- _需求: Requirement 9_
- _预计时间: 45 分钟_

#### - [ ] 5.4 执行成本对比测试
- 创建测试脚本 `tests/test_cost_comparison.py`
- 同一任务分别使用 DeepSeek 和 OpenAI
- 对比成本和质量
- 验证成本节省 >= 40%（目标 ~45%）
- 生成对比报告
- _需求: Requirement 14_
- _预计时间: 1 小时_

#### - [ ] 5.5 执行性能测试
- 创建测试脚本 `tests/test_performance.py`
- 测试 Research Agent 响应时间 < 150s
- 测试 Editor Agent 响应时间 < 90s
- 测试并发能力（5 个任务）
- 测试内存使用 <= 110% OpenAI
- _需求: Requirement 12_
- _预计时间: 1 小时_

#### - [ ] 5.6 执行质量测试
- 创建测试脚本 `tests/test_quality.py`
- 选择 10 个测试主题
- 对比 DeepSeek 和 OpenAI 输出
- 评估: 结构完整性、引用准确性、内容连贯性
- 验证质量 >= 85%
- _需求: Requirement 13_
- _预计时间: 2 小时_

#### - [ ] 5.7 运行所有单元测试
- 执行: `pytest tests/ -v --cov=src --cov-report=html`
- 验证测试覆盖率 >= 80%
- 修复失败的测试
- 生成覆盖率报告
- _需求: NFR 2_
- _预计时间: 30 分钟_

#### - [ ] 5.8 执行配置验证测试
- 运行配置验证脚本: `python scripts/check_config.py`
- 验证所有必需的环境变量
- 验证 API Key 有效性
- 验证 aisuite 版本
- _需求: Requirement 15_
- _预计时间: 15 分钟_

#### - [ ] 5.9 执行错误处理测试
- 创建测试脚本 `tests/test_error_handling.py`
- 测试各种错误场景（401, 429, 500, Timeout）
- 验证错误处理逻辑
- 验证错误日志记录
- _需求: Requirement 11_
- _预计时间: 45 分钟_

#### - [ ] 5.10 生成测试报告
- 汇总所有测试结果
- 生成测试报告: `reports/phase1_test_report.md`
- 包含: 测试覆盖率、性能指标、质量评估、成本对比
- 标记通过/失败的测试
- _需求: All Requirements_
- _预计时间: 30 分钟_

---

### 模块 6: 文档和部署（2.5 小时）

#### - [ ]* 6.1 更新 README 文档
- 更新项目 README.md
- 添加 DeepSeek 集成说明
- 添加配置指南
- 添加成本优化说明
- 添加故障排查指南
- _需求: NFR 1_
- _预计时间: 1 小时_

#### - [ ]* 6.2 创建 API 文档
- 使用 FastAPI 自动生成 API 文档
- 添加配置说明
- 添加使用示例
- 添加常见问题 FAQ
- _需求: NFR 1_
- _预计时间: 45 分钟_

#### - [ ]* 6.3 创建部署检查清单
- 创建 `docs/deployment_checklist.md`
- 列出所有部署前检查项
- 包含环境变量配置
- 包含依赖安装
- 包含测试验证
- _需求: NFR 1_
- _预计时间: 30 分钟_

---

## 验收标准

### 功能验收

- [ ] 所有 15 个需求的验收标准都已满足
- [ ] DeepSeek API 调用成功
- [ ] 工具调用（Tavily、arXiv、Wikipedia）正常
- [ ] 成本追踪正常工作
- [ ] 降级机制正常工作
- [ ] 配置验证脚本通过

### 质量验收

- [ ] 单元测试覆盖率 >= 80%
- [ ] 所有集成测试通过
- [ ] 成本降低 >= 40%（目标 ~45%）
- [ ] 输出质量 >= 85%（相比 OpenAI）
- [ ] 性能满足要求（响应时间 <= 150% OpenAI）
- [ ] 所有 4 个 Agent 都使用 DeepSeek 模型

### 文档验收

- [ ] README 更新完整
- [ ] API 文档生成
- [ ] 部署检查清单完整
- [ ] 测试报告生成

---

## 时间估算

| 模块 | 任务数 | 预计时间 |
|------|--------|----------|
| 环境准备 | 4 | 1 小时 |
| 配置管理 | 6 | 2 小时 |
| 成本追踪 | 5 | 1.5 小时 |
| 代理集成 | 12 | 4 小时 |
| 测试验证 | 10 | 3 小时 |
| 文档和部署 | 3 | 1.5 小时 |
| **总计** | **40** | **13 小时** |

**实际工作日**: 1.5-2 天（每天 6-8 小时）

**说明**: 
- 最快完成时间: 12 小时（有经验的开发者）
- 推荐完成时间: 13-16 小时（包含充分测试和文档）
- 最长完成时间: 18 小时（新手开发者）

---

## 依赖关系

```
环境准备 (1.1-1.4)
    ↓
配置管理 (2.1-2.6)
    ↓
成本追踪 (3.1-3.5)
    ↓
代理集成 (4.1-4.12)
    ↓
测试验证 (5.1-5.10)
    ↓
文档和部署 (6.1-6.3)
```

---

## 风险和缓解

### 高风险

1. **DeepSeek API Key 获取困难**
   - 缓解: 立即申请，准备备用账号

2. **工具调用格式差异**
   - 缓解: 已验证 100% 兼容，风险已消除

### 中风险

3. **输出质量下降**
   - 缓解: 充分测试质量，如不满足可调整策略
   - 缓解: 实现降级机制，确保服务可用性

4. **速率限制**
   - 缓解: 充值少量费用，控制测试频率
   - 缓解: 实现重试机制

---

## 下一步行动

### 立即开始（Day 1 上午）

1. ✅ 申请 DeepSeek API Key (任务 1.1)
2. ✅ 验证 aisuite 版本 (任务 1.2)
3. ✅ 配置环境变量 (任务 1.3)
4. ✅ 修复现有代码问题 (任务 1.4)

### Day 1 下午

5. ✅ 创建 ModelConfig 类 (任务 2.1-2.4)
6. ✅ 创建 CostTracker 类 (任务 3.1-3.4)

### Day 1 下午 - Day 2 上午

7. ✅ 更新所有代理 (任务 4.1-4.12)
8. ✅ 编写单元测试 (任务 2.5, 3.5, 4.12)

### Day 2 下午

9. ✅ 执行所有测试 (任务 5.1-5.10)
10. ✅ 生成文档 (任务 6.1-6.3)

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待执行
