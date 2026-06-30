# 智能新闻与 AI 问答系统 (News + RAG Agent)

一个基于 FastAPI + LangChain + Vue 3 的全栈应用，集新闻浏览、用户管理、AI 智能问答（RAG）于一体。

## 项目架构

```
├── backend/                    # AI Agent 后端服务 (端口 8001)
│   ├── app/agent/              # LangChain Agent 实现
│   ├── app/rag/                # RAG 检索增强生成 (向量检索 + 重排序)
│   ├── app/router/             # API 路由 (聊天、文档上传等)
│   ├── app/config/             # 配置文件 (YAML)
│   ├── app/prompts/            # Agent 系统提示词
│   └── main.py                 # 服务入口
│
├── FastAPIUserService/         # 用户微服务 (端口 8000)
│   ├── routers/                # 用户、新闻、收藏、历史 API
│   ├── crud/                   # 数据库操作
│   ├── models/                 # 数据模型
│   └── main.py                 # 服务入口
│
├── xwzx-news/                  # Vue 3 前端 (端口 5173)
│   ├── src/views/              # 页面组件
│   ├── src/api/                # API 接口封装
│   └── vite.config.js          # Vite 配置 (代理)
│
└── backend/data/               # 数据目录 (ChromaDB、MD5 存储)
```

## 快速开始

### 前置条件

- Python 3.12+
- Node.js 18+
- [Ollama](https://ollama.ai/)（本地嵌入模型）
- MySQL / MariaDB

### 1. 克隆并安装依赖

```bash
git clone <repo-url>
cd Agent-Langchain-RAG-FastAPI

# 后端依赖
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate    # Linux/Mac
pip install -r backend/requirements.txt

# 用户服务依赖
pip install -r FastAPIUserService/requirements.txt

# 前端依赖
cd xwzx-news
npm install
cd ..
```

### 2. 配置环境变量

创建 `.env` 文件（三个服务共用）：

```env
# 阿里云通义千问 API (Agent 模型)
ALIYUN_ACCESS_KEY_SECRET=your_api_key
ALIYUN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 数据库配置 (用户服务)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=news_db

# Redis (会话管理)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT 密钥
FASTAPI_SECRET_KEY=your_secret_key
FASTAPI_ALGORITHM=HS256

# 重排序模型路径 (Qwen3-Reranker)
RERANKER_MODEL_PATH=D:\Hugging_Face\models\Qwen3-Reranker-0.6B
```

### 3. 下载重排序模型

下载 [Qwen3-Reranker-0.6B](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B) 到本地路径，或在 `.env` 中配置 `RERANKER_MODEL_PATH`。  
> 也可启动服务时自动下载（需网络）。

### 4. 启动 Ollama 嵌入模型

```bash
ollama pull qwen3-embedding:0.6b
ollama serve
```

### 5. 启动服务

```bash
# 终端 1: 用户服务 (端口 8000)
cd FastAPIUserService
python -m uvicorn main:app --reload --port 8000

# 终端 2: Agent 后端 (端口 8001)
cd backend
python -m uvicorn backend.main:app --reload --port 8001

# 终端 3: 前端 (端口 5173)
cd xwzx-news
npm run dev
```

### 6. 访问

- 前端: http://localhost:5173
- Agent API: http://localhost:8001/docs
- 用户 API: http://localhost:8000/docs

## 核心功能

### AI 问答 (RAG)

- **混合检索**：向量检索（Chroma）+ BM25 关键词检索
- **会话隔离**：每个对话上传的文档仅在该对话中可见
- **跨会话上传**：相同文件可在不同会话中重新上传
- **重排序**：Qwen3-Reranker 对检索结果精排，取 Top 3
- **HyDE**：假设性文档嵌入增强检索
- **流式输出**：SSE 逐字符流式响应
- **Markdown 渲染**：回答以 Markdown 格式展示

### 用户管理

- 注册 / 登录 (JWT)
- 个人资料编辑（头像、昵称、简介）
- 预设头像库、本地相册上传、自定义链接

### 新闻模块

- 分类浏览、新闻详情
- 收藏 / 取消收藏
- 浏览历史记录
- 相关新闻推荐

### Agent 工具

- `rag_summary_tools` — 知识库检索与摘要
- `get_weather_tools` — 天气查询
- `what_time_is_now` — 当前时间
- `get_user_info_tools` — 用户信息
- `reorder_documents_tools` — 文档重排序

## 技术栈

| 组件 | 技术 |
|---|---|
| 前端 | Vue 3, Vant 4, Vite, Pinia, marked |
| Agent 后端 | FastAPI, LangChain, ChromaDB |
| 用户服务 | FastAPI, SQLAlchemy, MySQL |
| 嵌入模型 | Ollama + qwen3-embedding |
| 重排序 | Qwen3-Reranker (CrossEncoder) |
| LLM | 通义千问 qwen3-max (DashScope) |
| 流式 | Server-Sent Events (SSE) |
| 认证 | JWT (HTTPBearer) |

# 配置说明
# LLM 模型切换
系统支持 阿里云百炼（DashScope） 和 **Ollama（本地部署）**两种模式：

LLM_TYPE=ALIYUN：使用 Qwen3-Max 大模型 + text-embedding-v4 嵌入
LLM_TYPE=OLLAMA：使用本地 Ollama 模型
#重排序模型
下载 Qwen3-Reranker-0.6B 模型并配置 RERANKER_MODEL_PATH 路径，参考 模型配置指南。

# 故障排除
详细的故障排除指南请参考：故障排除

# 常见问题：

API Key 错误：检查 ALIYUN_ACCESS_KEY 是否正确配置
数据库连接失败：确认 MySQL / Redis 服务已启动
ChromaDB 异常：检查 chroma.yaml 中的路径配置
重排序模型加载失败：确认 RERANKER_MODEL_PATH 指向正确的模型路径
Ollama 连接失败：确认 ollama serve 已运行且模型已拉取
# 联系方式
如有任何问题或建议，欢迎提交 GitHub Issues 或联系作者：

Email: 2655609714@qq.com

QQ: 2655609714
