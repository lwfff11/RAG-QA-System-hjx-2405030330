from langchain_ollama import OllamaLLM
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from knowledge_base import KnowledgeBase


class RAGQASystem:
    def __init__(self, model: str = "deepseek-r1:7b"):
        self.kb = KnowledgeBase()
        self.llm = OllamaLLM(
            model=model,
            temperature=0.7,
            base_url="http://localhost:11434"
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        self.qa_chain = None
        self._build_chain()
    
    def _build_chain(self):
        retriever = self.kb.get_retriever(k=3)
        
        if retriever is None:
            self.qa_chain = None
            return
        
        system_prompt = """你是一个基于文档的智能问答助手。请根据提供的参考文档回答用户的问题。

参考文档：
{context}

用户问题：{question}

回答要求：
1. 请仅基于提供的参考文档内容回答问题
2. 如果文档中没有相关信息，请明确说"文档中未找到相关答案"
3. 回答要简洁明了，重点突出
4. 如果需要，可以引用文档中的具体内容

现在，请回答用户的问题。"""
        
        prompt = PromptTemplate(
            template=system_prompt,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": prompt}
        )
    
    def ask(self, question: str) -> dict:
        if self.qa_chain is None:
            return {
                "answer": "知识库为空，请先添加文档！",
                "source_documents": []
            }
        
        try:
            result = self.qa_chain.invoke({"question": question})
            return {
                "answer": result["answer"],
                "source_documents": result.get("source_documents", [])
            }
        except Exception as e:
            return {
                "answer": f"问答过程中出错: {str(e)}",
                "source_documents": []
            }
    
    def clear_memory(self):
        self.memory.clear()
    
    def rebuild_chain(self):
        self._build_chain()


def main():
    print("=" * 50)
    print("RAG 问答系统 (命令行版)")
    print("=" * 50)
    
    qa_system = RAGQASystem()
    
    print(f"当前知识库文档数量: {qa_system.kb.get_chunks_count()}")
    print(f"当前知识库来源: {qa_system.kb.get_sources()}")
    print()
    print("请先添加文档到知识库，然后可以提问。")
    print("输入 'quit' 或 'exit' 退出程序。")
    print("输入 'clear' 清空对话记忆。")
    print("=" * 50)
    print()
    
    while True:
        question = input("请输入问题: ").strip()
        
        if question.lower() in ['quit', 'exit', '退出']:
            print("再见！")
            break
        
        if question.lower() == 'clear':
            qa_system.clear_memory()
            print("对话记忆已清空！")
            continue
        
        if not question:
            continue
        
        print("\n正在思考...")
        result = qa_system.ask(question)
        
        print(f"\n回答: {result['answer']}")
        
        if result['source_documents']:
            print("\n参考文档:")
            for i, doc in enumerate(result['source_documents'], 1):
                print(f"\n[{i}] 来源: {doc.metadata.get('source', 'unknown')}")
                print(f"内容片段: {doc.page_content[:150]}...")
        
        print()
        print("-" * 50)
        print()


if __name__ == "__main__":
    main()