from langchain_ollama import OllamaLLM


def test_ollama_connection():
    print("=" * 50)
    print("Ollama API 测试脚本")
    print("=" * 50)
    
    try:
        print("\n正在连接Ollama服务...")
        llm = OllamaLLM(
            model="deepseek-r1:7b",
            temperature=0.7,
            base_url="http://localhost:11434"
        )
        
        print("成功连接Ollama服务！")
        print("\n正在测试模型响应...")
        
        test_query = "你好，请用一句话介绍你自己。"
        response = llm.invoke(test_query)
        
        print(f"\n问题: {test_query}")
        print(f"\n回答: {response}")
        print("\n" + "=" * 50)
        print("✓ 测试成功！Ollama API 工作正常。")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败！错误信息: {str(e)}")
        print("\n请确保：")
        print("1. Ollama服务已启动 (运行 'ollama serve')")
        print("2. deepseek-r1:7b模型已下载 (运行 'ollama pull deepseek-r1:7b')")
        print("3. Ollama服务运行在 http://localhost:11434")
        print("=" * 50)
        return False


if __name__ == "__main__":
    test_ollama_connection()