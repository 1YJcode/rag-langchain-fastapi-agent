from backend.app.utils.config_handler import  loader_config
from backend.app.utils.path_tool import get_abstract_path
rag_config = loader_config(config_path=get_abstract_path("app/config/rag.yaml"))
prompt_config = loader_config(config_path=get_abstract_path("app/config/prompt.yaml"))
chroma_config = loader_config(config_path=get_abstract_path("app/config/chroma.yaml"))

if __name__ == '__main__':
    print(rag_config["chat_model_name"])
    print(prompt_config["report_prompt"])