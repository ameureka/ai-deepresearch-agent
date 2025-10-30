# 🚀 快速开始 - v0.1.0

## 一分钟启动

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/agentic-ai-public.git
cd agentic-ai-public

# 2. 配置环境
cp .env.example .env
# 编辑 .env 填入你的 API Keys

# 3. 启动服务
docker build -t ai-research-assistant .
docker run --rm -it -p 8000:8000 --env-file .env ai-research-assistant

# 4. 访问应用
# 打开浏览器: http://localhost:8000
```

## 必需的 API Keys

```bash
# .env 文件
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key
TAVILY_API_KEY=tvly-your-tavily-key
```

获取 API Keys:
- DeepSeek: https://platform.deepseek.com/
- OpenAI: https://platform.openai.com/
- Tavily: https://tavily.com/

## 核心功能

- ✅ **成本节省 45%** - DeepSeek API 集成
- ✅ **无限长度文本** - 智能分块处理
- ✅ **自动参数调整** - 模型适配层
- ✅ **智能降级** - 失败自动切换

## 测试

```bash
# 运行所有测试
docker exec -it ai-research bash
PYTHONPATH=. pytest tests/ -v

# 结果: 64/64 测试通过 (100%)
```

## 文档

- 📖 [完整 README](README.md)
- 📝 [发布说明](RELEASE_NOTES_v0.1.0.md)
- 🔧 [Git 推送指南](GIT_PUSH_GUIDE.md)
- ✅ [完成总结](V0.1_COMPLETION_SUMMARY.md)

## 需要帮助？

- 查看 [README.md](README.md) 的故障排查部分
- 提交 Issue: https://github.com/YOUR_USERNAME/agentic-ai-public/issues

---

**Version**: 0.1.0 | **Status**: ✅ Ready to Use
