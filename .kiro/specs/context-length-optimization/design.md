# 上下文长度优化方案 - 设计文档

## 概述

本文档详细描述了智能体系统上下文长度优化的设计方案。基于对当前系统的深入分析，我们提出了一个分阶段的解决方案，从立即修复到长期架构升级。

## 问题分析总结

### 错误现象

在 Phase 1 DeepSeek 集成完成后，系统测试中 Editor Agent 出现以下错误：

```
Error code: 400 - {'error': {'message': 'invalid max_tokens value, 
the valid range of max_tokens is [1, 8192]', 'type': 'invalid_request_error'}}
```

### 根本原因

1. **参数不匹配**: 代码中 `max_tokens=15000` 超过 DeepSeek 限制 (8192)
2. **缺少适配层**: 没有根据模型类型动态调整参数
3. **上下文管理缺失**: 数据直接传递，无压缩或分块机制
4. **架构设计问题**: Agent 直接调用 API，缺少抽象层

### 模型限制对比

| 模型 | max_tokens | Context Window | 说明 |
|------|-----------|----------------|------|
| DeepSeek Chat | 8,192 | 32K | 输出限制严格 |
| DeepSeek Reasoner | 8,192 | 64K | 推理模型 |
| GPT-4o-mini | 16,384 | 128K | OpenAI 标准 |
| GPT-4o | 16,384 | 128K | OpenAI 高级 |
| o1-mini | 65,536 | 128K | 推理模型 |

**关键发现**: DeepSeek 的 max_tokens 限制是 OpenAI 的一半

## 架构设计

### 当前架构问题

```
当前流程:
Agent → 直接调用 API → 模型
  ↓
问题: 无参数验证、无上下文管理、无错误恢复
```

### 目标架构

```
优化后流程:
Agent → 模型适配层 → 上下文管理器 → API → 模型
         ↓              ↓
    参数验证/调整    分块/压缩/检索
```

## 组件设计

### 1. 模型适配层 (Model Adapter)

#### 职责
- 管理不同模型的参数限制
- 自动验证和调整参数
- 提供统一的模型调用接口

#### 接口设计

```python
class ModelAdapter:
    """模型适配器 - 处理不同模型的参数差异"""
    
    # 模型限制配置
    MODEL_LIMITS = {
        "deepseek:deepseek-chat": {
            "max_tokens": 8192,
            "context_window": 32768,
            "supports_streaming": True
        },
        "deepseek:deepseek-reasoner": {
            "max_tokens": 8192,
            "context_window": 65536,
            "supports_streaming": False
        },
        "openai:gpt-4o-mini": {
            "max_tokens": 16384,
            "context_window": 128000,
            "supports_streaming": True
        }
    }
    
    @classmethod
    def get_model_limits(cls, model: str) -> dict:
        """获取模型限制"""
        return cls.MODEL_LIMITS.get(model, {
            "max_tokens": 4096,  # 保守默认值
            "context_window": 8192
        })
    
    @classmethod
    def validate_and_adjust_params(cls, model: str, **kwargs) -> dict:
        """验证并调整参数"""
        limits = cls.get_model_limits(model)
        adjusted = kwargs.copy()
        
        # 调整 max_tokens
        if 'max_tokens' in adjusted:
            requested = adjusted['max_tokens']
            max_allowed = limits['max_tokens']
            if requested > max_allowed:
                logger.warning(
                    f"max_tokens {requested} exceeds limit {max_allowed}, "
                    f"adjusting to {max_allowed}"
                )
                adjusted['max_tokens'] = max_allowed
        
        return adjusted
    
    @classmethod
    def safe_api_call(cls, model: str, messages: list, **kwargs):
        """安全的 API 调用（带参数验证）"""
        # 1. 验证和调整参数
        adjusted_params = cls.validate_and_adjust_params(model, **kwargs)
        
        # 2. 调用 API
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **adjusted_params
            )
            return response
        except Exception as e:
            # 3. 错误处理
            if "max_tokens" in str(e):
                # 参数错误，进一步降低
                if 'max_tokens' in adjusted_params:
                    adjusted_params['max_tokens'] = adjusted_params['max_tokens'] // 2
                    logger.warning(f"Retrying with reduced max_tokens: {adjusted_params['max_tokens']}")
                    return client.chat.completions.create(
                        model=model,
                        messages=messages,
                        **adjusted_params
                    )
            raise
```

#### 使用示例

```python
# 修改前
response = client.chat.completions.create(
    model=model,
    messages=messages,
    max_tokens=15000  # 可能超限
)

# 修改后
response = ModelAdapter.safe_api_call(
    model=model,
    messages=messages,
    max_tokens=15000  # 自动调整
)
```

### 2. 上下文管理器 (Context Manager)

#### 职责
- 监控上下文长度
- 决定处理策略（直接/分块/压缩）
- 管理数据流转

#### 接口设计

```python
class ContextManager:
    """上下文管理器"""
    
    def __init__(self, model: str):
        self.model = model
        self.limits = ModelAdapter.get_model_limits(model)
        self.chunking_threshold = int(self.limits['context_window'] * 0.8)
    
    def should_chunk(self, text: str) -> bool:
        """判断是否需要分块"""
        token_count = count_tokens(text)
        return token_count > self.chunking_threshold
    
    def should_compress(self, text: str) -> bool:
        """判断是否需要压缩"""
        token_count = count_tokens(text)
        return token_count > self.limits['context_window'] * 0.5
    
    def process_text(self, text: str, processor_func, **kwargs):
        """智能处理文本"""
        if not self.should_chunk(text):
            # 直接处理
            return processor_func(text, **kwargs)
        
        # 分块处理
        logger.info(f"Text too long ({count_tokens(text)} tokens), using chunking")
        return self._process_with_chunking(text, processor_func, **kwargs)
    
    def _process_with_chunking(self, text: str, processor_func, **kwargs):
        """分块处理"""
        # 实现见下文
        pass
```

### 3. 分块处理器 (Chunking Processor)

#### 设计原理

**分块策略**:
1. 按语义边界分割（段落、章节）
2. 保持块间重叠（200 tokens）
3. 提供上下文信息
4. 智能合并结果

#### 实现设计

```python
class ChunkingProcessor:
    """分块处理器"""
    
    def __init__(self, max_chunk_size: int = 6000, overlap_size: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
    
    def chunk_by_semantic(self, text: str) -> List[str]:
        """按语义分块"""
        # 1. 按段落分割
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for para in paragraphs:
            para_tokens = count_tokens(para)
            
            # 如果加上这段会超，先保存当前块
            if current_tokens + para_tokens > self.max_chunk_size:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
            
            # 如果单段就超了，强制分割
            if para_tokens > self.max_chunk_size:
                sub_chunks = self._split_long_paragraph(para)
                chunks.extend(sub_chunks)
            else:
                current_chunk.append(para)
                current_tokens += para_tokens
        
        # 最后一块
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def process_with_context(self, chunks: List[str], processor_func):
        """带上下文处理"""
        results = []
        
        for i, chunk in enumerate(chunks):
            # 构建上下文
            context_info = {
                'position': f"{i+1}/{len(chunks)}",
                'is_first': i == 0,
                'is_last': i == len(chunks) - 1,
                'prev_text': chunks[i-1][-self.overlap_size:] if i > 0 else None,
                'next_text': chunks[i+1][:self.overlap_size] if i < len(chunks)-1 else None
            }
            
            # 构建提示
            prompt = self._build_chunk_prompt(chunk, context_info)
            
            # 处理
            result = processor_func(prompt)
            results.append(result)
        
        return results
    
    def _build_chunk_prompt(self, chunk: str, context: dict) -> str:
        """构建块提示"""
        parts = [f"[文档位置: {context['position']}]"]
        
        if context['prev_text']:
            parts.append(f"[前文结尾]: ...{context['prev_text']}")
        
        parts.append(f"[当前段落]:\n{chunk}")
        
        if context['next_text']:
            parts.append(f"[后文开头]: {context['next_text']}...")
        
        parts.append("\n请处理当前段落，注意与前后文的连贯性。")
        
        return '\n\n'.join(parts)
    
    def merge_chunks(self, chunks: List[str]) -> str:
        """合并块"""
        if len(chunks) <= 1:
            return chunks[0] if chunks else ""
        
        # 简单合并（可以后续优化为智能合并）
        return '\n\n'.join(chunks)
```

### 4. 摘要压缩器 (Summarization Compressor)

#### 设计原理

**压缩策略**:
1. 结构化提取关键信息
2. 分层递归压缩
3. 保持可配置的压缩比
4. 缓存原始数据

#### 实现设计

```python
class SummarizationCompressor:
    """摘要压缩器"""
    
    def __init__(self, model: str, target_ratio: float = 0.3):
        self.model = model
        self.target_ratio = target_ratio
        self.cache = {}
    
    def compress(self, text: str, cache_key: str = None) -> dict:
        """压缩文本"""
        # 检查缓存
        if cache_key and cache_key in self.cache:
            return self.cache[cache_key]
        
        # 生成结构化摘要
        summary = self._generate_structured_summary(text)
        
        # 缓存
        if cache_key:
            self.cache[cache_key] = {
                'summary': summary,
                'original': text,
                'compression_ratio': len(summary['text']) / len(text)
            }
        
        return summary
    
    def _generate_structured_summary(self, text: str) -> dict:
        """生成结构化摘要"""
        prompt = f"""
        请分析以下文本，提取结构化信息：
        
        {text}
        
        请以 JSON 格式返回：
        {{
            "main_topic": "主题",
            "key_points": ["要点1", "要点2", "要点3"],
            "important_data": ["数据1", "数据2"],
            "conclusions": ["结论1", "结论2"]
        }}
        """
        
        response = ModelAdapter.safe_api_call(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=2000
        )
        
        try:
            structured = json.loads(response.choices[0].message.content)
            # 生成文本摘要
            text_summary = self._structured_to_text(structured)
            structured['text'] = text_summary
            return structured
        except json.JSONDecodeError:
            # 降级为简单摘要
            return self._simple_summary(text)
    
    def _structured_to_text(self, structured: dict) -> str:
        """结构化数据转文本"""
        parts = [
            f"主题: {structured['main_topic']}",
            f"关键点: {', '.join(structured['key_points'])}",
        ]
        if structured.get('important_data'):
            parts.append(f"重要数据: {', '.join(structured['important_data'])}")
        if structured.get('conclusions'):
            parts.append(f"结论: {', '.join(structured['conclusions'])}")
        
        return '\n'.join(parts)
```

### 5. 增强的降级机制

#### 设计原理

**降级策略**:
1. 识别错误类型
2. 参数错误先调整参数重试
3. 调整失败再降级模型
4. 记录所有操作

#### 实现设计

```python
def enhanced_fallback(agent_func):
    """增强的降级装饰器"""
    @wraps(agent_func)
    def wrapper(*args, **kwargs):
        model = kwargs.get('model')
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                return agent_func(*args, **kwargs)
            
            except Exception as e:
                error_str = str(e)
                
                # 1. 参数错误处理
                if "max_tokens" in error_str or "400" in error_str:
                    logger.warning(f"Parameter error on attempt {attempt + 1}: {e}")
                    
                    if attempt < max_retries - 1:
                        # 调整参数重试
                        if 'max_tokens' in kwargs:
                            kwargs['max_tokens'] = kwargs['max_tokens'] // 2
                            logger.info(f"Retrying with reduced max_tokens: {kwargs['max_tokens']}")
                            continue
                
                # 2. 模型降级
                if model and "deepseek" in model and attempt < max_retries - 1:
                    logger.warning(f"Model {model} failed, falling back to {ModelConfig.FALLBACK_MODEL}")
                    kwargs['model'] = ModelConfig.FALLBACK_MODEL
                    # 重置参数
                    if 'max_tokens' in kwargs:
                        kwargs['max_tokens'] = 15000  # OpenAI 可以支持
                    continue
                
                # 3. 所有尝试失败
                raise
        
        return None
    
    return wrapper
```

## 数据模型

### Token 使用统计

```python
@dataclass
class TokenUsageStats:
    """Token 使用统计"""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    timestamp: datetime
    context_window_usage: float  # 使用率 0-1
    
    def to_dict(self) -> dict:
        return {
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'model': self.model,
            'timestamp': self.timestamp.isoformat(),
            'context_window_usage': f"{self.context_window_usage:.2%}"
        }
```

### 处理策略配置

```python
@dataclass
class ContextProcessingConfig:
    """上下文处理配置"""
    enable_chunking: bool = True
    enable_compression: bool = False
    chunking_threshold: float = 0.8  # 上下文窗口的 80%
    compression_ratio: float = 0.3
    chunk_overlap: int = 200
    max_chunk_size: int = 6000
    
    @classmethod
    def from_env(cls):
        """从环境变量加载"""
        return cls(
            enable_chunking=os.getenv('ENABLE_CHUNKING', 'true').lower() == 'true',
            enable_compression=os.getenv('ENABLE_COMPRESSION', 'false').lower() == 'true',
            chunking_threshold=float(os.getenv('CHUNKING_THRESHOLD', '0.8')),
            compression_ratio=float(os.getenv('COMPRESSION_RATIO', '0.3')),
            chunk_overlap=int(os.getenv('CHUNK_OVERLAP', '200')),
            max_chunk_size=int(os.getenv('MAX_CHUNK_SIZE', '6000'))
        )
```

## 错误处理

### 错误分类

1. **参数错误** (400)
   - 识别: "max_tokens", "invalid"
   - 处理: 调整参数重试

2. **速率限制** (429)
   - 识别: "rate_limit"
   - 处理: 指数退避重试

3. **模型错误** (500)
   - 识别: "internal_error"
   - 处理: 降级到备用模型

4. **超时错误**
   - 识别: TimeoutError
   - 处理: 增加超时时间重试

### 错误恢复流程

```
API 调用失败
    ↓
识别错误类型
    ↓
┌─────────────┬─────────────┬─────────────┐
│ 参数错误     │ 速率限制     │ 模型错误     │
↓             ↓             ↓
调整参数       等待重试       降级模型
    ↓             ↓             ↓
重试 (最多2次)
    ↓
成功 / 失败报告
```

## 测试策略

### 单元测试

1. **ModelAdapter 测试**
   - 测试参数验证逻辑
   - 测试不同模型的限制
   - 测试参数调整算法

2. **ChunkingProcessor 测试**
   - 测试语义分块
   - 测试重叠处理
   - 测试合并逻辑

3. **SummarizationCompressor 测试**
   - 测试结构化提取
   - 测试压缩比例
   - 测试缓存机制

### 集成测试

1. **端到端流程测试**
   - 短文本（< 2K tokens）
   - 中等文本（2K-10K tokens）
   - 长文本（> 10K tokens）

2. **错误恢复测试**
   - 模拟参数错误
   - 模拟模型失败
   - 验证降级机制

3. **性能测试**
   - 测量处理时间
   - 测量 token 使用
   - 测量成本

## 部署考虑

### 配置管理

所有配置通过环境变量或配置文件管理：

```bash
# 模型配置
WRITER_MODEL=deepseek:deepseek-chat
EDITOR_MODEL=deepseek:deepseek-chat
FALLBACK_MODEL=openai:gpt-4o-mini

# 上下文管理
ENABLE_CHUNKING=true
ENABLE_COMPRESSION=false
CHUNKING_THRESHOLD=0.8
COMPRESSION_RATIO=0.3
CHUNK_OVERLAP=200
MAX_CHUNK_SIZE=6000

# 监控
ENABLE_TOKEN_LOGGING=true
TOKEN_USAGE_WARNING_THRESHOLD=0.9
```

### 监控指标

1. **Token 使用**
   - 平均输入 tokens
   - 平均输出 tokens
   - 上下文窗口使用率

2. **性能指标**
   - API 调用延迟
   - 分块处理时间
   - 端到端处理时间

3. **错误率**
   - 参数错误次数
   - 降级触发次数
   - 最终失败率

### 成本优化

1. **缓存策略**
   - 缓存摘要结果
   - 缓存重复查询

2. **模型选择**
   - 优先使用 DeepSeek（成本低）
   - 必要时降级到 OpenAI

3. **Token 优化**
   - 移除冗余信息
   - 压缩历史上下文
   - 智能选择相关内容

## 未来扩展

### Phase 2: 摘要压缩

在 Phase 1 分块处理稳定后，添加摘要压缩功能：
- 实现 SummarizationCompressor
- 在 Agent 间传递时自动压缩
- 提供摘要和详情的切换

### Phase 3: 外部记忆系统

长期考虑引入 RAG 系统：
- 向量数据库（ChromaDB/Pinecone）
- 分层记忆（短期/工作/长期）
- 智能检索相关上下文

### Phase 4: 流式处理

支持流式输出：
- 实时显示生成内容
- 提前检测长度问题
- 动态调整策略

## 总结

本设计提供了一个完整的上下文长度优化方案，从立即修复到长期架构升级。核心组件包括：

1. **ModelAdapter**: 处理模型参数差异
2. **ContextManager**: 智能决策处理策略
3. **ChunkingProcessor**: 分块处理长文本
4. **SummarizationCompressor**: 压缩历史上下文
5. **Enhanced Fallback**: 智能错误恢复

这些组件协同工作，确保系统能够处理任意长度的文本，同时保持良好的性能和用户体验。
