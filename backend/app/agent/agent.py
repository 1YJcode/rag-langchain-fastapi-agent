import os, json, asyncio
from typing import Optional, List, AsyncGenerator
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langsmith import traceable
from pydantic import BaseModel


from backend.app.agent.agent_context import current_request_session_id
from backend.app.agent.agent_middleware import get_middleware
from backend.app.agent.agent_tools import rag_summary_tools, get_weather_tools, what_time_is_now, get_user_info_tools, \
    reorder_documents_tools
from backend.app.core.logger_handler import logger
from backend.app.rag.rag_service import RagService
from backend.app.utils.prompt_loader import load_prompt
from backend.app.services import session_manager as sm



class AgentFactory:
    """
    生产 Agent 工厂类
    支持：
    - 每次调用创建全新的AgentExecutor 实例
    - 动态注入工具、提示词、模型配置
    - 支持异步流式调用
    """

    def __init__(
            self,
            model: str = "qwen3-max",
            api_key: Optional[str] = None,
            default_tools: Optional[List[BaseTool]] = None,
            default_middleware: Optional[List] = None,
            default_system_prompt: Optional[str] = None
    ):
        """
        初始化工厂配置（仅配置，不创建实例）
        :param model: 默认模型名称
        :param api_key: 默认 API Key(不传则从env读取)
        :param default_tools: 默认工具列表
        :param default_middleware:
        :param default_system_prompt: 默认系统提示词
        """
        self.model = model
        self.api_key = api_key or os.getenv("CHAT_API_KEY")
        self.default_tools = default_tools or self._get_default_tools()
        self.default_middleware = default_middleware or self._get_default_middleware()
        self.default_system_prompt = default_system_prompt or self._get_default_system_prompt()

    @staticmethod
    def _get_default_tools() -> List[BaseTool]:
        """获取默认工具列表"""
        return [
            rag_summary_tools,
            get_weather_tools,
            what_time_is_now,
            get_user_info_tools,
            reorder_documents_tools
        ]

    def _get_default_middleware(self) -> List:
        """获取系统默认中间件列表"""
        return get_middleware()


    @staticmethod
    def _get_default_system_prompt() -> str:
        """获取默认系统提示词"""
        return load_prompt('main_prompt')

    def _create_chat_model(self, custom_model: Optional[str] = None):
        """内部方法：创建聊天模型实例"""
        # 使用阿里云DashScope
        api_key = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        base_url = os.getenv("ALIYUN_BASE_URL")

        return ChatTongyi(
            model=custom_model or self.model,
            api_key=api_key,
            streaming=True,
            top_p=0.7
        )

    def _create_prompt(self, custom_system_prompt: Optional[str] = None) -> ChatPromptTemplate:
        """内部方法：创建提示词模版"""
        return ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

    def create_agent_executor(
            self,
            custom_tools: Optional[List[BaseTool]] = None,
            custom_model: Optional[str] = None,
            custom_system_prompt: Optional[str] = None,
            verbose: bool = True,
            return_intermediate_steps: bool = False,
            **kwargs
    ) -> AgentExecutor:
        """
        核心工厂方法：创建全新的 AgentExecutor 实例
        每次调用都会生成新的实例，彻底避免全局状态污染

        :param custom_tools: 自定义工具列表（默认覆盖）
        :param custom_model: 自定义模型（覆盖默认）
        :param custom_system_prompt: 自定义系统提示词（默认覆盖）
        :param verbose: 是否打印详细日志
        :param return_intermediate_steps: 是否返回中间步骤
        :param kwargs: 其他参数 AgentExecutor 参数
        :return: 全新 AgentExecutor 实例
        """

        # 1. 创建组件（每次都重新创建，避免全局状态污染）
        chat_model = self._create_chat_model(custom_model)
        prompt = self._create_prompt()
        tools = custom_tools or self.default_tools
        system_prompt = custom_system_prompt or self.default_system_prompt

        # 2.创建Agent
        agent = create_tool_calling_agent(chat_model, tools, prompt)

        # 3.创建 Executor
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=verbose,
            return_intermediate_steps=return_intermediate_steps,
            **kwargs
        )


# 初始化全局工厂
agent_factory = AgentFactory()

def get_agent_executor():
    """
    获取AgentExecutor实例，用于LangGraph
    :return: AgentExecutors实例
    """
    return agent_factory.create_agent_executor()


async def get_agent_response(
        query: str,
        history: Optional[List[tuple]] = None,
        custom_tools: Optional[List[BaseTool]] = None,
        **kwargs
):
    """
    获取 Agent 响应（使用工厂创建实例）
    :param query: 用户查询
    :param history: 会话历史[(user_msg, assistance_msg), ...]
    :param custom_tools: 自定义工具（可选，用于动态切换工具）
    :param kwargs: 其他工厂参数
    :return: 响应结果
    """
    try:
        # 1.从工厂获取全新的Executor 实例
        agent_executor = agent_factory.create_agent_executor(custom_tools=custom_tools, **kwargs)

        # 2.构建聊天历史
        chat_history: List[BaseModel] = []
        if history:
            from langchain_core.messages import HumanMessage, AIMessage
            for user_msg, assistance_msg in history:
                chat_history.append(HumanMessage(user_msg))
                chat_history.append(AIMessage(assistance_msg))

        # 3.流式执行
        full_response = []
        steps = []
        async for chunk in agent_executor.astream({
            "input": query,
            "chat_history": chat_history,
            "system_prompt": agent_factory.default_system_prompt
        }):
            if "output" in chunk:
                full_response.append(chunk["output"])
            elif "intermediate_steps" in chunk:
                for action, observation in chunk["intermediate_steps"]:
                    # 记录日志
                    logger.info(f"\n\n[Agent 思考]{action.log}")
                    logger.info(f"[工具调用]{action.tool}")
                    logger.info(f"[工具输入]{action.tool_input}")
                    logger.info(f"[Agent 思考{observation}\n")
                    # 搜集步骤
                    steps.append({
                        "thought": action.tool,
                        "tool": action.tool,
                        "tool_input": action.tool_input,
                        "tool_output": observation,
                    })

        return {
            "response": "".join(full_response) if full_response else "抱歉，我无法理解你的请求。",
            "steps": steps
        }

    except Exception as e:
        logger.error(f"Agent 执行错误：{str(e)}", exc_info=True)
        return {
            "response": f"抱歉，处理您的请求时出现了错误: {str(e)}",
            "steps": []
        }


@traceable
async def get_agent_stream_response(
        query: str,
        session_id: str,
        user_id: str,
        custom_tools: Optional[List[BaseTool]] = None,
        **kwargs
) -> AsyncGenerator[str, None]:
    """
    获取 Agent 流式响应（自动执行 RAG 检索 + 重排序）
    :param query: 用户查询
    :param session_id: 会话 ID
    :param user_id: 用户 ID
    :param custom_tools: 自定义工具（可选）
    :param kwargs: 其他参数
    :return: 流式响应生成器
    """
    try:
        logger.info(f"[Agent流式响应]开始处理请求，用户ID:{user_id}，会话ID:{session_id}，查询:{query}")

        # 发送初始事件
        yield f"data: {json.dumps({'type': 'response', 'content': '', 'session_id': session_id}, ensure_ascii=False)}\n\n"

        # ========== 第二步：注入当前会话上下文 + 自动 RAG 检索 ==========
        current_request_session_id.set(session_id)

        enriched_system_prompt = agent_factory.default_system_prompt
        try:
            rag_service = RagService()
            await rag_service.initialize_retriever(query, session_id=session_id)
            rag_result = await rag_service.get_documents_and_summary(query, session_id=session_id)
            rag_summary = rag_result.get("summary", "")
            rag_docs = rag_result.get("documents", [])

            if rag_summary and "没有找到相关的信息" not in rag_summary:
                context_block = f"\n\n## 知识库检索结果（已通过重排序模型优化）\n{rag_summary}\n"
                if rag_docs:
                    context_block += "\n### 参考文档片段\n"
                    for i, doc in enumerate(rag_docs[:3], 1):
                        doc_preview = doc[:300] + "..." if len(doc) > 300 else doc
                        context_block += f"{i}. {doc_preview}\n\n"
                enriched_system_prompt = agent_factory.default_system_prompt + context_block
                logger.info(f"[RAG自动检索]成功获取{len(rag_docs)}个文档，已注入系统提示词")
        except Exception as e:
            logger.error(f"[RAG自动检索]失败:{e}", exc_info=True)

        # ========== 第三步：获取会话历史 ==========
        history = await sm.session_manager.get_history(session_id, user_id)
        logger.info(f"[Agent流式响应]获取会话历史成功，历史记录数:{len(history)}")

        # 构建聊天历史
        chat_history: List[BaseMessage] = []
        if history:
            from langchain_core.messages import HumanMessage, AIMessage
            for user_msg, assistance_msg in history:
                chat_history.append(HumanMessage(content=user_msg))
                chat_history.append(AIMessage(content=assistance_msg))

        # ========== 第三步：创建 Agent 并执行 ==========
        agent_executor = agent_factory.create_agent_executor(
            custom_tools=custom_tools,
            return_intermediate_steps=True,
            **kwargs
        )

        full_response = []
        steps = []

        yield f"data: {json.dumps({'type': 'thought', 'content': '正在分析你的问题...'}, ensure_ascii=False)}\n\n"

        async for chunk in agent_executor.astream({
            "input": query,
            "chat_history": chat_history,
            "system_prompt": enriched_system_prompt
        }):
            if "output" in chunk:
                chunk_content = chunk["output"]

                # 去重：跳过已经输出过的内容
                current_accumulated = "".join(full_response)
                if chunk_content in current_accumulated:
                    continue

                full_response.append(chunk_content)

                for char in chunk_content:
                    yield f"data: {json.dumps({'type': 'response', 'content': char}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.01)
            elif "intermediate_steps" in chunk:
                for action, observation in chunk["intermediate_steps"]:
                    logger.info(f"\n\n[Agent 思考]{action.log}")
                    logger.info(f"[工具调用]{action.tool}")
                    logger.info(f"[工具输入]{action.tool_input}")
                    logger.info(f"[工具结果]{observation}\n")
                    steps.append({
                        "thought": action.log,
                        "tool": action.tool,
                        "tool_input": action.tool_input,
                        "tool_output": observation
                    })
                    yield f"data: {json.dumps({'type': 'thought', 'content': action.log}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.01)
                    yield f"data: {json.dumps({'type': 'tool_call', 'tool': action.tool, 'input': str(action.tool_input)}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.01)
                    obs_str = str(observation)
                    if len(obs_str) > 200:
                        obs_str = obs_str[:200] + "..."
                    yield f"data: {json.dumps({'type': 'tool_result', 'content': obs_str}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.01)

        response = "".join(full_response) if full_response else "抱歉，我无法理解您的请求。"

        # 添加到会话历史
        await sm.session_manager.add_message(session_id, user_id, query, response)
        logger.info(f"[Agent流式响应]处理完成，会话ID:{session_id}")

    except Exception as e:
        logger.error(f"[Agent流式响应]处理请求失败:{str(e)}", exc_info=True)
        error_message = f"错误: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'content': error_message, 'session_id': session_id}, ensure_ascii=False)}\n\n"

    finally:
        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"








