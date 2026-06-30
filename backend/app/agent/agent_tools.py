from datetime import datetime
from typing import List
from langchain_core.tools import tool
from backend.app.core.logger_handler import logger
from backend.app.rag.rag_service import RagService
from backend.app.rag.reorder_service import reorder_service
from backend.app.utils.auth_utils import decode_fastapi_jwt
from backend.app.agent.agent_context import current_request_session_id


@tool(description="【备选检索】当系统提示词末尾没有`知识库检索结果`时，可调用此工具从你上传的文档中检索信息。返回格式为：'摘要:[摘要内容]\n\n检索到文档列表:\n1. [文档1内容]\n2. [文档2内容]\n...'。注意：文档已自动经重排序模型优化，返回最相关的 top 3 结果。通常情况下系统已自动注入检索结果，无需调用此工具")
async def rag_summary_tools(query: str) -> str:
    """RAG 摘要工具（按当前会话隔离）"""
    session_id = current_request_session_id.get()
    result = await RagService().get_documents_and_summary(query, session_id=session_id or None)
    documents = result.get('documents', [])
    summary = result.get('summary', "")

    # 格式化返回结果
    formatted_result = f"摘要: {summary}\n\n"
    formatted_result += "检索到的文档列表（已重排序）:\n"
    for i, doc in enumerate(documents, 1):
        formatted_result += f"{i}. {doc}\n"  # 显示完整文档内容

    return formatted_result

@tool(description="用于对文档列表进行重排序，传入查询语句query和文档列表documents，返回重排序后的文档列表，包含文档内容和相似度。注意：rag_summary_tool已内置重排序功能，通常不需要单独调用此工具")
async def reorder_documents_tools(query: str, documents: List[str]) -> str:
    """重排序文档工具"""
    result = await reorder_service.reorder_documents(query, documents)
    if result["success"]:
        # 格式化返回结果
        formatted_result = await reorder_service.format_reorder_result(result["documents"])
        # 记录日志
        logger.info(formatted_result)
        return formatted_result
    else:
        return f"重排序失败: {result['error']}"

@tool(description="当用户明确问自己的ID和用户名时，从JWT中获取当前用户ID和用户名，参数为完整的JWT token字符串")
async def get_user_info_tools(token: str) -> str:
    """获取用户信息工具"""
    payload = decode_fastapi_jwt(token)
    if payload:
        user_id = payload.get("user_id", "未知")
        user_name = payload.get("user_name", "未知")
        return f"用户信息：\n- 用户ID: {user_id}\n- 用户名: {user_name}"
    else:
        return "无法解析JWT token，无法获取用户信息"

@tool(description="用于获取天气信息，需要提供城市名称作为参数，你需要从用户输入中提取城市名称，是str类型")
async def get_weather_tools(city: str) -> str:
    """获取天气工具"""
    if not city:
        return "请提供城市名称"
    return f"[{city}]的天气是晴朗的"

@tool(description="用于获取当前年月日时分的工具")
async def what_time_is_now() -> str:
    """获取当前年月日时分的工具"""
    return f"当前时间是:{datetime.now().strftime('%Y-%m-%d %H:%M')}"






