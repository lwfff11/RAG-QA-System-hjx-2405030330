
@echo off
chcp 65001 &gt;nul
echo ========================================
echo RAG 智能问答系统 - 启动脚本
echo ========================================
echo.
echo 正在启动应用...
echo 请确保已安装 Ollama 并下载了所需模型！
echo.
echo 应用地址: http://localhost:8501
echo ========================================
echo.

python -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo 启动失败！请检查：
    echo 1. Python 是否已安装
    echo 2. 是否已安装依赖包 (pip install -r requirements.txt)
    echo 3. 虚拟环境是否已激活
    echo.
    pause
)
