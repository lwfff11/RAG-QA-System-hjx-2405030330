import urllib.request
import sys

print("=" * 50)
print("  Ollama 下载器")
print("=" * 50)
print()

url = "https://github.com/ollama/ollama/releases/latest/download/OllamaSetup.exe"
filename = "OllamaSetup.exe"

print(f"下载地址: {url}")
print(f"保存位置: {filename}")
print()
print("开始下载...")
print()

def report_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    percent = (downloaded / total_size) * 100
    mb_downloaded = downloaded / (1024 * 1024)
    mb_total = total_size / (1024 * 1024)
    sys.stdout.write(f"\r进度: {percent:.1f}% ({mb_downloaded:.1f}MB / {mb_total:.1f}MB)")
    sys.stdout.flush()

try:
    urllib.request.urlretrieve(url, filename, reporthook=report_progress)
    print()
    print()
    print("=" * 50)
    print("  ✅ 下载成功！")
    print("=" * 50)
    print()
    print(f"文件已保存到: {filename}")
    print()
    print("现在请双击运行 OllamaSetup.exe 进行安装")
    print()
    
    choice = input("是否现在打开安装程序？(Y/N): ").strip().upper()
    if choice == "Y":
        import os
        os.startfile(filename)
        
except Exception as e:
    print()
    print()
    print("=" * 50)
    print("  ❌ 下载失败")
    print("=" * 50)
    print()
    print(f"错误: {e}")
    print()
    print("请尝试手动下载:")
    print()
    print("1. 打开浏览器，访问: https://ollama.com/download")
    print("2. 点击 Download for Windows 按钮")
    print("3. 保存到当前目录")
    print()

input("按回车键退出...")