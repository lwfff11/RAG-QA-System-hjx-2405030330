
import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document


class KnowledgeBase:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.vectorstore = None
        self._init_vectorstore()
    
    def _init_vectorstore(self):
        if os.path.exists(self.persist_directory) and len(os.listdir(self.persist_directory)) &gt; 0:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            self.vectorstore = None
    
    def load_document(self, file_path: str) -&gt; List[Document]:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            loader = PyPDFLoader(file_path)
        elif ext == '.docx':
            loader = Docx2txtLoader(file_path)
        elif ext == '.txt':
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
        
        documents = loader.load()
        return documents
    
    def add_documents(self, file_paths: List[str]) -&gt; int:
        all_documents = []
        
        for file_path in file_paths:
            try:
                documents = self.load_document(file_path)
                for doc in documents:
                    doc.metadata['source'] = os.path.basename(file_path)
                all_documents.extend(documents)
            except Exception as e:
                print(f"加载文件 {file_path} 时出错: {str(e)}")
                continue
        
        if not all_documents:
            return 0
        
        split_docs = self.text_splitter.split_documents(all_documents)
        
        if self.vectorstore is None:
            self.vectorstore = Chroma.from_documents(
                documents=split_docs,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
        else:
            self.vectorstore.add_documents(split_docs)
        
        return len(split_docs)
    
    def search(self, query: str, k: int = 3) -&gt; List[Document]:
        if self.vectorstore is None:
            return []
        
        results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def get_retriever(self, k: int = 3):
        if self.vectorstore is None:
            return None
        return self.vectorstore.as_retriever(search_kwargs={"k": k})
    
    def get_chunks_count(self) -&gt; int:
        if self.vectorstore is None:
            return 0
        return len(self.vectorstore.get()['ids'])
    
    def clear_database(self):
        if os.path.exists(self.persist_directory):
            import shutil
            shutil.rmtree(self.persist_directory)
            self.vectorstore = None
    
    def get_sources(self) -&gt; List[str]:
        if self.vectorstore is None:
            return []
        ids = self.vectorstore.get()['ids']
        if not ids:
            return []
        metadatas = self.vectorstore.get()['metadatas']
        sources = list(set([meta.get('source', 'unknown') for meta in metadatas]))
        return sources


def main():
    print("=" * 50)
    print("知识库测试")
    print("=" * 50)
    
    kb = KnowledgeBase()
    print(f"当前知识库文本块数量: {kb.get_chunks_count()}")
    print(f"当前知识库文档: {kb.get_sources()}")


if __name__ == "__main__":
    main()
