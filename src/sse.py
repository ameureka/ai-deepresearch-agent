"""
SSE (Server-Sent Events) 工具模块

本模块提供 SSE 流式接口的核心工具函数：
1. format_sse_event: 格式化 SSE 事件
2. 相关的辅助函数

SSE 规范：
- 事件格式：event: <type>\ndata: <json>\n\n
- 事件类型：start, plan, progress, done, error
- 所有数据使用 JSON 格式

设计原则：
- 简单明了，符合 SSE 标准
- 所有数据必须是可 JSON 序列化的
- 每个事件以两个换行符结尾
"""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def format_sse_event(event_type: str, data: Dict[str, Any]) -> str:
    """
    格式化 SSE 事件

    将事件类型和数据格式化为符合 SSE 规范的字符串。

    SSE 事件格式：
        event: <event_type>
        data: <json_data>
        <blank line>

    参数：
        event_type: 事件类型（start, plan, progress, done, error）
        data: 事件数据（必须可 JSON 序列化）

    返回：
        格式化的 SSE 事件字符串

    异常：
        TypeError: 如果 data 无法序列化为 JSON
        ValueError: 如果 event_type 或 data 为空

    示例：
        >>> format_sse_event("start", {"prompt": "研究 AI"})
        'event: start\\ndata: {"prompt": "研究 AI"}\\n\\n'

        >>> format_sse_event("progress", {"step": 1, "total": 3})
        'event: progress\\ndata: {"step": 1, "total": 3}\\n\\n'

    设计说明：
        - 使用 json.dumps 确保数据正确序列化
        - 使用 ensure_ascii=False 支持中文字符
        - 事件以 \\n\\n 结尾（SSE 规范要求）
        - 不添加 id 字段（简化实现，符合 MVP 原则）
    """
    # 验证参数
    if not event_type:
        raise ValueError("event_type 不能为空")
    if data is None:
        raise ValueError("data 不能为 None")

    try:
        # 序列化数据为 JSON
        # ensure_ascii=False: 支持中文字符
        # separators=(',', ':'): 紧凑格式，减少传输大小
        json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

        # 构建 SSE 事件
        # 格式：event: <type>\ndata: <json>\n\n
        event_str = f"event: {event_type}\ndata: {json_data}\n\n"

        # 记录事件（用于调试，生产环境可关闭）
        logger.debug(f"📤 SSE Event: {event_type} ({len(json_data)} bytes)")

        return event_str

    except (TypeError, ValueError) as e:
        logger.error(f"❌ SSE 事件格式化失败: {e}\n事件类型: {event_type}\n数据: {data}")
        raise TypeError(f"无法序列化数据为 JSON: {e}")


def format_sse_comment(comment: str) -> str:
    """
    格式化 SSE 注释

    SSE 支持注释行（以 : 开头），用于：
    1. 保持连接活跃（心跳）
    2. 调试信息
    3. 服务器端日志

    注释不会被客户端 EventSource 处理，但会保持连接。

    参数：
        comment: 注释内容

    返回：
        格式化的 SSE 注释字符串

    示例：
        >>> format_sse_comment("heartbeat")
        ': heartbeat\\n\\n'

        >>> format_sse_comment("processing step 1/3")
        ': processing step 1/3\\n\\n'

    使用场景：
        - 每 30 秒发送心跳防止连接超时
        - 记录服务器端处理进度（不需要客户端显示）
    """
    return f": {comment}\n\n"


def create_sse_heartbeat() -> str:
    """
    创建 SSE 心跳消息

    返回一个标准的心跳注释，用于保持连接活跃。

    某些代理服务器、CDN 或浏览器可能会在空闲一段时间后关闭连接。
    定期发送心跳可以防止这种情况。

    建议频率：每 15-30 秒

    返回：
        SSE 心跳字符串

    示例：
        >>> create_sse_heartbeat()
        ': heartbeat\\n\\n'
    """
    return format_sse_comment("heartbeat")


# === SSE 事件类型常量 ===
class SSEEvents:
    """
    SSE 事件类型常量

    定义所有支持的事件类型，提供类型安全和代码补全。

    使用示例：
        format_sse_event(SSEEvents.START, {"prompt": "研究主题"})
    """
    START = "start"       # 任务开始
    PLAN = "plan"         # 发送执行计划
    PROGRESS = "progress" # 步骤执行进度
    DONE = "done"         # 任务完成
    ERROR = "error"       # 发生错误


# === SSE 事件构建器（便捷函数）===

def create_start_event(prompt: str) -> str:
    """
    创建 START 事件

    参数：
        prompt: 研究主题

    返回：
        格式化的 SSE 事件
    """
    return format_sse_event(SSEEvents.START, {"prompt": prompt})


def create_plan_event(steps: list) -> str:
    """
    创建 PLAN 事件

    参数：
        steps: 执行步骤列表

    返回：
        格式化的 SSE 事件
    """
    return format_sse_event(SSEEvents.PLAN, {"steps": steps})


def create_progress_event(step: int, total: int, message: str) -> str:
    """
    创建 PROGRESS 事件

    参数：
        step: 当前步骤编号（从 1 开始）
        total: 总步骤数
        message: 步骤描述

    返回：
        格式化的 SSE 事件
    """
    return format_sse_event(
        SSEEvents.PROGRESS,
        {"step": step, "total": total, "message": message}
    )


def create_done_event(report: str) -> str:
    """
    创建 DONE 事件

    参数：
        report: 最终研究报告（Markdown 格式）

    返回：
        格式化的 SSE 事件
    """
    return format_sse_event(SSEEvents.DONE, {"report": report})


def create_error_event(message: str, step: int = None) -> str:
    """
    创建 ERROR 事件

    参数：
        message: 错误信息
        step: 出错的步骤编号（可选）

    返回：
        格式化的 SSE 事件
    """
    data = {"message": message}
    if step is not None:
        data["step"] = step
    return format_sse_event(SSEEvents.ERROR, data)


# === SSE 响应头配置 ===

def get_sse_headers() -> Dict[str, str]:
    """
    获取 SSE 标准响应头

    返回适用于 SSE 的 HTTP 响应头配置。

    关键响应头：
        - Cache-Control: no-cache, no-transform
          禁用缓存，确保事件实时传递

        - Connection: keep-alive
          保持连接打开

        - X-Accel-Buffering: no
          禁用 Nginx 缓冲（如果使用 Nginx）

        - Content-Type: text/event-stream
          （由 FastAPI StreamingResponse 自动设置）

    返回：
        响应头字典

    使用示例：
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers=get_sse_headers()
        )

    生产环境注意事项：
        - 某些 CDN 可能会缓冲 SSE，需要特殊配置
        - Cloudflare 需要启用 "Stream" 功能
        - AWS CloudFront 需要配置 "Origin Response Timeout"
    """
    return {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        "Access-Control-Allow-Origin": "*",  # CORS（可根据需要调整）
    }


# === SSE 流控制 ===

class SSEStreamController:
    """
    SSE 流控制器

    提供对 SSE 流的高级控制，包括：
    - 心跳管理
    - 流量控制
    - 错误恢复

    （可选功能，Phase 2 MVP 暂不实现，预留接口）
    """

    def __init__(self, heartbeat_interval: int = 30):
        """
        初始化流控制器

        参数：
            heartbeat_interval: 心跳间隔（秒）
        """
        self.heartbeat_interval = heartbeat_interval
        self.last_heartbeat = 0

    def should_send_heartbeat(self) -> bool:
        """
        检查是否应该发送心跳

        返回：
            bool: 如果距离上次心跳超过 heartbeat_interval 秒，返回 True
        """
        import time
        current_time = time.time()
        if current_time - self.last_heartbeat >= self.heartbeat_interval:
            self.last_heartbeat = current_time
            return True
        return False


# === 工具函数：SSE 事件验证 ===

def validate_sse_event(event_type: str, data: Dict[str, Any]) -> bool:
    """
    验证 SSE 事件是否符合规范

    检查：
    1. event_type 是否在支持的类型中
    2. data 是否包含必需的字段
    3. data 是否可 JSON 序列化

    参数：
        event_type: 事件类型
        data: 事件数据

    返回：
        bool: 验证通过返回 True

    异常：
        ValueError: 验证失败时抛出
    """
    # 检查事件类型
    valid_types = {SSEEvents.START, SSEEvents.PLAN, SSEEvents.PROGRESS, SSEEvents.DONE, SSEEvents.ERROR}
    if event_type not in valid_types:
        raise ValueError(f"无效的事件类型: {event_type}，支持的类型: {valid_types}")

    # 检查必需字段
    required_fields = {
        SSEEvents.START: ["prompt"],
        SSEEvents.PLAN: ["steps"],
        SSEEvents.PROGRESS: ["step", "total", "message"],
        SSEEvents.DONE: ["report"],
        SSEEvents.ERROR: ["message"],
    }

    missing_fields = []
    for field in required_fields.get(event_type, []):
        if field not in data:
            missing_fields.append(field)

    if missing_fields:
        raise ValueError(f"事件 {event_type} 缺少必需字段: {missing_fields}")

    # 检查是否可 JSON 序列化
    try:
        json.dumps(data)
    except (TypeError, ValueError) as e:
        raise ValueError(f"事件数据无法序列化为 JSON: {e}")

    return True
