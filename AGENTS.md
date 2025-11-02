# Repository Guidelines / 仓库指南

## Project Structure & Module Organization / 项目结构与模块划分
- `src/` houses the FastAPI services, agent orchestration, and shared utilities; `main.py` exposes the ASGI app.  
  `src/` 目录包含 FastAPI 服务、智能体编排与公共工具，`main.py` 提供 ASGI 入口。
- `ai-chatbot-main/` contains the Next.js 15 interface with `app/` routes, shared components, and Drizzle migrations in `lib/db/`.  
  `ai-chatbot-main/` 目录为 Next.js 15 前端，`app/` 路由、共享组件及 `lib/db/` 中的 Drizzle 迁移文件都集中于此。
- `tests/` stores backend pytest suites and Playwright smoke checks, while UI Playwright assets stay in `ai-chatbot-main/playwright/`.  
  `tests/` 目录收录后端 pytest 测试与 Playwright 冒烟脚本，前端 Playwright 资源位于 `ai-chatbot-main/playwright/`。
- Helper scripts, deployment configs, and shared assets reside in `scripts/`, `docker/`, `render.yaml`, `static/`, and `templates/`.  
  运维脚本、部署配置及共享资源分别存放在 `scripts/`、`docker/`、`render.yaml`、`static/` 与 `templates/`。

## Build, Test, and Development Commands / 构建、测试与开发命令
- `./scripts/setup-backend.sh` and `./scripts/setup-frontend.sh` provision Python venv and npm/pnpm dependencies.  
  通过 `./scripts/setup-backend.sh` 与 `./scripts/setup-frontend.sh` 初始化后端虚拟环境及前端依赖。
- `./scripts/dev.sh` runs uvicorn and `next dev` together; `./scripts/stop-dev.sh` stops both services.  
  使用 `./scripts/dev.sh` 同时启动 uvicorn 与 `next dev`，`./scripts/stop-dev.sh` 负责关闭。
- Backend only: `source venv/bin/activate && uvicorn main:app --reload`.  
  仅运行后端时，激活虚拟环境后执行 `uvicorn main:app --reload`。
- Frontend only: `cd ai-chatbot-main && pnpm dev` (repo pins `pnpm@9`; npm 可在必要时使用)。  
  仅运行前端时进入 `ai-chatbot-main` 并执行 `pnpm dev`，仓库使用 `pnpm@9`，需要时可临时改用 npm。

## Coding Style & Naming Conventions / 代码风格与命名规范
- Python modules follow 4-space indentation, snake_case naming, and must pass `ruff check src/` plus `black src/`.  
  Python 代码采用四空格缩进与 snake_case 命名，并确保通过 `ruff check src/` 与 `black src/`。
- TypeScript/React favors PascalCase components and kebab-case route folders; run `pnpm lint` and `pnpm format` (Ultracite).  
  TypeScript/React 组件使用 PascalCase，路由文件夹使用 kebab-case，提交前运行 `pnpm lint` 与 `pnpm format`（Ultracite）。
- Drizzle migrations follow timestamp prefixes from `pnpm db:generate`; avoid manual edits to generated SQL.  
  Drizzle 迁移文件由 `pnpm db:generate` 生成，遵循时间戳前缀，请勿手工修改生成的 SQL。

## Testing Guidelines / 测试规范
- Backend unit tests: `PYTHONPATH=. pytest tests/ -v`; coverage via `pytest tests/ --cov=src --cov-report=html`.  
  后端单测使用 `PYTHONPATH=. pytest tests/ -v`；覆盖率通过 `pytest tests/ --cov=src --cov-report=html` 获取。
- Frontend unit suites run with `pnpm test:unit:run`; E2E checks use `pnpm test:e2e` and require `PLAYWRIGHT=True`.  
  前端单测执行 `pnpm test:unit:run`，端到端测试执行 `pnpm test:e2e`，需设置 `PLAYWRIGHT=True`。
- Place backend tests under `tests/` mirroring module paths (`test_<topic>.py`); co-locate frontend tests as `.test.tsx`.  
  新增后端测试需在 `tests/` 下按模块路径划分并命名为 `test_<主题>.py`；前端测试与组件同目录，扩展名为 `.test.tsx`。

## Commit & Pull Request Guidelines / 提交与合并请求规范
- Follow Conventional Commits (`feat(scope):`, `fix:`, `docs:`); keep scopes descriptive (e.g., `planner`, `phase4`).  
  提交信息遵循 Conventional Commits，scope 保持明确（如 `planner`、`phase4`）。
- PR descriptions should explain motivation, detail backend/frontend impact, list env changes, and attach UI screenshots or GIFs.  
  PR 描述需说明动机、列出前后端影响、罗列环境变量变更，并附关键 UI 截图或 GIF。
- Add a "Testing" checklist summarizing executed commands and link related issues or roadmap items.  
  在 PR 中添加“Testing”清单，列出已执行的命令并关联相关 issue 或路线图条目。

## Environment & Security Tips / 环境与安全提示
- Copy `.env.example` and `ai-chatbot-main/.env.local.example`; never commit secrets to version control.  
  使用 `.env.example` 与 `ai-chatbot-main/.env.local.example` 复制生成配置文件，勿将密钥提交到版本库。
- Run `./scripts/check-env.sh` to validate required variables and use `pnpm db:pull` / `npm run db:pull` before pushing schema updates.  
  提交前执行 `./scripts/check-env.sh` 确认环境变量齐全，并通过 `pnpm db:pull` / `npm run db:pull` 同步最新数据库结构。
