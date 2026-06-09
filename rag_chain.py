# -*- coding: utf-8 -*-
from typing import List, Dict, Optional
from knowledge_base import KnowledgeBase


try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


# 经过实测对 qwen2:1.5b 有效的 prompt 模板
RAG_PROMPT = """你是文档助手，只使用下面提供的文档内容回答用户问题，不要用自己的知识回答。

===== 文档内容 =====
{context}
===== 文档结束 =====

问题：{question}

请用简洁的中文，基于文档回答："""


class RAGQASystem:
    def __init__(
        self,
        kb: KnowledgeBase,
        model: str = "qwen2:1.5b",
        base_url: str = "http://localhost:11434",
        num_ctx: int = 4096,
        temperature: float = 0.15,
        top_k: int = 3,
    ):
        self.kb = kb
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.num_ctx = num_ctx
        self.top_k = top_k
        if not _HAS_REQUESTS:
            raise RuntimeError("请安装 requests 库")

    def _extract_doc_text(self, doc) -> str:
        if isinstance(doc, dict):
            return doc.get("text") or doc.get("page_content") or ""
        if hasattr(doc, "page_content"):
            return doc.page_content
        return str(doc)

    def _extract_source(self, doc) -> str:
        if isinstance(doc, dict):
            meta = doc.get("metadata") or {}
            return meta.get("source") or "文档"
        if hasattr(doc, "metadata") and isinstance(doc.metadata, dict):
            return doc.metadata.get("source") or "文档"
        return "文档"

    def _format_context(self, docs: List) -> str:
        parts = []
        for i, doc in enumerate(docs, 1):
            text = self._extract_doc_text(doc).strip()
            src = self._extract_source(doc)
            parts.append(f"[文档{i}] 来源: {src}\n{text}")
        return "\n\n".join(parts)

    def _contains_keyword_match(self, question: str, docs: List) -> bool:
        """判断检索结果与问题是否相关（代码层面，避免小模型自己瞎猜）。"""
        if not docs:
            return False
        all_text = "".join(self._extract_doc_text(d) for d in docs)
        import re

        tokens = set()
        for m in re.findall(r"[\u4e00-\u9fa5]{2,6}", question):
            tokens.add(m)
        for m in re.findall(r"[A-Za-z][A-Za-z0-9_+\-]{1,19}", question):
            tokens.add(m)

        stopwords = {"什么", "哪些", "如何", "怎么", "为什么", "请问", "解释", "介绍",
                     "说明", "定义", "是指", "是否", "有没有", "包括", "包含", "属于",
                     "步骤", "流程", "作用", "功能", "原理", "关系", "区别", "对比",
                     "how", "what", "why", "where", "which", "is", "are", "the", "and", "or"}
        tokens = {t for t in tokens if t.lower() not in stopwords}
        if not tokens:
            return True
        return any(t in all_text for t in tokens)

    def ask(self, question: str) -> Dict:
        if self.kb.get_chunks_count() == 0:
            return {
                "answer": "知识库为空，请先上传文档并构建知识库！",
                "source_documents": [],
            }

        try:
            docs = self.kb.search(question, k=self.top_k)
            if not docs:
                return {"answer": "文档中未找到相关答案", "source_documents": []}

            if not self._contains_keyword_match(question, docs):
                return {"answer": "文档中未找到相关答案", "source_documents": docs}

            context = self._format_context(docs)
            prompt = RAG_PROMPT.format(context=context, question=question)

            resp = _requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_ctx": self.num_ctx,
                        "top_p": 0.9,
                    },
                },
                timeout=180,
            )
            if resp.status_code != 200:
                return {
                    "answer": f"模型调用失败 (HTTP {resp.status_code})",
                    "source_documents": docs,
                }

            answer = resp.json().get("response", "").strip()
            if not answer:
                answer = "文档中未找到相关答案"

            return {
                "answer": answer,
                "source_documents": docs,
            }
        except Exception as e:
            return {
                "answer": f"问答过程中出错: {e}",
                "source_documents": [],
            }

    def clear_memory(self):
        pass


def main():
    kb = KnowledgeBase()
    qa = RAGQASystem(kb=kb)
    print(f"chunks: {qa.kb.get_chunks_count()}, sources: {qa.kb.get_sources()}")


if __name__ == "__main__":
    main()
