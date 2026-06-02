
import os
import sys
import subprocess


def main():
    print("=" * 50)
    print("RAG 智能问答系统 - 启动器")
    print("=" * 50)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")
    
    if not os.path.exists(app_path):
        print(f"错误: 找不到 app.py 文件: {app_path}")
        input("按回车键退出...")
        return
    
    print("\n正在启动 Streamlit 应用...")
    print("应用地址: http://localhost:8501")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    except KeyboardInterrupt:
        print("\n\n已停止服务。")
    except Exception as e:
        print(f"\n启动失败: {str(e)}")
        input("按回车键退出...")


if __name__ == "__main__":
    main()
