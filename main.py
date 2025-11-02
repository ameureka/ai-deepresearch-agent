"""
主应用程序 - 多代理研究报告生成系统的 Web 服务
本文件实现了一个 FastAPI Web 应用，提供：
1. 用户界面用于提交研究主题
2. 后台任务处理系统
3. 实时进度跟踪
4. 数据库持久化
5. Phase 2: 标准化 API 和 SSE 流式接口
"""

from __future__ import annotations

import os
import uuid
import json
import threading
import logging
import traceback
from datetime import datetime
from queue import Queue
from typing import Optional, Literal, Dict, Any
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from sqlalchemy import create_engine, Column, Text, DateTime, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from dotenv import load_dotenv

from src.planning_agent import planner_agent, executor_agent_step
from src.api_models import ApiResponse, ResearchRequest, HealthResponse, ModelInfo
from src.sse import (
    format_sse_event,
    SSEEvents,
    get_sse_headers,
    create_start_event,
    create_plan_event,
    create_progress_event,
    create_done_event,
    create_error_event
)
from fastapi.responses import StreamingResponse

import html, textwrap

# === 配置结构化日志 ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# === 加载环境变量 ===
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 修复 Heroku 的 postgres:// URL 格式（需要使用 postgresql://）
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL 未设置")


# === 数据库设置 ===
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)

research_task_queue: Queue = Queue()
worker_thread: Optional[threading.Thread] = None
worker_stop_event = threading.Event()


def default_progress() -> Dict[str, Any]:
    return {
        "currentStep": None,
        "totalSteps": None,
        "completedSteps": 0,
        "events": [],
    }


def ensure_progress(task: ResearchTask) -> Dict[str, Any]:
    progress = task.progress or {}
    if not isinstance(progress, dict):
        progress = {}
    events = progress.get("events", [])
    if not isinstance(events, list):
        events = list(events) if events else []
    progress["events"] = events
    progress.setdefault("currentStep", None)
    progress.setdefault("totalSteps", None)
    progress.setdefault("completedSteps", 0)
    task.progress = progress
    return progress


def ensure_queue_info(task: "ResearchTask") -> Dict[str, Any]:
    queue_info = task.queue_info or {}
    if not isinstance(queue_info, dict):
        queue_info = {}
    task.queue_info = queue_info
    return queue_info


def add_event(task: ResearchTask, event_type: str, message: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    progress = ensure_progress(task)
    event = {
        "type": event_type,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if extra:
        event.update(extra)
    progress["events"].append(event)
    task.progress = progress
    task.updated_at = datetime.utcnow()
    return event


def serialize_progress(progress: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not progress or not isinstance(progress, dict):
        return default_progress()
    events = progress.get("events", [])
    if not isinstance(events, list):
        events = list(events)
    return {
        "currentStep": progress.get("currentStep"),
        "totalSteps": progress.get("totalSteps"),
        "completedSteps": progress.get("completedSteps", 0),
        "events": events,
    }


def serialize_queue_info(queue_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not queue_info or not isinstance(queue_info, dict):
        return {}
    sanitized = {}
    for key, value in queue_info.items():
        if isinstance(value, (str, int, float, type(None))):
            sanitized[key] = value
        else:
            try:
                sanitized[key] = json.loads(json.dumps(value))
            except Exception:
                sanitized[key] = str(value)
    return sanitized


def run_research_task(queue_item: Dict[str, Any]) -> None:
    task_id = queue_item.get("task_id")
    prompt = queue_item.get("prompt")
    model = queue_item.get("model")

    if not task_id:
        logger.error("Queue item missing task_id, skipping execution")
        return

    session = SessionLocal()
    try:
        task: Optional[ResearchTask] = (
            session.query(ResearchTask)
            .filter(ResearchTask.task_id == task_id)
            .one_or_none()
        )

        if not task:
            logger.error(f"ResearchTask with task_id {task_id} not found, skipping execution.")
            return

        if prompt:
            task.topic = prompt
        prompt_to_use = task.topic

        if not prompt_to_use:
            logger.error(f"ResearchTask {task_id} lacks prompt/topic, marking as failed.")
            task.status = "failed"
            add_event(task, "error", "Prompt is required but missing.")
            session.commit()
            return

        queue_info = ensure_queue_info(task)
        if "enqueuedAt" not in queue_info:
            queue_info["enqueuedAt"] = datetime.utcnow().isoformat() + "Z"
        queue_info["startedAt"] = datetime.utcnow().isoformat() + "Z"
        queue_info["workerId"] = threading.current_thread().name
        retry_count = queue_info.get("retryCount", 0)
        if not isinstance(retry_count, int):
            try:
                retry_count = int(retry_count)  # type: ignore[arg-type]
            except Exception:
                retry_count = 0
        queue_info["retryCount"] = retry_count
        task.queue_info = queue_info

        task.status = "running"
        ensure_progress(task)
        add_event(task, "start", "Research started", {"prompt": prompt_to_use})
        task.started_at = datetime.utcnow()
        session.commit()

        execution_history = []

        steps = planner_agent(prompt_to_use, model=model)
        add_event(task, "plan", "Research plan generated", {"steps": steps})
        progress = ensure_progress(task)
        progress["totalSteps"] = len(steps)
        progress["completedSteps"] = 0
        progress["currentStep"] = None
        task.progress = progress
        session.commit()

        for index, step_title in enumerate(steps):
            step_number = index + 1
            add_event(
                task,
                "progress",
                step_title,
                {"step": step_number, "total": len(steps)},
            )
            progress = ensure_progress(task)
            progress["completedSteps"] = step_number
            progress["currentStep"] = step_title
            task.progress = progress
            session.commit()

            step_desc, agent_name, output = executor_agent_step(
                step_title, execution_history, prompt_to_use
            )
            execution_history.append([step_title, step_desc, output])
            logger.info(
                f"Task {task_id}: step {step_number}/{len(steps)} completed using {agent_name}"
            )

        final_report = (
            execution_history[-1][2] if execution_history else "未生成报告。"
        )

        add_event(task, "done", "Research completed", {"report": final_report})
        progress = ensure_progress(task)
        progress["completedSteps"] = progress.get("totalSteps") or len(steps)
        progress["currentStep"] = None
        task.progress = progress
        task.status = "completed"
        task.report = final_report
        queue_info = ensure_queue_info(task)
        queue_info["finishedAt"] = datetime.utcnow().isoformat() + "Z"
        task.queue_info = queue_info
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        session.commit()
        logger.info(f"Task {task_id} completed successfully.")

    except Exception as exc:
        logger.error(f"Task {task_id} failed: {exc}")
        logger.error(traceback.format_exc())
        session.rollback()
        task = (
            session.query(ResearchTask)
            .filter(ResearchTask.task_id == task_id)
            .one_or_none()
        )
        if task:
            ensure_progress(task)
            add_event(task, "error", f"Task failed: {exc}")
            progress = ensure_progress(task)
            progress["currentStep"] = None
            task.progress = progress
            task.status = "failed"
            queue_info = ensure_queue_info(task)
            queue_info["failedAt"] = datetime.utcnow().isoformat() + "Z"
            task.queue_info = queue_info
            task.failed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()
            session.commit()
    finally:
        session.close()


def worker_loop() -> None:
    logger.info("Research worker started.")
    while not worker_stop_event.is_set():
        try:
            queue_item = research_task_queue.get()
            if queue_item is None:
                research_task_queue.task_done()
                break
            run_research_task(queue_item)
        except Exception as exc:
            logger.error(f"Unexpected error in worker loop: {exc}")
            logger.error(traceback.format_exc())
        finally:
            research_task_queue.task_done()
    logger.info("Research worker stopped.")


def start_worker() -> None:
    global worker_thread
    if worker_thread and worker_thread.is_alive():
        return
    worker_stop_event.clear()
    worker_thread = threading.Thread(
        target=worker_loop, name="ResearchWorker", daemon=True
    )
    worker_thread.start()


def stop_worker() -> None:
    global worker_thread
    if worker_thread and worker_thread.is_alive():
        worker_stop_event.set()
        research_task_queue.put(None)
        worker_thread.join(timeout=5)
        logger.info("Research worker thread joined.")
        worker_thread = None



class Task(Base):
    """
    任务数据模型 - 存储研究报告生成任务的信息
    """

    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)  # 任务唯一标识符
    prompt = Column(Text)  # 用户输入的研究主题
    status = Column(String)  # 任务状态：running, done, error
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow)  # 更新时间
    result = Column(Text)  # 任务结果（JSON 格式）


class ResearchTask(Base):
    """
    research_tasks 表模型 - 与 Next.js Drizzle 表结构保持对齐
    """

    __tablename__ = "research_tasks"
    __table_args__ = {"extend_existing": True}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(PGUUID(as_uuid=True), nullable=True)
    chat_id = Column(PGUUID(as_uuid=True), nullable=True)
    topic = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="queued")
    progress = Column(JSONB, nullable=True)
    report = Column(Text, nullable=True)
    queue_info = Column(JSONB, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 创建数据库表（如果不存在）
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 数据库表初始化完成")
except Exception as e:
    logger.error(f"❌ 数据库创建失败: {e}")
    raise RuntimeError(f"数据库初始化失败: {e}")

# === FastAPI 应用设置 ===
app = FastAPI(
    title="AI Research Assistant API",
    description="多代理研究报告生成系统 - Phase 2 标准化 API",
    version="2.0.0"
)


@app.on_event("startup")
async def startup_event():
    start_worker()


@app.on_event("shutdown")
async def shutdown_event():
    stop_worker()

# === Phase 2: 配置 CORS 中间件（更严格的配置）===
# 从环境变量读取允许的来源，如果未设置则使用默认值
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://*.vercel.app"
).split(",")

# 处理通配符域名（*.vercel.app）
# FastAPI 的 CORSMiddleware 支持正则表达式
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

logger.info(f"✅ CORS 配置完成，允许的来源: {ALLOWED_ORIGINS}")

# === Phase 2: 全局异常处理器 ===
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器 - 捕获所有未处理的异常

    这确保：
    1. 所有错误都返回统一的 ApiResponse 格式
    2. 不向客户端泄露敏感信息（如堆栈跟踪）
    3. 错误被正确记录到日志系统

    参数：
        request: FastAPI 请求对象
        exc: 捕获的异常

    返回：
        JSONResponse with ApiResponse format
    """
    # 记录详细的错误信息到日志（包含堆栈跟踪）
    logger.error(
        f"❌ 未处理的异常: {type(exc).__name__}: {str(exc)}\n"
        f"路径: {request.url.path}\n"
        f"方法: {request.method}\n"
        f"堆栈跟踪:\n{traceback.format_exc()}"
    )

    # 向客户端返回简化的错误信息（不包含敏感信息）
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse(
            success=False,
            error=f"Internal server error: {type(exc).__name__}"
        ).dict()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTP 异常处理器 - 处理标准的 HTTP 异常

    将 FastAPI 的 HTTPException 转换为标准的 ApiResponse 格式。

    参数：
        request: FastAPI 请求对象
        exc: HTTPException 实例

    返回：
        JSONResponse with ApiResponse format
    """
    logger.warning(
        f"⚠️ HTTP 异常 {exc.status_code}: {exc.detail}\n"
        f"路径: {request.url.path}\n"
        f"方法: {request.method}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            success=False,
            error=exc.detail
        ).dict()
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    Pydantic 验证异常处理器

    处理请求体验证失败的情况。

    参数：
        request: FastAPI 请求对象
        exc: ValidationError 实例

    返回：
        JSONResponse with ApiResponse format
    """
    logger.warning(
        f"⚠️ 请求验证失败:\n"
        f"路径: {request.url.path}\n"
        f"错误: {exc.errors()}"
    )

    # 格式化验证错误信息
    error_messages = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ApiResponse(
            success=False,
            error=f"Validation error: {'; '.join(error_messages)}"
        ).dict()
    )


# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
# 设置模板引擎
templates = Jinja2Templates(directory="templates")

# 内存中的任务进度跟踪字典
task_progress = {}


class PromptRequest(BaseModel):
    """请求模型 - 用户提交的研究主题"""

    prompt: str


class QueueResearchTaskRequest(BaseModel):
    """研究任务排队请求模型"""

    taskId: str
    prompt: Optional[str] = None
    model: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    """
    首页路由 - 返回 SSE 流式接口界面（Phase 2 标准）
    """
    return templates.TemplateResponse("index-sse.html", {"request": request})


@app.get("/legacy", response_class=HTMLResponse)
def read_legacy_index(request: Request):
    """
    旧版轮询接口界面（已弃用，保留用于兼容）
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", response_class=JSONResponse)
def health_check_legacy():
    """
    健康检查端点 - 用于验证服务是否正常运行

    【简化版本】用于启动脚本和快速健康检查
    详细健康信息请使用 /api/health
    """
    return {"status": "ok"}


@app.get("/api", response_class=JSONResponse)
def health_check(request: Request):
    """
    健康检查端点 - 用于验证服务是否正常运行

    【已弃用】此端点保留用于向后兼容，请使用 /api/health
    """
    return {"status": "ok"}


@app.post("/api/research/tasks")
async def enqueue_research_task(request: QueueResearchTaskRequest):
    """
    将研究任务加入后台队列执行
    """
    session = SessionLocal()
    try:
        task: Optional[ResearchTask] = (
            session.query(ResearchTask)
            .filter(ResearchTask.task_id == request.taskId)
            .one_or_none()
        )
        if not task:
            raise HTTPException(status_code=404, detail="Research task not found")

        prompt = request.prompt or task.topic
        if not prompt or not prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt is required")

        previous_status = task.status
        task.topic = prompt
        task.status = "queued"
        task.report = None
        task.progress = default_progress()
        task.started_at = None
        task.completed_at = None
        task.failed_at = None

        queue_info = ensure_queue_info(task)
        previous_retries = queue_info.get("retryCount", 0)
        if not isinstance(previous_retries, int):
            try:
                previous_retries = int(previous_retries)  # type: ignore[arg-type]
            except Exception:
                previous_retries = 0
        queue_info.clear()
        now_iso = datetime.utcnow().isoformat() + "Z"
        queue_info["enqueuedAt"] = now_iso
        queue_info["retryCount"] = (
            previous_retries + 1 if previous_status in {"failed", "cancelled"} else previous_retries
        )
        task.queue_info = queue_info

        add_event(task, "queued", "Task queued for execution")
        session.commit()
    finally:
        session.close()

    research_task_queue.put(
        {"task_id": request.taskId, "prompt": prompt, "model": request.model}
    )
    logger.info(f"Task {request.taskId} enqueued for execution.")
    return {"taskId": request.taskId, "status": "queued"}


@app.get("/api/research/tasks/{task_id}")
async def get_research_task_status(task_id: str):
    """
    查询研究任务最新状态
    """
    session = SessionLocal()
    try:
        task: Optional[ResearchTask] = (
            session.query(ResearchTask)
            .filter(ResearchTask.task_id == task_id)
            .one_or_none()
        )
        if not task:
            raise HTTPException(status_code=404, detail="Research task not found")

        progress = serialize_progress(task.progress)
        queue_info = serialize_queue_info(task.queue_info)
        created_at = (
            task.created_at.isoformat() + "Z" if task.created_at else None
        )
        updated_at = (
            task.updated_at.isoformat() + "Z" if task.updated_at else None
        )
        started_at = (
            task.started_at.isoformat() + "Z" if task.started_at else None
        )
        completed_at = (
            task.completed_at.isoformat() + "Z" if task.completed_at else None
        )
        failed_at = (
            task.failed_at.isoformat() + "Z" if task.failed_at else None
        )

        return {
            "taskId": task.task_id,
            "status": task.status,
            "topic": task.topic,
            "progress": progress,
            "report": task.report,
            "queueInfo": queue_info,
            "startedAt": started_at,
            "completedAt": completed_at,
            "failedAt": failed_at,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
    finally:
        session.close()


# === Phase 2: 标准化 API 接口 ===

@app.get("/api/health", response_model=ApiResponse)
async def health_check_v2():
    """
    健康检查端点（Phase 2 标准化版本）

    返回服务状态信息，用于：
    1. 监控服务是否正常运行
    2. 防止服务休眠（cron-job.org 定期 ping）
    3. 负载均衡器健康检查

    性能要求：< 100ms

    返回：
        ApiResponse with HealthResponse data
        - status: "ok" | "degraded" | "error"
        - timestamp: ISO 格式时间戳
        - version: API 版本号

    状态码：
        200: 服务正常
        503: 服务不可用（但进程仍在运行）
    """
    import time
    start_time = time.time()

    try:
        # 检查数据库连接（可选）
        # 如果数据库连接失败，仍然返回 200，但 status 为 "degraded"
        db_ok = True
        try:
            from sqlalchemy import text
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
        except Exception as e:
            logger.warning(f"⚠️ 数据库健康检查失败: {e}")
            db_ok = False

        # 计算响应时间
        elapsed_ms = (time.time() - start_time) * 1000

        # 构建响应
        health_data = HealthResponse(
            status="ok" if db_ok else "degraded",
            timestamp=datetime.utcnow().isoformat() + "Z",
            version="2.0.0"
        )

        logger.info(f"✅ 健康检查成功 ({elapsed_ms:.1f}ms)")

        return ApiResponse(
            success=True,
            data=health_data.dict()
        )

    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ApiResponse(
                success=False,
                error="Service temporarily unavailable"
            ).dict()
        )


@app.get("/api/models", response_model=ApiResponse)
async def get_models():
    """
    获取可用模型列表

    返回系统中配置的所有 AI 模型信息，包括：
    - 模型名称和标识符
    - 提供商信息
    - 上下文窗口大小
    - 是否支持流式输出

    这个接口：
    1. 用于前端展示可用模型
    2. 帮助用户了解系统能力
    3. 支持动态模型选择（未来功能）

    性能要求：< 200ms（静态数据）

    返回：
        ApiResponse with list of ModelInfo

    示例响应：
        {
            "success": true,
            "data": {
                "models": [
                    {
                        "name": "deepseek:deepseek-chat",
                        "provider": "deepseek",
                        "description": "DeepSeek Chat - 高性价比通用对话模型",
                        "context_window": 65536,
                        "supports_streaming": true
                    },
                    ...
                ]
            }
        }
    """
    from src.config import ModelConfig

    try:
        # 构建模型信息列表
        models = [
            ModelInfo(
                name=ModelConfig.PLANNER_MODEL,
                provider=ModelConfig.PLANNER_MODEL.split(":")[0],
                description="DeepSeek Reasoner - 复杂推理和规划任务专用模型",
                context_window=65536,
                supports_streaming=True
            ),
            ModelInfo(
                name=ModelConfig.RESEARCHER_MODEL,
                provider=ModelConfig.RESEARCHER_MODEL.split(":")[0],
                description="DeepSeek Chat - 研究和信息搜集",
                context_window=65536,
                supports_streaming=True
            ),
            ModelInfo(
                name=ModelConfig.WRITER_MODEL,
                provider=ModelConfig.WRITER_MODEL.split(":")[0],
                description="DeepSeek Chat - 内容生成和写作",
                context_window=65536,
                supports_streaming=True
            ),
            ModelInfo(
                name=ModelConfig.EDITOR_MODEL,
                provider=ModelConfig.EDITOR_MODEL.split(":")[0],
                description="DeepSeek Chat - 内容审核和编辑",
                context_window=65536,
                supports_streaming=True
            ),
            ModelInfo(
                name=ModelConfig.FALLBACK_MODEL,
                provider=ModelConfig.FALLBACK_MODEL.split(":")[0],
                description="GPT-4O Mini - 高可靠性降级模型",
                context_window=128000,
                supports_streaming=True
            ),
        ]

        # 去重（相同的模型可能被多个 agent 使用）
        unique_models = {}
        for model in models:
            if model.name not in unique_models:
                unique_models[model.name] = model

        logger.info(f"📋 返回 {len(unique_models)} 个模型信息")

        return ApiResponse(
            success=True,
            data={
                "models": [m.dict() for m in unique_models.values()],
                "total": len(unique_models),
                "default_model": ModelConfig.RESEARCHER_MODEL
            }
        )

    except Exception as e:
        logger.error(f"❌ 获取模型列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve models: {str(e)}"
        )


@app.post("/generate_report")
def generate_report(req: PromptRequest):
    """
    生成报告端点 - 接收用户的研究主题并启动后台任务
    
    参数:
        req: 包含研究主题的请求对象
    
    返回:
        包含任务 ID 的字典
    """
    # 生成唯一的任务 ID
    task_id = str(uuid.uuid4())
    
    # 在数据库中创建任务记录
    db = SessionLocal()
    db.add(Task(id=task_id, prompt=req.prompt, status="running"))
    db.commit()
    db.close()

    # 初始化任务进度跟踪
    task_progress[task_id] = {"steps": []}
    
    # 使用规划代理生成执行步骤
    initial_plan_steps = planner_agent(req.prompt)
    
    # 为每个步骤创建进度跟踪条目
    for step_title in initial_plan_steps:
        task_progress[task_id]["steps"].append(
            {
                "title": step_title,
                "status": "pending",  # 待执行
                "description": "等待执行",
                "substeps": [],
            }
        )

    # 在后台线程中启动代理工作流
    thread = threading.Thread(
        target=run_agent_workflow, args=(task_id, req.prompt, initial_plan_steps)
    )
    thread.start()
    return {"task_id": task_id}


@app.get("/task_progress/{task_id}")
def get_task_progress(task_id: str):
    """
    获取任务进度端点 - 返回任务的实时执行进度
    
    参数:
        task_id: 任务唯一标识符
    
    返回:
        包含步骤列表的进度信息
    """
    return task_progress.get(task_id, {"steps": []})


@app.get("/task_status/{task_id}")
def get_task_status(task_id: str):
    """
    获取任务状态端点 - 返回任务的最终状态和结果
    
    参数:
        task_id: 任务唯一标识符
    
    返回:
        包含任务状态和结果的字典
    """
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    db.close()
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    return {
        "status": task.status,
        "result": json.loads(task.result) if task.result else None,
    }


def format_history(history):
    """
    格式化执行历史 - 将历史记录转换为可读的字符串格式
    
    参数:
        history: 执行历史列表 [(标题, 描述, 输出), ...]
    
    返回:
        格式化的历史字符串
    """
    return "\n\n".join(
        f"🔹 {title}\n{desc}\n\n📝 输出:\n{output}" for title, desc, output in history
    )


def run_agent_workflow(task_id: str, prompt: str, initial_plan_steps: list):
    """
    运行代理工作流 - 在后台线程中执行多代理研究任务
    
    参数:
        task_id: 任务唯一标识符
        prompt: 用户的研究主题
        initial_plan_steps: 规划代理生成的执行步骤列表
    """
    steps_data = task_progress[task_id]["steps"]
    execution_history = []

    def update_step_status(index, status, description="", substep=None):
        """
        更新步骤状态 - 更新任务进度跟踪中的步骤信息
        
        参数:
            index: 步骤索引
            status: 新状态（pending, running, done, error）
            description: 状态描述
            substep: 子步骤信息（可选）
        """
        if index < len(steps_data):
            steps_data[index]["status"] = status
            if description:
                steps_data[index]["description"] = description
            if substep:
                steps_data[index]["substeps"].append(substep)
            steps_data[index]["updated_at"] = datetime.utcnow().isoformat()

    try:
        # 遍历并执行每个计划步骤
        for i, plan_step_title in enumerate(initial_plan_steps):
            update_step_status(i, "running", f"正在执行: {plan_step_title}")

            # 执行单个代理步骤
            actual_step_description, agent_name, output = executor_agent_step(
                plan_step_title, execution_history, prompt
            )

            # 将执行结果添加到历史记录
            execution_history.append([plan_step_title, actual_step_description, output])

            # HTML 转义函数
            def esc(s: str) -> str:
                return html.escape(s or "")

            def nl2br(s: str) -> str:
                return esc(s).replace("\n", "<br>")

            # 更新步骤状态为完成，并添加详细的执行信息
            update_step_status(
                i,
                "done",
                f"已完成: {plan_step_title}",
                {
                    "title": f"调用了 {agent_name}",
                    "content": f"""
<div style='border:1px solid #ccc; border-radius:8px; padding:10px; margin:8px 0; background:#fff;'>
  <div style='font-weight:bold; color:#2563eb;'>📘 用户提示</div>
  <div style='white-space:pre-wrap;'>{prompt}</div>

  <div style='font-weight:bold; color:#16a34a; margin-top:8px;'>📜 上一步</div>
  <pre style='white-space:pre-wrap; background:#f9fafb; padding:6px; border-radius:6px; margin:0;'>
{format_history(execution_history[-2:-1])}
  </pre>

  <div style='font-weight:bold; color:#f59e0b; margin-top:8px;'>🧹 当前任务</div>
  <div style='white-space:pre-wrap;'>{actual_step_description}</div>

  <div style='font-weight:bold; color:#10b981; margin-top:8px;'>✅ 输出</div>
  <!-- ⚠️ 这里不使用 <pre> 标签以保留 HTML 格式 -->
  <div style='white-space:pre-wrap;'>
{output}
  </div>
</div>
""".strip(),
                },
            )

        # 提取最终报告（最后一步的输出）
        final_report_markdown = (
            execution_history[-1][-1] if execution_history else "未生成报告。"
        )

        # 构建结果对象
        result = {"html_report": final_report_markdown, "history": steps_data}

        # 更新数据库中的任务状态
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        task.status = "done"
        task.result = json.dumps(result)
        task.updated_at = datetime.utcnow()
        db.commit()
        db.close()

    except Exception as e:
        # 处理工作流执行过程中的错误
        print(f"任务 {task_id} 的工作流错误: {e}")
        
        # 找到出错的步骤并更新其状态
        if steps_data:
            error_step_index = next(
                (i for i, s in enumerate(steps_data) if s["status"] == "running"),
                len(steps_data) - 1,
            )
            if error_step_index >= 0:
                update_step_status(
                    error_step_index,
                    "error",
                    f"执行过程中出错: {e}",
                    {"title": "错误", "content": str(e)},
                )

        # 更新数据库中的任务状态为错误
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        task.status = "error"
        task.updated_at = datetime.utcnow()
        db.commit()
        db.close()


# === Phase 2: SSE 流式接口 ===

@app.post("/api/research/stream")
async def research_stream(request: ResearchRequest):
    """
    SSE 流式研究接口（Phase 2 核心功能）

    接收研究主题，通过 Server-Sent Events (SSE) 实时推送研究进度和结果。

    工作流程：
        1. 发送 START 事件（包含 prompt）
        2. 调用 planner_agent 生成执行计划
        3. 发送 PLAN 事件（包含步骤列表）
        4. 循环执行每个步骤：
           a. 发送 PROGRESS 事件（步骤编号、总数、描述）
           b. 调用 executor_agent_step 执行步骤
        5. 发送 DONE 事件（包含最终报告）
        6. 如果出错，发送 ERROR 事件

    SSE 事件类型：
        - start: 任务开始，data: {prompt}
        - plan: 执行计划，data: {steps: [str]}
        - progress: 步骤进度，data: {step, total, message}
        - done: 任务完成，data: {report: str}
        - error: 发生错误，data: {message, step?}

    参数：
        request: ResearchRequest
            - prompt: 研究主题（必需，10-5000 字符）
            - model: 可选的模型名称

    返回：
        StreamingResponse (text/event-stream)

    响应头：
        - Content-Type: text/event-stream
        - Cache-Control: no-cache, no-transform
        - Connection: keep-alive
        - X-Accel-Buffering: no (禁用 Nginx 缓冲)

    性能要求：
        - 首个事件 (START) < 2s
        - 完整任务 < 5min
        - 支持 5 个并发连接

    错误处理：
        - 所有异常都会发送 ERROR 事件
        - 不会中断连接（客户端决定何时关闭）
        - 详细错误记录到日志

    使用示例（curl）：
        curl -X POST http://localhost:8000/api/research/stream \\
             -H "Content-Type: application/json" \\
             -d '{"prompt": "Research AI applications"}' \\
             -N

    使用示例（JavaScript）：
        const eventSource = new EventSource('/api/research/stream');
        eventSource.addEventListener('start', (e) => {
            const data = JSON.parse(e.data);
            console.log('Started:', data.prompt);
        });
        eventSource.addEventListener('progress', (e) => {
            const data = JSON.parse(e.data);
            console.log(`Step ${data.step}/${data.total}: ${data.message}`);
        });
        eventSource.addEventListener('done', (e) => {
            const data = JSON.parse(e.data);
            console.log('Report:', data.report);
            eventSource.close();
        });

    设计决策：
        - 不使用数据库（减少延迟，符合 MVP 原则）
        - 不保存历史（客户端负责记录）
        - 使用异步生成器（async generator）
        - 错误时不关闭连接（客户端控制）
    """
    logger.info(f"🚀 SSE 流式研究请求: {request.prompt[:50]}...")

    async def event_generator():
        """
        异步事件生成器

        使用 async generator 逐步生成 SSE 事件。
        这允许：
        1. 非阻塞执行
        2. 实时推送事件
        3. 自动清理资源
        """
        try:
            # === 1. START 事件 ===
            logger.info("📤 发送 START 事件")
            yield create_start_event(request.prompt)

            # === 2. PLAN 事件 - 调用 planner_agent ===
            logger.info("🧠 调用 planner_agent 生成执行计划")
            try:
                steps = planner_agent(
                    request.prompt,
                    model=request.model
                )
                logger.info(f"✅ 生成了 {len(steps)} 个执行步骤")
            except Exception as e:
                logger.error(f"❌ planner_agent 失败: {e}")
                yield create_error_event(f"Failed to generate plan: {str(e)}")
                return

            logger.info("📤 发送 PLAN 事件")
            yield create_plan_event(steps)

            # === 3. 执行步骤循环 ===
            execution_history = []

            for i, step_title in enumerate(steps):
                step_number = i + 1
                logger.info(f"📤 发送 PROGRESS 事件: {step_number}/{len(steps)}")
                yield create_progress_event(
                    step=step_number,
                    total=len(steps),
                    message=step_title
                )

                logger.info(f"⚙️  执行步骤 {step_number}: {step_title[:50]}...")
                try:
                    step_desc, agent_name, output = executor_agent_step(
                        step_title,
                        execution_history,
                        request.prompt
                    )
                    execution_history.append([step_title, step_desc, output])
                    logger.info(
                        f"✅ 步骤 {step_number} 完成，"
                        f"使用代理: {agent_name}，"
                        f"输出长度: {len(output)} 字符"
                    )
                except Exception as e:
                    logger.error(f"❌ 步骤 {step_number} 执行失败: {e}")
                    yield create_error_event(
                        message=f"Step {step_number} failed: {str(e)}",
                        step=step_number
                    )
                    return

            if execution_history:
                final_report = execution_history[-1][2]
                logger.info(f"📤 发送 DONE 事件，报告长度: {len(final_report)} 字符")
                yield create_done_event(final_report)
            else:
                logger.warning("⚠️ 执行历史为空，无法生成报告")
                yield create_error_event("No report generated")

        except Exception as e:
            logger.error(f"❌ SSE 生成器发生未处理的异常: {e}\n{traceback.format_exc()}")
            yield create_error_event(f"Internal error: {str(e)}")

    # 返回 StreamingResponse
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers=get_sse_headers()
    )
