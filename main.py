"""
主应用程序 - 多代理研究报告生成系统的 Web 服务
本文件实现了一个 FastAPI Web 应用，提供：
1. 用户界面用于提交研究主题
2. 后台任务处理系统
3. 实时进度跟踪
4. 数据库持久化
"""

import os
import uuid
import json
import threading
from datetime import datetime
from typing import Optional, Literal
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Text, DateTime, String
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

from src.planning_agent import planner_agent, executor_agent_step

import html, textwrap

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


# 删除现有表（开发环境）
try:
    Base.metadata.drop_all(bind=engine)
except Exception as e:
    print(f"❌ 数据库删除失败: {e}")

# 创建数据库表
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"❌ 数据库创建失败: {e}")

# === FastAPI 应用设置 ===
app = FastAPI()
# 添加 CORS 中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
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


@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    """
    首页路由 - 返回主界面 HTML
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api", response_class=JSONResponse)
def health_check(request: Request):
    """
    健康检查端点 - 用于验证服务是否正常运行
    """
    return {"status": "ok"}


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
