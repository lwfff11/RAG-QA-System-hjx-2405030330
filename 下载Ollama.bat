@echo off
chcp 65001 >nul
echo ========================================
echo   Ollama 下载和安装指南
echo ========================================
echo.
echo 请按以下步骤操作：
echo.
echo [1] 自动下载（需要网络稳定）
echo [2] 手动下载（推荐）
echo [3] 退出
echo.
set /p choice="请选择 (1/2/3): "

if "%choice%"=="1" goto auto_download
if "%choice%"=="2" goto manual_download
if "%choice%"=="3" goto end

echo.
echo 无效选择
goto end

:auto_download
echo.
echo 正在尝试自动下载...
echo.
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/ollama/ollama/releases/latest/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe'"
if exist "OllamaSetup.exe" (
    echo.
    echo 下载成功！
    echo.
    set /p install="是否现在安装？(Y/N): "
    if /i "%install%"=="Y" (
        start OllamaSetup.exe
    )
) else (
    echo.
    echo 自动下载失败，请使用手动下载方式。
    goto manual_download
)
goto end

:manual_download
echo.
echo ========================================
echo   手动下载步骤
echo ========================================
echo.
echo 1. 请打开浏览器，访问以下链接：
echo.
echo    https://ollama.com/download
echo.
echo 2. 点击 "Download for Windows" 按钮
echo.
echo 3. 下载完成后，双击运行安装程序
echo.
echo 4. 安装完成后，继续下载模型：
echo.
echo    打开命令提示符，运行：
echo    ollama pull nomic-embed-text
echo    ollama pull deepseek-r1:7b
echo.
echo ========================================
echo.
start https://ollama.com/download
echo.
pause
goto end

:end