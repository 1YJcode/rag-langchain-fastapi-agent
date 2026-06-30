from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import uuid

from backend.app.agent.agent import get_agent_stream_response
from backend.app.core.rate_limit import rate_limit
from backend.app.core.success_response import success_response
from backend.app.router.chat_service import ChatService, get_router_service
from backend.app.schemas.models import QueryRequest, RAGResponse, SessionResponse, ReorderResponse, ReorderRequest, \
    RAGRequest
from backend.app.utils.auth_utils import get_current_user_id

chat_router = APIRouter(prefix="/api", tags=["api"])


@chat_router.post("/agent/query/stream")
async def query_stream(
        request: QueryRequest,
        user_id: str = Depends(get_current_user_id),
        _: None = Depends(rate_limit(limit=100, window=60))
):
    """查询Agent流式响应"""
    # 如果没有提供session_id，自动生成一个
    session_id = request.session_id or str(uuid.uuid4())

    # 直接调用get_agent_stream_response函数
    return StreamingResponse(
        get_agent_stream_response(request.query, session_id, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@chat_router.post("/rag/query", response_model=RAGResponse)
async def query_rag(
        request: RAGRequest,
        router_service: ChatService = Depends(get_router_service),
        _: None = Depends(rate_limit(limit=15, window=60))
):
    """RAG检索"""
    response = await router_service.handle_rag_query(request.query)
    return success_response(data=RAGResponse(response=response))

@chat_router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, user_id: str = Depends(get_current_user_id), router_service: ChatService = Depends(get_router_service)):
    """获取会话信息，使用user_id验证"""
    history = await router_service.handle_get_session(session_id, user_id)
    # 兼容处理：如果返回的是 dict 包装，提取列表
    if isinstance(history, dict):
        history = history.get("history", [])
    return success_response(data=SessionResponse(session_id=session_id, history=history))

@chat_router.delete("/session/{session_id}")
async def delete_session(session_id: str, user_id: str = Depends(get_current_user_id), router_service: ChatService = Depends(get_router_service)):
    """删除会话"""
    await router_service.handle_delete_session(session_id, user_id)
    return success_response(message=f"会话{session_id}删除成功")

@chat_router.get("/sessions")
async def get_all_sessions(
    user_id: str = Depends(get_current_user_id),
    router_service: ChatService = Depends(get_router_service)
):
    """获取当前用户的所有会话（含标题）"""
    sessions = await router_service.handle_get_user_sessions(user_id, user_id)
    # 返回完整的会话信息（id, title, created_at, updated_at）
    return success_response(data={"sessions": sessions})


@chat_router.get("/sessions/{session_id}")
async def get_user_sessions(user_id: str, current_user_id: str = Depends(get_current_user_id), router_service: ChatService = Depends(get_router_service)):
    """获取用户所有会话ID"""
    session_ids = await router_service.handle_get_user_sessions(user_id, current_user_id)
    return success_response(data={"sessions": session_ids})


@chat_router.post("/vector/add/single")
async def add_single_vector(
        file: UploadFile = File(...),
        session_id: Optional[str] = Form(None),
        user_id: str = Depends(get_current_user_id),
        router_service: ChatService = Depends(get_router_service),
        _: None = Depends(rate_limit(limit=5, window=60))
):
    """上传文件，将文件保存到向量数据库，仅支持TXT和PDF"""
    result = await router_service.handle_add_vector_single(file, user_id, session_id=session_id)
    is_dup = result.get("status") == "duplicate"
    return success_response(
        data={"ok": [] if is_dup else [result["filename"]], "duplicates": [result["filename"]] if is_dup else []},
        message=f"文件 {result['filename']} 已{'存在跳过' if is_dup else '成功上传'}"
    )


@chat_router.post("/vector/add/multiple")
async def add_multiple_vectors(
        files: List[UploadFile] = File(..., description="要上传的文件列表，仅支持PDF和TXT格式"),
        session_id: Optional[str] = Form(None),
        user_id: str = Depends(get_current_user_id),
        router_service: ChatService = Depends(get_router_service),
        _: None = Depends(rate_limit(limit=3, window=60))
):
    """上传多个文件，将文件保存到向量数据库，仅支持TXT和PDF"""
    results = await router_service.handle_add_vector_multiple(files, user_id, session_id=session_id)
    ok_files = [r["filename"] for r in results if r["status"] == "ok"]
    dup_files = [r["filename"] for r in results if r["status"] == "duplicate"]

    msg_parts = []
    if ok_files:
        msg_parts.append(f"新增 {len(ok_files)} 个文件")
    if dup_files:
        msg_parts.append(f"{len(dup_files)} 个文件已存在跳过")

    return success_response(
        data={"ok": ok_files, "duplicates": dup_files},
        message="，".join(msg_parts) if msg_parts else "处理完成"
    )

@chat_router.delete("/vector/clean")
async def clean_user_vector(user_id: str = Depends(get_current_user_id), router_service: ChatService = Depends(get_router_service)):
    """删除用户上传的所有向量"""
    await router_service.clean_user_upload(user_id)
    return success_response(message="已成功删除用户上传的所有向量")


@chat_router.post("/reorder", response_model=ReorderResponse)
async def reorder_documents(
        request: ReorderRequest,
        router_service: ChatService = Depends(get_router_service),
        _: None = Depends(rate_limit(limit=20, window=60))
):
    """使用Ollama本地嵌入模型对文档进行中文排序"""
    sorted_docs = await router_service.handle_reorder(request.query, request.documents)
    return success_response(data=ReorderResponse(documents=sorted_docs))













