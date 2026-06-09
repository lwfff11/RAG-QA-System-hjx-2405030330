import streamlit as st

st.set_page_config(page_title="Test App", layout="wide")

st.title("🤖 RAG 智能问答系统 - 测试版")
st.caption("简化版测试")

def check_ollama():
    import requests
    try:
        return requests.get("http://localhost:11434/api/tags", timeout=5).status_code == 200
    except:
        return False

ollama_ok = check_ollama()

if ollama_ok:
    st.success("✅ Ollama 服务连接正常")
else:
    st.error("❌ Ollama 服务未连接")

st.divider()
st.write("测试输入：")
prompt = st.chat_input("请输入问题...")
if prompt:
    st.write(f"您输入了: {prompt}")
