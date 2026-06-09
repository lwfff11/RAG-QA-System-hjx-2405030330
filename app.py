import os
import json
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="RAG 智能问答系统", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

OLLAMA_BASE = "http://localhost:11434"
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@st.cache_resource(show_spinner=False)
def get_knowledge_base(embedding_model: str = "nomic-embed-text"):
    from knowledge_base import KnowledgeBase
    return KnowledgeBase(
        embedding_model=embedding_model,
        base_url=OLLAMA_BASE,
    )


def clear_kb_cache():
    st.cache_resource.clear()


def init_session_state():
    defaults = {
        "messages": [],
        "uploaded_files": [],
        "dark_mode": False,
        "selected_model": "qwen2:1.5b",
        "embedding_model": "nomic-embed-text",
        "kb_chunks": 0,
        "kb_sources": [],
        "qa_ready": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def check_ollama_connection():
    try:
        return requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5).status_code == 200
    except Exception:
        return False


def list_local_models():
    try:
        data = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5).json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def apply_dark_mode():
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: #e0e0e0; }
        .stSidebar { background-color: #161b22; }
        h1,h2,h3,h4,h5,h6 { color: #58a6ff; }
        </style>
        """, unsafe_allow_html=True)


def export_chat_history():
    if not st.session_state.messages:
        st.caption("暂无对话历史")
        return
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    export_data = {
        "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model": st.session_state.selected_model,
        "messages": history,
    }
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
    st.download_button(
        "📥 下载对话历史",
        data=json_str,
        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True,
    )


def preview_files(uploaded_files):
    if not uploaded_files:
        return
    st.subheader("📄 文档预览")
    for file in uploaded_files:
        ext = os.path.splitext(file.name)[1].lower()
        with st.expander(f"📎 {file.name}"):
            if ext in [".txt", ".md"]:
                try:
                    content = file.read().decode("utf-8", errors="ignore")
                    st.text_area("内容", value=content[:2000], height=200, disabled=True, label_visibility="collapsed")
                    file.seek(0)
                except Exception as e:
                    st.warning(f"无法预览: {e}")
            else:
                st.info(f"{ext.upper()} 文件 - 构建知识库后可检索")


def handle_upload(uploaded_files):
    if not uploaded_files:
        return []
    file_paths = []
    for file in uploaded_files:
        temp_path = os.path.join(UPLOAD_DIR, file.name)
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())
        file_paths.append(temp_path)
    return file_paths


def main():
    init_session_state()
    apply_dark_mode()

    ollama_available = check_ollama_connection()
    available_models = list_local_models() if ollama_available else []

    st.title("🤖 RAG 智能问答系统")
    st.caption("基于本地知识库的检索增强生成问答系统 | LangChain + Ollama")

    if not ollama_available:
        st.error("⚠️ Ollama 服务未连接")
        st.info("请确保 Ollama 已安装并运行")
        st.stop()

    kb = get_knowledge_base(embedding_model=st.session_state.embedding_model)

    with st.sidebar:
        st.header("📚 知识库管理")

        st.subheader("1. 文档上传")
        uploaded_files = st.file_uploader(
            "支持 PDF / DOCX / TXT / MD / PPTX",
            type=["pdf", "docx", "txt", "md", "pptx"],
            accept_multiple_files=True,
        )
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            st.success(f"已选择 {len(uploaded_files)} 个文件")
            preview_files(uploaded_files)

        if st.button("🔨 构建知识库", type="primary", use_container_width=True):
            if uploaded_files:
                with st.spinner("正在处理文档并构建向量索引..."):
                    file_paths = handle_upload(uploaded_files)
                    try:
                        chunks_count = kb.add_documents(file_paths)
                        if chunks_count > 0:
                            st.session_state.kb_chunks = kb.get_chunks_count()
                            st.session_state.kb_sources = kb.get_sources()
                            st.session_state.qa_ready = True
                            st.session_state.uploaded_files = []
                            st.success(f"成功！共 {st.session_state.kb_chunks} 个文本块，{len(st.session_state.kb_sources)} 个文档")
                        else:
                            st.warning("未提取到文本")
                    except Exception as e:
                        st.error(f"处理失败: {e}")
            else:
                st.warning("请先上传文档")

        if st.button("🗑️ 清空知识库", use_container_width=True):
            kb.clear_database()
            st.session_state.kb_chunks = 0
            st.session_state.kb_sources = []
            st.session_state.qa_ready = False
            st.session_state.messages = []
            st.success("知识库已清空")

        st.divider()

        st.subheader("2. 模型选择")
        if available_models:
            new_model = st.selectbox(
                "LLM 模型",
                options=available_models,
                index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0,
            )
            if new_model != st.session_state.selected_model:
                st.session_state.selected_model = new_model

            emb_models = [m for m in available_models if "embed" in m.lower()]
            if emb_models:
                new_emb = st.selectbox(
                    "嵌入模型",
                    options=emb_models,
                    index=emb_models.index(st.session_state.embedding_model) if st.session_state.embedding_model in emb_models else 0,
                )
                if new_emb != st.session_state.embedding_model:
                    st.session_state.embedding_model = new_emb
                    clear_kb_cache()
                    st.warning("嵌入模型已变更，请重新构建知识库")

        st.divider()

        st.subheader("3. 知识库状态")
        live_chunks = kb.get_chunks_count()
        live_sources = kb.get_sources()
        st.metric("文本块", live_chunks)
        st.metric("文档数", len(live_sources))
        if live_sources:
            with st.expander("文档列表"):
                for s in live_sources:
                    st.write(f"- {s}")

        st.divider()

        st.subheader("4. 对话管理")
        if st.button("🧹 清空对话", use_container_width=True):
            st.session_state.messages = []
        export_chat_history()

        st.divider()

        st.subheader("5. 外观设置")
        st.session_state.dark_mode = st.toggle("暗色模式", value=st.session_state.dark_mode)

    st.divider()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("请输入问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if kb.get_chunks_count() == 0:
                msg = "知识库为空，请先上传文档并构建知识库！"
                st.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            else:
                try:
                    from rag_chain import RAGQASystem
                    qa = RAGQASystem(
                        kb=kb,
                        model=st.session_state.selected_model,
                        base_url=OLLAMA_BASE,
                    )
                    with st.spinner("正在检索并回答..."):
                        result = qa.ask(prompt)
                        st.markdown(result["answer"])
                        st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
                except Exception as e:
                    msg = f"❌ 出错: {e}"
                    st.markdown(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg})


if __name__ == "__main__":
    main()
