# CLI Tips Reference

## Repository Navigation & Inspection
- `pwd`, `ls`, `ls -a`, `tree -L 2`: 快速确认当前目录与项目结构。
- `find . -name 'filename'`: 在仓库内定位目标文件。
- `rg "<keyword>" -n`: 高效搜索代码或配置关键字，显示行号。
- `sed -n '40,80p' file`, `nl -ba file`: 部分预览并附带行号，便于定位修改。

## Editing & Content Updates
- `cat <<'EOF' > path/file`: 一次性写入完整文件内容。
- `apply_patch`: 精准对文件进行增删改（推荐用于小颗粒度变更）。
- `echo "text" >> file`: 追加内容，适合追加忽略规则、脚本命令等。
- `wc -l file`, `wc -w file`: 统计行数或字数，验证文档长度要求。

## Dependency & Environment Setup
- `./scripts/setup-backend.sh`, `./scripts/setup-frontend.sh`: 初始化后端虚拟环境与前端依赖。
- `source venv/bin/activate`: 激活 Python 虚拟环境。
- `pnpm install`, `pnpm install --filter <pkg>`: 安装前端依赖（项目固定 `pnpm@9`）。
- `cp .env.example .env`, `cp ai-chatbot-main/.env.local.example ai-chatbot-main/.env.local`: 基于模板创建环境变量文件。

## Testing & Quality Checks
- 后端：`PYTHONPATH=. pytest tests/ -v`, `pytest tests/ --cov=src --cov-report=html`。
- 前端：`pnpm test:unit:run`（Vitest）、`pnpm test:e2e`（Playwright）、`pnpm test:visual`（Percy 联合 Playwright）、`pnpm test:a11y`（axe-core 扫描）、`pnpm test:perf`（Lighthouse CI）。
- Percy 运行前设置 `export NEXT_PUBLIC_ENABLE_RESEARCH_PREVIEW=true` 与 `export PERCY_TOKEN=...`，否则快照不会上传。
- 研究端到端数据测试需设置 `RUN_RESEARCH_E2E=true` 及相关 Neon 环境变量，否则测试会被跳过。
- 质量工具：`ruff check src/`, `black src/`, `pnpm lint`, `pnpm format`。
- 类型检查：`npx tsc --noEmit` 或 `pnpm exec tsc --noEmit`。

## Application Run & Debug
- 后端：`uvicorn main:app --reload --host 0.0.0.0 --port 8000`。
- 前端：`cd ai-chatbot-main && pnpm dev`。
- 综合启动：`./scripts/dev.sh` / 停止：`./scripts/stop-dev.sh`。
- API 调试：`curl http://localhost:8000/health`, `curl -X POST http://localhost:8000/api/research/stream -d ...`。

## Git Workflow & Safety
- `git status -sb`, `git diff`, `git log --oneline | head`: 检查当前改动与历史提交。
- `git add <file> && git commit -m "feat(scope): message"`: 遵循 Conventional Commits。
- 审慎命令：避免 `git reset --hard`, `rm -rf` 等破坏性操作；若必须执行需先确认。
- 添加忽略：`echo "path/to/generated/" >> .gitignore`，保持仓库整洁。
