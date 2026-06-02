
import os
import streamlit as st
from rag_chain import RAGQASystem


st.set_page_config(
    page_title="RAG 智能问答系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    if "qa_system" not in st.session_state:
        st.session_state.qa_system = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []


def get_qa_system():
    if st.session_state.qa_system is None:
        with st.spinner("正在初始化问答系统..."):
            st.session_state.qa_system = RAGQASystem()
    return st.session_state.qa_system


def main():
    init_session_state()
    
    st.title("🤖 RAG 智能问答系统")
    st.markdown("基于本地知识库的检索增强生成问答系统")
    
    with st.sidebar:
        st.header("📚 知识库管理")
        
        uploaded_files = st.file_uploader(
            "上传文档 (支持 PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            st.success(f"已选择 {len(uploaded_files)} 个文件")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔨 构建知识库", type="primary", use_container_width=True):
                if st.session_state.uploaded_files:
                    qa_system = get_qa_system()
                    
                    temp_dir = "temp_uploads"
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    file_paths = []
                    for file in st.session_state.uploaded_files:
                        temp_path = os.path.join(temp_dir, file.name)
                        with open(temp_path, "wb") as f:
                            f.write(file.getbuffer())
                        file_paths.append(temp_path)
                    
                    with st.spinner("正在处理文档..."):
                        chunks_count = qa_system.kb.add_documents(file_paths)
                        qa_system.rebuild_chain()
                    
                    st.success(f"成功添加 {chunks_count} 个文本块到知识库！")
                    st.session_state.uploaded_files = []
                    st.rerun()
                else:
                    st.warning("请先上传文档！")
        
        with col2:
            if st.button("🗑️ 清空知识库", use_container_width=True):
                qa_system = get_qa_system()
                qa_system.kb.clear_database()
                qa_system.rebuild_chain()
                st.session_state.messages = []
                st.success("知识库已清空！")
                st.rerun()
        
        st.divider()
        
        qa_system = get_qa_system()
        chunks_count = qa_system.kb.get_chunks_count()
        sources = qa_system.kb.get_sources()
        
        st.subheader("📊 知识库状态")
        st.metric("文本块数量", chunks_count)
        st.metric("文档数量", len(sources))
        
        if sources:
            with st.expander("📄 文档列表"):
                for source in sources:
                    st.write(f"- {source}")
        
        st.divider()
        
        if st.button("🧹 清空对话历史", use_container_width=True):
            st.session_state.messages = []
            qa_system.clear_memory()
            st.rerun()
    
    st.divider()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📚 参考文档"):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"**[{i}] 来源:** {source['name']}")
                        st.write(f"**内容片段:** {source['content']}")
                        st.divider()
    
    if prompt := st.chat_input("请输入您的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("正在思考...")
            
            qa_system = get_qa_system()
            result = qa_system.ask(prompt)
            
            full_response = result["answer"]
            message_placeholder.markdown(full_response)
            
            sources = []
            for doc in result["source_documents"]:
                sources.append({
                    "name": doc.metadata.get("source", "unknown"),
                    "content": doc.page_content[:300] + "..."
                })
            
            if sources:
                with st.expander("📚 参考文档"):
                    for i, source in enumerate(sources, 1):
                        st.write(f"**[{i}] 来源:** {source['name']}")
                        st.write(f"**内容片段:** {source['content']}")
                        st.divider()
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "sources": sources
        })


if __name__ == "__main__":
    main()
