import contextvars

"""当前请求的会话ID，用于 Agent 工具函数和 RAG 检索按会话隔离文档"""
current_request_session_id: contextvars.ContextVar[str] = contextvars.ContextVar('request_session_id', default='')
