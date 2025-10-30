"""
推荐的项目改进方案
结合 aisuite 的灵活性 + 生产级架构
"""

# ========== 1. 智能模型选择 ==========
from aisuite import Client

class SmartAgent:
    """根据任务类型自动选择最佳模型"""
    
    MODEL_CONFIGS = {
        "planning": {
            "model": "openai:o1-mini",  # 推理能力强
            "temperature": 1,
            "use_case": "复杂规划任务"
        },
        "research": {
            "model": "anthropic:claude-3-5-sonnet-20241022",  # 工具调用最强
            "temperature": 0,
            "max_turns": 5,
            "use_case": "需要多次工具调用的研究任务"
        },
        "writing": {
            "model": "openai:gpt-4o",  # 写作质量高
            "temperature": 0.7,
            "use_case": "创意写作、报告生成"
        },
        "editing": {
            "model": "anthropic:claude-3-5-sonnet-20241022",  # 批判性思维强
            "temperature": 0,
            "use_case": "审查、改进文本"
        },
        "simple_qa": {
            "model": "openai:gpt-4o-mini",  # 成本低
            "temperature": 0,
            "use_case": "简单问答"
        }
    }
    
    def __init__(self):
        self.client = Client()
    
    def execute(self, task_type: str, prompt: str, **kwargs):
        config = self.MODEL_CONFIGS[task_type]
        
        return self.client.chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=config.get("temperature", 0),
            **kwargs
        )


# ========== 2. 生产级异步任务处理 ==========
from celery import Celery
from celery.result import AsyncResult

celery_app = Celery(
    'research_agent',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/1'
)

@celery_app.task(bind=True, max_retries=3)
def run_research_workflow(self, task_id: str, prompt: str):
    """
    生产级工作流执行
    - 支持分布式执行
    - 自动重试
    - 进度追踪
    """
    agent = SmartAgent()
    
    try:
        # 1. 规划阶段
        self.update_state(state='PROGRESS', meta={'step': 'planning', 'progress': 10})
        plan = agent.execute('planning', f"制定研究计划: {prompt}")
        
        # 2. 研究阶段
        self.update_state(state='PROGRESS', meta={'step': 'research', 'progress': 30})
        research_data = agent.execute(
            'research',
            f"执行研究: {plan}",
            tools=[tavily_tool, arxiv_tool, wikipedia_tool],
            max_turns=5
        )
        
        # 3. 写作阶段
        self.update_state(state='PROGRESS', meta={'step': 'writing', 'progress': 60})
        draft = agent.execute('writing', f"撰写报告: {research_data}")
        
        # 4. 编辑阶段
        self.update_state(state='PROGRESS', meta={'step': 'editing', 'progress': 80})
        final_report = agent.execute('editing', f"改进报告: {draft}")
        
        self.update_state(state='PROGRESS', meta={'step': 'done', 'progress': 100})
        
        return {
            "status": "success",
            "report": final_report,
            "metadata": {
                "plan": plan,
                "research_sources": len(research_data)
            }
        }
    
    except Exception as e:
        # 自动重试
        self.retry(exc=e, countdown=60)  # 1分钟后重试


# ========== 3. FastAPI 改进版 ==========
from fastapi import FastAPI, BackgroundTasks, WebSocket
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

# 方案 A: 使用 Celery（推荐）
@app.post("/generate_report")
async def generate_report_celery(req: PromptRequest):
    """使用 Celery 处理异步任务"""
    task = run_research_workflow.delay(str(uuid.uuid4()), req.prompt)
    
    return {
        "task_id": task.id,
        "status_url": f"/task_status/{task.id}"
    }

@app.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    task = AsyncResult(task_id, app=celery_app)
    
    if task.state == 'PENDING':
        response = {
            "state": task.state,
            "status": "任务等待中..."
        }
    elif task.state == 'PROGRESS':
        response = {
            "state": task.state,
            "current_step": task.info.get('step', ''),
            "progress": task.info.get('progress', 0)
        }
    elif task.state == 'SUCCESS':
        response = {
            "state": task.state,
            "result": task.result
        }
    else:
        response = {
            "state": task.state,
            "error": str(task.info)
        }
    
    return response


# 方案 B: WebSocket 实时流式输出
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """实时流式对话"""
    await websocket.accept()
    
    try:
        while True:
            # 接收用户消息
            data = await websocket.receive_json()
            prompt = data.get("message")
            
            # 流式响应
            agent = SmartAgent()
            
            await websocket.send_json({
                "type": "status",
                "content": "正在思考..."
            })
            
            # 模拟流式输出（实际需要 LLM 支持）
            response = agent.execute('simple_qa', prompt)
            
            # 分块发送
            for chunk in response.split():
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk + " "
                })
                await asyncio.sleep(0.05)  # 模拟打字效果
            
            await websocket.send_json({
                "type": "done"
            })
    
    except Exception as e:
        await websocket.close()


# 方案 C: Server-Sent Events（更简单）
@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """SSE 流式响应"""
    
    async def event_generator():
        agent = SmartAgent()
        
        yield f"data: {json.dumps({'type': 'status', 'content': '开始处理...'})}\n\n"
        
        # 调用 LLM（需要支持流式）
        response = agent.execute('simple_qa', req.message)
        
        # 分块发送
        for chunk in response.split():
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            await asyncio.sleep(0.05)
        
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


# ========== 4. 缓存优化 ==========
import redis
import hashlib

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def cache_llm_call(ttl=3600):
    """缓存 LLM 调用结果"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = hashlib.md5(
                f"{func.__name__}:{str(args)}:{str(kwargs)}".encode()
            ).hexdigest()
            
            # 尝试从缓存获取
            cached = redis_client.get(f"llm:{cache_key}")
            if cached:
                print(f"✅ 缓存命中: {cache_key[:8]}...")
                return json.loads(cached)
            
            # 调用实际函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            redis_client.setex(
                f"llm:{cache_key}",
                ttl,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator


# ========== 5. 监控与日志 ==========
from prometheus_client import Counter, Histogram
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus 指标
llm_calls = Counter(
    'llm_calls_total',
    'Total LLM API calls',
    ['model', 'task_type', 'status']
)

llm_latency = Histogram(
    'llm_latency_seconds',
    'LLM API call latency',
    ['model', 'task_type']
)

def track_llm_call(task_type: str):
    """装饰器：追踪 LLM 调用"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            model = kwargs.get('model', 'unknown')
            
            try:
                result = await func(*args, **kwargs)
                
                llm_calls.labels(
                    model=model,
                    task_type=task_type,
                    status='success'
                ).inc()
                
                logger.info(f"✅ LLM call succeeded: {task_type} with {model}")
                
                return result
            
            except Exception as e:
                llm_calls.labels(
                    model=model,
                    task_type=task_type,
                    status='error'
                ).inc()
                
                logger.error(f"❌ LLM call failed: {task_type} with {model} - {e}")
                raise
            
            finally:
                duration = time.time() - start_time
                llm_latency.labels(
                    model=model,
                    task_type=task_type
                ).observe(duration)
        
        return wrapper
    return decorator


# ========== 使用示例 ==========
@track_llm_call('research')
@cache_llm_call(ttl=7200)
async def research_with_monitoring(prompt: str):
    agent = SmartAgent()
    return agent.execute('research', prompt, tools=[...], max_turns=5)
