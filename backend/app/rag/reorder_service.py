import os
import asyncio
from typing import List, Dict, Any
import torch
from dotenv import load_dotenv
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from backend.app.core.logger_handler import logger

# 加载环境变量
load_dotenv()

def check_and_download_rerank_model() -> None:
    """检查并重排序模型，在FastAPI启动时执行"""
    LOCAL_MODEL_PATH = os.getenv("RERANKER_MODEL_PATH", r"D:\Hugging_Face\models\Qwen3-Reranker-0.6B")
    HF_MODEL_NAME = "Qwen/Qwen3-Reranker-0.6B"

    try:
        if os.path.exists(LOCAL_MODEL_PATH) and os.path.isdir(LOCAL_MODEL_PATH):
            logger.info(f"检测到本地重排序模型：{LOCAL_MODEL_PATH}")
        else:
            logger.warning(f"本地模型未找到：{LOCAL_MODEL_PATH}")
            logger.info(f"开始自动下载模型{HF_MODEL_NAME}")
            os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = AutoModelForSequenceClassification.from_pretrained(
                HF_MODEL_NAME,
                cache_dir=LOCAL_MODEL_PATH
            )
            tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME, cache_dir=LOCAL_MODEL_PATH)
            model = model.to(device)
            logger.info(f"模型下载完成，使用设备：{device}")
    except Exception as e:
        logger.error(f"模型检查失败:{str(e)}")
        raise RuntimeError(f"重排序模型检查失败:{str(e)}")


class ReorderService:
    """文档重排序服务"""
    def __init__(self):
        self.LOCAL_MODEL_PATH = os.getenv("RERANKER_MODEL_PATH", r"D:\Hugging_Face\models\Qwen3-Reranker-0.6B")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model = None
        self._tokenizer = None
        self.max_seq_len = 512

    async def _get_model(self):
        """懒加载模型+分词器"""
        if self._model is None or self._tokenizer is None:
            logger.info(f"加载 Qwen3 重排序模型：{self.LOCAL_MODEL_PATH}")
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.LOCAL_MODEL_PATH,
                local_files_only=True
            )
            self._model = AutoModelForSequenceClassification.from_pretrained(
                self.LOCAL_MODEL_PATH,
                local_files_only=True
            )
            self._model = self._model.to(self.device)
            self._model.eval()
            logger.info(f"Qwen3 重排序模型加载成功，设备：{self.device}")
        return self._model, self._tokenizer

    async def reorder_documents(self, query: str, documents: List[str]) -> Dict[str, Any]:
        """对文档进行重排序（模型推理在后台线程执行，不阻塞事件循环）"""
        # 过滤空文档
        documents = [doc for doc in documents if doc and doc.strip()]
        if not documents:
            return {"success": True, "documents": [], "error": ""}

        try:
            model, tokenizer = await self._get_model()

            # 将 CPU 密集的推理任务放到线程池执行
            def _score_documents():
                scores = []
                for doc in documents:
                    pair_text = f"Query: {query}\nDocument: {doc}"
                    inputs = tokenizer(
                        pair_text,
                        truncation=True,
                        padding=True,
                        max_length=self.max_seq_len,
                        return_tensors="pt"
                    ).to(self.device)

                    with torch.no_grad():
                        outputs = model(**inputs)
                        score = outputs.logits[0, 0].cpu().item()
                    scores.append(score)
                return scores

            scores = await asyncio.to_thread(_score_documents)

            # 组装结果并降序排序
            scored_documents = [
                {"document": doc, "similarity": float(score)}
                for doc, score in zip(documents, scores)
            ]
            sorted_docs = sorted(scored_documents, key=lambda x: x["similarity"], reverse=True)

            # 只保留 TOP3 高分文档
            sorted_docs = sorted_docs[:3]

            logger.info(f"[重排序服务]重排序成功，返回 {len(sorted_docs)} 个文档")

            return {
                "success": True,
                "documents": sorted_docs,
                "error": ""
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"[重排序服务]重排序失败: {error_msg}", exc_info=True)
            return {
                "success": False,
                "documents": [],
                "error": error_msg
            }


    @staticmethod
    async def format_reorder_result(sorted_docs: List[Dict]) -> str:
        """格式化重排序结果"""
        formatted_result = "重排序后的文档列表：\n"
        for i, doc in enumerate(sorted_docs):
            formatted_result += f"{i+1}. 相似度: {doc.get('similarity', 0):.4f}\n"
            formatted_result += f"  内容: {doc.get('document', '')}\n\n"
        return formatted_result


# 全局实例
reorder_service = ReorderService()













