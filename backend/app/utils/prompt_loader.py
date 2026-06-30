from backend.app.core.logger_handler import logger
from backend.app.utils.config import prompt_config
from backend.app.utils.path_tool import get_abstract_path


def load_prompt(prompt_type: str = "main_prompt"):
    """
    加载指定类型的提示词模版

    Args:
        prompt_type:提示词类型，对应prompt_config中的键名
        - main_prompt:主要提示词
        - rag_summary_prompt: RAG摘要提示词
        - report_prompt:报告提示词
        - reorder_prompt: 文档重排序提示词
    :return: 提示词模版内容
    """
    try:
        # 检查prompt_type是否存在于配置中
        if prompt_type not in prompt_config:
            logger.error(f"[加载提示词模版]配置中不存在{prompt_type}类型的提示词")
            raise KeyError(f"配置中不存在{prompt_type}类型的提示词")
        prompt_path = get_abstract_path(prompt_config[prompt_type])
        if prompt_path is None:
            logger.error(f"配置中该文件的相对路径存在，但项目根目录不存在该文件")
            raise FileNotFoundError(f"项目根目录中不存在{prompt_path}这个文件")
    except Exception as e:
        logger.error(f"[加载提示词模版]加载{prompt_config.get(prompt_type, prompt_type)}时出错:{e}")
        raise e
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"[加载提示词模版]读取{prompt_path}时出错:{e}")
        raise e

if __name__ == "__main__":
    # print(load_prompt("report_prompt"))
    print(load_prompt("rag_summarize_prompt"))