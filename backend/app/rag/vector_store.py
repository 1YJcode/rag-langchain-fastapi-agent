import os
import asyncio
import tempfile
import aiofiles
from aiofiles import os as aio_os
from typing import List
from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from backend.app.core.logger_handler import logger
from backend.app.utils.config import chroma_config
from backend.app.utils.file_handler import listdir_allowed_type, txt_loader, pdf_loader, markdown_loader, ppt_loader, \
    word_loader, get_file_md5_hex
from backend.app.utils.path_tool import get_abstract_path
from backend.app.utils.factory import embed_model
from backend.app.rag.text_splitter import AsyncTextSplitter

class VectorStoreService:
    def __init__(self):
        persist_directory = get_abstract_path(chroma_config['persist_directory'])
        # 使用同步 Chroma，在调用时用to_thread 包裹
        self.vectors_store = Chroma(
            collection_name=chroma_config['collection_name'],
            embedding_function=embed_model,
            persist_directory=persist_directory
        )

        self.splitter = AsyncTextSplitter(
            chunk_size=chroma_config['chunk_size'],
            chunk_overlap=chroma_config['chunk_overlap'],
            separators=chroma_config['separators'],
            embedding_model=embed_model,
            similarity_threshold=chroma_config['similarity_threshold'],
            merge_max_ratio=chroma_config['merge_max_ratio']
        )




    async def get_bm25_retriever(self):
        """
        获取BM25检索器
        :param self:
        :return: BM25Retriever实例
        """
        # 从文件直接加载文档，不依赖向量数据库
        allow_file_path: tuple[str] = await listdir_allowed_type(
            chroma_config['data_path'],
            tuple(chroma_config['allow_knowledge_file_type'])
        )
        file_paths = list(allow_file_path)

        all_docs: List[Document] = []
        for file_path in file_paths:
            documents = await self.get_file_document(file_path)
            if documents:
                split_docs = await self.splitter.async_split_documents(documents)
                all_docs.extend(split_docs)

        # 创建BM25检索器
        if all_docs:
            bm25_retriever = BM25Retriever.from_documents(
                documents=all_docs,
                k=chroma_config['k']
            )
            return bm25_retriever
        else:
            return None


    async def _get_all_documents(self) -> List[Document]:
        """
        获取向量库中所有文档
        :param self:
        :return: 文档列表
        """
        # 使用同步操作获取所有文档
        all_docs = await asyncio.to_thread(
            self.vectors_store.get,
            include=['documents', 'metadatas']
        )

        # 构建Document对象列表
        documents = []
        for i, doc in enumerate(all_docs["documents"]):
            metadata = all_docs["metadatas"][i] if i <= len(all_docs["metadatas"]) else {}
            documents.append(Document(page_content=doc, metadata=metadata))

        return documents


    async def get_retriever(self, query: str = None, session_id: str = None):
        """
        获取混合检索器（向量搜当前会话文档 + BM25 搜全局知识）
        query: 查询语句，用于动态调整权重
        session_id: 会话ID，向量检索时只搜该会话上传的文档
        :return: EnsembleRetriever实例或单独的向量检索器
        """
        # 向量检索器：按 session_id 过滤（只查当前会话上传的文档）
        search_kwargs = {'k': chroma_config['k']}
        if session_id:
            search_kwargs['filter'] = {"session_id": session_id}

        vector_retriever = self.vectors_store.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs,
        )

        # BM25 检索器：搜 data/ 目录的预置文件（全局知识，不按会话过滤）
        bm25_retriever = await self.get_bm25_retriever()

        # 混合两者
        if bm25_retriever:
            weights = await self.get_dynamic_weights(query)
            ensemble_retriever = EnsembleRetriever(
                retrievers=[vector_retriever, bm25_retriever],
                weights=weights
            )
            return ensemble_retriever
        else:
            return vector_retriever


    @staticmethod
    async def get_dynamic_weights(query: str = None):
        """
        根据查询动态调整权重
        :param query: 查询语句
        :return: 权重列表[向量检索权重, BM25检索权重]
        """
        # 默认权重
        default_vector_weights = 0.5
        default_bm25_weights = 0.5

        if not query:
            return [default_vector_weights, default_bm25_weights]

        # 根据查询特征调整权重
        query_length = len(query)
        query_words = len(query.split())

        # 长查询（>50字符）更合适向量检索
        if query_length > 50:
            vector_weight = 0.7
            bm25_weight = 0.3

        # 短查询（<20字符）更适合BM25检索
        elif query_length < 20:
            vector_weight = 0.3
            bm25_weight = 0.7

        else:
            vector_weight = default_vector_weights
            bm25_weight = default_bm25_weights

        # 关键词密集的查询（词数/长度比例高）更适合BM25
        if query_words > 0:
            word_density = query_words / query_length
            if word_density > 0.1:
                bm25_weight = min(bm25_weight + 0.1, 0.7)
                vector_weight = max(vector_weight - 0.1, 0.3)

        return [vector_weight, bm25_weight]

    async def check_md5_hex(self, md5_for_check: str) -> bool:
        """
        异步检查md5
        """
        md5_path = get_abstract_path(chroma_config['md5_hex_store'])
        # 确保目录存在
        md5_dir = os.path.dirname(md5_path)
        if not await aio_os.path.exists(md5_dir):
            await aio_os.makedirs(md5_dir, exist_ok=True)

        if not await aio_os.path.exists(md5_path):
            async with aiofiles.open(md5_path, 'w', encoding="utf-8"):
                pass
            return False

        async with aiofiles.open(md5_path, 'r', encoding="utf-8") as f:
            async for line in f:
                if line.strip() == md5_for_check:
                    return True

            return False


    async def save_md5_hex(self, md5_hex: str):
        """异步保存md5"""
        async with aiofiles.open(get_abstract_path(chroma_config["md5_hex_store"]), "a", encoding="utf-8") as f:
            await f.write(md5_hex + "\n")

    async def delete_user_documents(self, user_id: str):
        """
        删除指定用户的所有文档
        :param user_id: 用户ID
        """
        try:
            # 使用同步操作删除文档
            await asyncio.to_thread(
                self.vectors_store.delete,
                where={"user_id": user_id}
            )
            logger.info(f"[向量数据库]已删除用户 {user_id} 的所有文档")
        except Exception as e:
            logger.error(f"[向量数据库]删除用户 {user_id} 的文档时出错:{e}")
            raise



    async def get_file_document(self, read_path: str) -> list[Document]:
        """异步加载文件"""
        if read_path.endswith('.txt'):
            return await txt_loader(read_path)
        elif read_path.endswith('.pdf'):
            return await pdf_loader(read_path)
        elif read_path.endswith('.md'):
            return await markdown_loader(read_path)
        elif read_path.endswith('.pptx'):
            return await ppt_loader(read_path)
        elif read_path.endswith('.docx'):
            return await word_loader(read_path)
        else:
            return []



    async def get_document(self, files: list = None, user_id: str = None, session_id: str = None):
        """
        处理文档并将其转为向量存入向量数据库
        :param files: 上传的文件列表，如果为None则从数据文件夹读取
        :param user_id: 用户ID，用于标记文档的所有者
        :param session_id: 会话ID，用于按会话隔离文档
        """

        # 确定要处理的文件列表
        file_paths = []
        if files:
            for file in files:
                # 创建临时文件，使用asyncio.to_thread 包裹
                temp_file_path = await asyncio.to_thread(
                    tempfile.NamedTemporaryFile,
                    delete=False,
                    suffix=os.path.splitext(file.filename)[1]
                )

                content = await file.read()
                await asyncio.to_thread(temp_file_path.write, content)
                await asyncio.to_thread(temp_file_path.close)
                file_paths.append(temp_file_path.name)

        else:
            # 从数据文件夹读取文件
            allowed_file_types: tuple[str] = await listdir_allowed_type(
                chroma_config['data_path'],
                tuple(chroma_config['allow_knowledge_file_type'])
            )

            file_paths = list(allowed_file_types)

        # 处理每一个文件，追踪成功数、重复数、失败原因
        success_count = 0
        duplicate_names = []
        fail_reasons = []

        for file_path in file_paths:
            # 计算MD5
            md5_hex = await get_file_md5_hex(file_path)

            # MD5 去重：同一会话内重复才跳过，不同会话允许重新上传
            md5_key = md5_hex
            if session_id:
                md5_key = f"{md5_hex}:{session_id}"

            if await self.check_md5_hex(md5_key):
                file_name = os.path.basename(file_path)
                if session_id:
                    logger.info(f"[向量数据库]文件 {file_name} 在本会话中已存在，跳过")
                    if files:
                        try:
                            os.unlink(file_path)
                        except:
                            pass
                    duplicate_names.append(file_name)
                    continue
                else:
                    logger.info(f"[向量数据库]文件 {file_path} 的md5值 {md5_hex} 已存在，跳过")
                    if files:
                        try:
                            os.unlink(file_path)
                        except:
                            pass
                    duplicate_names.append(file_name)
                    continue

            try:
                # 加载文档
                document: List[Document] = await self.get_file_document(file_path)
                if not document:
                    logger.error(f"[向量数据库]文件 {file_path} 加载内容为空，跳过")
                    if files:
                        try:
                            os.unlink(file_path)
                        except:
                            pass
                    fail_reasons.append(f"{os.path.basename(file_path)}: 文件内容加载失败")
                    continue

                # 切分文档
                document: List[Document] = await self.splitter.async_split_documents(document)
                if not document:
                    logger.error(f"[向量数据库]文件 {file_path} 切分后内容为空，跳过")
                    if files:
                        try:
                            os.unlink(file_path)
                        except:
                            pass
                    fail_reasons.append(f"{os.path.basename(file_path)}: 文本切分后为空")
                    continue

                # 添加用户ID和会话ID作为元数据（用于按会话隔离文档）
                for doc in document:
                    if user_id:
                        doc.metadata['user_id'] = user_id
                    if session_id:
                        doc.metadata['session_id'] = session_id

                # 异步写入向量库
                await asyncio.to_thread(self.vectors_store.add_documents, document)
                success_count += 1

                # 保存MD5（有 session_id 时使用组合键，实现同会话内去重）
                await self.save_md5_hex(md5_key)
                logger.info(f"[向量数据库]文件 {file_path} 已保存")

                # 如果是临时文件
                if files:
                    try:
                        os.unlink(file_path)

                    except:
                        pass

            except Exception as e:
                logger.error(f"[向量数据库]文件 {file_path} 处理时出错:{e}")
                fail_reasons.append(f"{os.path.basename(file_path)}: {str(e)}")
                # 如果是临时文件，删除
                if files:
                    try:
                        os.unlink(file_path)
                    except:
                        pass
                continue

        # 上传场景后处理
        if files:
            if success_count == 0 and not fail_reasons and duplicate_names:
                # 全部是重复文件
                dup_msg = "、".join(duplicate_names)
                raise FileExistsError(f"文件已存在，跳过: {dup_msg}")
            elif success_count == 0 and fail_reasons:
                # 全部处理失败
                error_msg = "；".join(fail_reasons)
                raise RuntimeError(f"所有文件处理失败: {error_msg}")
            else:
                if fail_reasons:
                    logger.warning(f"[向量数据库]部分文件处理失败: {fail_reasons}")
                if duplicate_names:
                    logger.info(f"[向量数据库]部分文件已存在，跳过: {duplicate_names}")



if __name__ == '__main__':
    async def main():
        store = VectorStoreService()
        await store.get_document()

        # 等待get_retriever方法完成
        retriever = await store.get_retriever()
        # 直接使用ainvoke方法，因为EnsembleRetriever的invoke可能返回协程
        results = await retriever.ainvoke("扫地")
        print(f"检索结果数量:{len(results)}")
        for result in results:
            print(result)

    asyncio.run(main())

















