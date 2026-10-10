# ai-agent-bootcamp

面向设备运维场景的 AI Agent 工程练习仓库。

## 主线项目

- P1 特种设备运维知识库问答（RAG）
- P2 设备巡检工单 Agent（LangGraph + MCP + FastAPI）
- P3 垂直领域 QLoRA 微调（Qwen2.5-1.5B）

## 技术栈

- Python 3.12（uv 管理，版本锁定）
- 代码检查 ruff，测试 pytest

## 目录

- `src/calc/` 计算模块（类型注解 + 异常捕获 + 日志）
- `src/utils/` 日志配置
- `tests/` 单元测试
- `main.py` 入口示例

## 运行

```bash
uv sync
uv run pytest
uv run python main.py
```
