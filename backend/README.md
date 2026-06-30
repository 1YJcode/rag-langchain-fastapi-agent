# Backend — AI Agent 服务

LangChain Agent 后端，提供 RAG 检索增强生成、文档管理、会话管理等 API。

## 技术栈

| 组件 | 说明 |
|---|---|
| FastAPI | Web 框架，端口 8001 |
| LangChain | Agent 编排与工具调用 |
| ChromaDB | 向量数据库 |
| LangChain-Classic | AgentExecutor (create_tool_calling_agent) |
| Ollama | 本地嵌入模型 (qwen3-embedding) |
| Qwen3-Reranker | 重排序模型 (HuggingFace) |
| 通义千问 qwen3-max | 主语言模型 (DashScope API) |

## 项目结构

```
backend/
├── app/
│   ├── agent/
│   │   ├── agent.py              # Agent 工厂 + 流式响应
│   │   ├── agent_context.py       # 请求上下文 (session_id)
│   │   ├── agent_middleware.py    # 中间件
│   │   └── agent_tools.py         # Agent 工具定义
│   ├── rag/
│   │   ├── rag_service.py         # RAG 主服务 (检索+重排序+摘要)
│   │   ├── reorder_service.py     # Qwen3-Reranker 重排序
│   │   ├── text_splitter.py       # 文本分割器
│   │   └── vector_store.py        # Chroma 向量库操作
│   ├── router/
│   │   ├── chat.py                # API 路由定义
│   │   ├── chat_service.py        # 路由业务逻辑
│   │   ├── health.py              # 健康检查
│   │   └── user.py                # 用户路由
│   ├── config/
│   │   ├── chroma.yaml            # Chroma 配置 (chunk_size, etc.)
│   │   ├── rag.yaml               # RAG 模型配置
│   │   └── prompt.yaml            # 提示词路径配置
│   ├── prompts/
│   │   ├── main_prompt.txt        # Agent 系统提示词
│   │   ├── rag_summarize.txt      # RAG 摘要提示词
│   │   └── reorder_prompt.txt     # 重排序提示词
│   ├── db/
│   │   ├── db_config.py           # 数据库配置
│   │   └── redis_config.py        # Redis 配置
│   ├── models/
│   │   └── chat_history.py        # 会话数据模型
│   ├── services/
│   │   └── database_session_manager.py  # 数据库会话管理器
│   ├── utils/
│   │   ├── auth_utils.py          # JWT 验证
│   │   ├── config.py              # 配置加载
│   │   ├── factory.py             # 模型工厂
│   │   ├── file_handler.py        # 文件加载 (txt/pdf/docx/pptx/md)
│   │   └── prompt_loader.py       # 提示词加载
│   └── core/
│       ├── rate_limit.py          # 限流中间件
│       ├── success_response.py    # 成功响应格式
│       └── logger_handler.py      # 日志
├── data/                          # 运行时数据
│   └── chromadb/                  # Chroma 持久化目录
└── main.py                        # 服务入口
```

## API 接口

### 聊天

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/agent/query/stream` | Agent 流式问答 (SSE) |
| POST | `/api/rag/query` | 直接 RAG 检索 |

### 会话管理

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/sessions` | 获取当前用户所有会话 |
| GET | `/api/session/{id}` | 获取会话历史 |
| DELETE | `/api/session/{id}` | 删除会话 |

### 文档上传

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/vector/add/single` | 上传单个文件 (支持 txt/pdf/docx/md/pptx) |
| POST | `/api/vector/add/multiple` | 批量上传 |
| DELETE | `/api/vector/clean` | 清除当前用户的所有向量 |

### 重排序

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/reorder` | 文档重排序 |

## RAG 流程

```
用户提问
  ↓
混合检索:
  ├── 向量检索 (Chroma, 按 session_id 过滤)
  └── BM25 关键词检索 (全局预置知识)
  ↓
EnsembleRetriever 合并结果
  ↓
Qwen3-Reranker 重排序 → Top 3
  ↓
LLM 生成摘要
  ↓
注入 Agent 系统提示词
  ↓
Agent 生成最终回答 (Markdown)
```

## 配置

主要配置在 `app/config/` 目录：

- **chroma.yaml**: `chunk_size: 200`, `chunk_overlap: 20`, `k: 5`
- **rag.yaml**: 模型名称、嵌入模型名称
- **prompt.yaml**: 提示词文件路径
