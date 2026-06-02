import os
import streamlit as st

st.set_page_config(
    page_title="RAG 智能问答系统 - 演示版",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "knowledge_base" not in st.session_state:
        st.session_state.knowledge_base = {}

def main():
    init_session_state()
    
    st.title("🤖 RAG 智能问答系统 - 演示版")
    st.markdown("这是一个演示版本，展示系统界面和功能")
    
    st.warning("⚠️ 演示模式：Ollama 服务未连接")
    st.info("安装 Ollama 后可使用完整功能")
    
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
                    with st.spinner("正在处理文档..."):
                        for file in st.session_state.uploaded_files:
                            try:
                                content = file.read().decode('utf-8', errors='ignore')
                                st.session_state.knowledge_base[file.name] = content[:500]
                            except:
                                pass
                        st.success(f"成功添加 {len(st.session_state.uploaded_files)} 个文档！")
                        st.session_state.uploaded_files = []
                        st.rerun()
                else:
                    st.warning("请先上传文档！")
        
        with col2:
            if st.button("🗑️ 清空知识库", use_container_width=True):
                st.session_state.knowledge_base = {}
                st.session_state.messages = []
                st.success("知识库已清空！")
                st.rerun()
        
        st.divider()
        
        st.subheader("📊 知识库状态")
        st.metric("文档数量", len(st.session_state.knowledge_base))
        
        if st.session_state.knowledge_base:
            with st.expander("📄 文档列表"):
                for filename in st.session_state.knowledge_base:
                    st.write(f"- {filename}")
        
        st.divider()
        
        if st.button("🧹 清空对话历史", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    st.divider()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
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
            
            import time
            time.sleep(1)
            
            # 模拟回复
            if st.session_state.knowledge_base:
                docs = list(st.session_state.knowledge_base.keys())
                response = f"这是一个演示回复。\n\n我已收到您的问题：'{prompt}'\n\n当前知识库中有 {len(docs)} 个文档：\n"
                for doc in docs:
                    response += f"- {doc}\n"
                
                sources = [{"name": doc, "content": st.session_state.knowledge_base[doc][:100] + "..."} 
                          for doc in docs[:3]]
            else:
                response = "这是一个演示回复。\n\n我已收到您的问题，但知识库为空，请先上传文档！"
                sources = []
            
            message_placeholder.markdown(response)
            
            if sources:
                with st.expander("📚 参考文档"):
                    for i, source in enumerate(sources, 1):
                        st.write(f"**[{i}] 来源:** {source['name']}")
                        st.write(f"**内容片段:** {source['content']}")
                        st.divider()
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "sources": sources
        })

if __name__ == "__main__":
    main()