"""
API 模型定义 - Phase 2 标准化 API 响应格式

本模块定义了 Phase 2 中使用的标准化 API 模型：
1. ApiResponse: 统一的 API 响应格式
2. ResearchRequest: SSE 研究请求模型
3. 相关的辅助类型

设计原则：
- 简单明了，符合 MVP 原则
- 提供清晰的类型提示
- 支持可选字段以保持灵活性
"""

from typing import Optional, Any, List
from pydantic import BaseModel, Field, validator


class ApiResponse(BaseModel):
    """
    统一的 API 响应格式

    所有 API 端点都应使用此格式返回数据，确保前端可以统一处理响应。

    字段说明：
        success: 布尔值，表示请求是否成功
        data: 任意类型，成功时返回的数据（可选）
        error: 字符串，失败时返回的错误信息（可选）

    使用示例：
        # 成功响应
        ApiResponse(success=True, data={"status": "ok"})

        # 失败响应
        ApiResponse(success=False, error="参数验证失败")

    设计决策：
        - success 字段必需，便于前端快速判断
        - data 和 error 互斥但不强制（简化实现）
        - error 不包含敏感信息（如堆栈跟踪）
    """

    success: bool = Field(
        ...,
        description="请求是否成功"
    )
    data: Optional[Any] = Field(
        None,
        description="成功时返回的数据，可以是任意类型"
    )
    error: Optional[str] = Field(
        None,
        description="失败时返回的错误信息，不包含敏感信息"
    )

    class Config:
        # 提供示例，用于 OpenAPI 文档生成
        schema_extra = {
            "examples": [
                {
                    "success": True,
                    "data": {"status": "ok"},
                    "error": None
                },
                {
                    "success": False,
                    "data": None,
                    "error": "Invalid request parameter"
                }
            ]
        }


class ResearchRequest(BaseModel):
    """
    SSE 研究请求模型

    用于 POST /api/research/stream 端点的请求体。

    字段说明：
        prompt: 研究主题（必需）
        model: 使用的模型名称（可选，默认使用配置中的模型）

    使用示例：
        ResearchRequest(
            prompt="Analyze the applications of AI in healthcare",
            model="deepseek:deepseek-chat"
        )

    验证规则：
        - prompt 不能为空
        - prompt 长度应在合理范围内（10-5000 字符）
        - model 如果指定，必须是有效的模型名称
    """

    prompt: str = Field(
        ...,
        description="研究主题或问题",
        min_length=10,
        max_length=5000
    )
    model: Optional[str] = Field(
        None,
        description="可选的模型名称，如不指定则使用默认模型"
    )

    @validator('prompt')
    def validate_prompt(cls, v):
        """
        验证 prompt 字段

        检查：
        1. 不能全是空白字符
        2. 应该是有意义的文本

        参数：
            v: prompt 值

        返回：
            验证后的 prompt

        异常：
            ValueError: 如果验证失败
        """
        # 去除首尾空白后检查
        stripped = v.strip()
        if not stripped:
            raise ValueError("prompt 不能为空或只包含空白字符")

        # 返回去除空白后的值
        return stripped

    @validator('model')
    def validate_model(cls, v):
        """
        验证 model 字段

        检查：
        1. 如果指定，应该符合模型名称格式
        2. 支持的格式：provider:model-name

        参数：
            v: model 值

        返回：
            验证后的 model
        """
        if v is not None:
            # 如果指定了模型，确保格式正确
            if not v.strip():
                raise ValueError("model 不能为空字符串")
            # 可以添加更多验证，如检查是否在允许的模型列表中
        return v

    class Config:
        # 提供示例，用于 OpenAPI 文档生成
        schema_extra = {
            "example": {
                "prompt": "Research the latest developments in quantum computing",
                "model": "deepseek:deepseek-chat"
            }
        }


class ModelInfo(BaseModel):
    """
    模型信息模型

    用于 GET /api/models 端点返回可用模型列表。

    字段说明：
        name: 模型标识符
        provider: 提供商（openai, deepseek 等）
        description: 模型描述
        context_window: 上下文窗口大小（tokens）
        supports_streaming: 是否支持流式输出
    """

    name: str = Field(
        ...,
        description="模型标识符，格式：provider:model-name"
    )
    provider: str = Field(
        ...,
        description="模型提供商"
    )
    description: str = Field(
        ...,
        description="模型描述"
    )
    context_window: int = Field(
        ...,
        description="上下文窗口大小（tokens）"
    )
    supports_streaming: bool = Field(
        True,
        description="是否支持流式输出"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "deepseek:deepseek-chat",
                "provider": "deepseek",
                "description": "DeepSeek Chat Model - 高性价比通用对话模型",
                "context_window": 65536,
                "supports_streaming": True
            }
        }


class HealthResponse(BaseModel):
    """
    健康检查响应模型

    用于 GET /api/health 端点。

    字段说明：
        status: 服务状态（ok, degraded, error）
        timestamp: 响应时间戳
        version: API 版本（可选）
    """

    status: str = Field(
        ...,
        description="服务状态"
    )
    timestamp: Optional[str] = Field(
        None,
        description="ISO 格式的时间戳"
    )
    version: Optional[str] = Field(
        None,
        description="API 版本"
    )

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "timestamp": "2025-10-31T03:00:00Z",
                "version": "2.0.0"
            }
        }


# SSE 事件类型定义（用于类型提示）
class SSEEventType:
    """
    SSE 事件类型常量

    定义了 POST /api/research/stream 端点支持的所有事件类型。

    事件类型：
        START: 任务开始
        PLAN: 发送执行计划
        PROGRESS: 步骤执行进度
        DONE: 任务完成
        ERROR: 发生错误

    使用示例：
        event_type = SSEEventType.START
    """

    START = "start"       # 任务开始，包含 prompt
    PLAN = "plan"         # 发送计划步骤列表
    PROGRESS = "progress" # 步骤执行进度更新
    DONE = "done"         # 任务完成，包含最终报告
    ERROR = "error"       # 发生错误，包含错误信息


class SSEStartEvent(BaseModel):
    """START 事件数据格式"""
    prompt: str = Field(..., description="研究主题")


class SSEPlanEvent(BaseModel):
    """PLAN 事件数据格式"""
    steps: List[str] = Field(..., description="执行步骤列表")


class SSEProgressEvent(BaseModel):
    """PROGRESS 事件数据格式"""
    step: int = Field(..., description="当前步骤编号（从 1 开始）")
    total: int = Field(..., description="总步骤数")
    message: str = Field(..., description="步骤描述")


class SSEDoneEvent(BaseModel):
    """DONE 事件数据格式"""
    report: str = Field(..., description="最终研究报告（Markdown 格式）")


class SSEErrorEvent(BaseModel):
    """ERROR 事件数据格式"""
    message: str = Field(..., description="错误信息")
    step: Optional[int] = Field(None, description="出错的步骤编号（可选）")
