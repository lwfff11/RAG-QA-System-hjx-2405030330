# RAG 智能问答系统

基于本地知识库的检索增强生成（Retrieval-Augmented Generation）问答系统，使用 Ollama 本地大模型、LangChain 框架和 Streamlit 可视化界面构建。

## 功能特点

- 📚 支持多种文档格式（PDF、DOCX、TXT）
- 🔍 智能语义检索相关文档片段
- 💬 多轮对话记忆功能
- 🤖 基于本地大模型，保护数据隐私
- 📊 知识库状态实时监控
- 🎨 美观友好的 Web 界面

## 环境要求

- **操作系统**: Windows 10/11
- **Python 版本**: 3.9 或更高版本
- **内存**: 建议 16GB 以上（取决于模型大小）
- **存储空间**: 至少 10GB 可用空间

## 安装步骤

### 1. 安装 Ollama

1. 访问 [Ollama 官网](https://ollama.com/) 下载 Windows 版本安装包
2. 运行安装程序完成安装
3. 打开命令提示符（CMD）或 PowerShell，验证安装：
   ```bash
   ollama --version
   ```

### 2. 下载模型

在命令提示符中运行以下命令下载所需模型：

```bash
# 下载 DeepSeek-R1 7B 模型（推荐）
ollama pull deepseek-r1:7b

# 或者下载 Qwen2 7B 模型
ollama pull qwen2:7b

# 下载嵌入模型
ollama pull nomic-embed-text
```

### 3. 配置 Python 环境

1. 克隆或下载本项目到本地
2. 在项目目录中创建虚拟环境：
   ```bash
   python -m venv venv
   ```

3. 激活虚拟环境：
   ```bash
   # Windows
   venv\Scripts\activate
   ```

4. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

### 4. 测试 Ollama 连接

运行测试脚本验证 Ollama 服务是否正常：

```bash
python test_ollama.py
```

如果测试成功，说明环境配置完成！

## 使用说明

### 启动 Web 应用

在项目目录下运行：

```bash
# 方式一：使用启动脚本
python run_app.py

# 方式二：直接使用 Streamlit
streamlit run app.py
```

应用将自动在浏览器中打开，默认地址为 `http://localhost:8501`

### 使用流程

1. **上传文档**
   - 在左侧侧边栏点击"上传文档"
   - 选择一个或多个 PDF、DOCX 或 TXT 文件
   - 点击"构建知识库"按钮

2. **提问问题**
   - 在底部聊天输入框中输入您的问题
   - 按回车或点击发送按钮
   - 系统会基于知识库内容给出回答

3. **查看参考文档**
   - 回答下方会显示相关的参考文档片段
   - 点击展开可查看详细内容

4. **管理知识库**
   - 侧边栏显示当前知识库状态
   - 可清空知识库重新构建
   - 可清空对话历史

### 命令行版本

如果需要在命令行中使用，可运行：

```bash
python rag_chain.py
```

## 项目结构

```
RAG-QA-System/
├── app.py                 # Streamlit Web 应用主文件
├── rag_chain.py           # RAG 问答链核心模块
├── knowledge_base.py      # 知识库管理模块
├── test_ollama.py         # Ollama 连接测试脚本
├── run_app.py             # 应用启动器
├── requirements.txt       # Python 依赖包列表
├── build.spec             # PyInstaller 打包配置
├── .gitignore            # Git 忽略文件配置
├── README.md             # 项目说明文档
├── chroma_db/            # Chroma 向量数据库（自动生成）
├── temp_uploads/         # 临时上传文件目录（自动生成）
└── docs/                # 示例文档目录（自行创建）
```

## 关键技术点

### RAG 工作流程

1. **文档加载**: 使用 LangChain 的文档加载器读取各种格式文档
2. **文本分割**: 使用 RecursiveCharacterTextSplitter 将文本分块（chunk_size=1000, chunk_overlap=200）
3. **向量化**: 使用 Ollama 的 nomic-embed-text 模型生成向量嵌入
4. **向量存储**: 存储在 Chroma 本地向量数据库中
5. **检索**: 根据用户查询检索最相关的 3 个文本块
6. **生成**: 将检索到的文档和用户问题一起发送给大模型生成回答

### 使用的模型

- **大语言模型**: deepseek-r1:7b（可选 qwen2:7b）
- **嵌入模型**: nomic-embed-text

### 系统提示词

系统提示词要求模型：
- 仅基于提供的参考文档回答问题
- 文档中无相关信息时明确说明
- 回答简洁明了，重点突出

## 打包为 EXE

使用 PyInstaller 将应用打包为独立可执行文件：

```bash
# 安装 PyInstaller（如未安装）
pip install pyinstaller

# 使用 spec 文件打包
pyinstaller build.spec

# 或者直接打包
pyinstaller --onefile --name RAG_QA_System run_app.py
```

打包后的文件位于 `dist/` 目录中。

**注意**: 打包后的 EXE 文件仍需要目标机器已安装 Ollama 并下载好相关模型才能运行。

## 常见问题

### Q: Ollama 服务无法连接？
A: 请确保 Ollama 服务已启动，可以运行 `ollama serve` 手动启动服务。

### Q: 模型下载很慢？
A: 可以尝试配置 Ollama 使用镜像源，或手动下载模型文件。

### Q: 回答质量不高？
A: 可以尝试：
- 增加文档数量和质量
- 调整文本分块参数
- 使用更大的模型
- 优化系统提示词

### Q: 内存占用过高？
A: 可以使用更小的模型（如 qwen2:1.5b）或减少同时加载的文档数量。

## 已知问题与改进方向

- [ ] 支持更多文档格式（PPT、Excel、Markdown 等）
- [ ] 添加文档预览功能
- [ ] 支持知识库的导出和导入
- [ ] 添加深色模式
- [ ] 优化大文件处理性能
- [ ] 添加问答历史导出功能
- [ ] 支持批量处理文件夹中的所有文档

## 项目截图

（请在此处添加项目运行截图）

## 参考资源

- [Ollama 官方文档](https://ollama.com/)
- [LangChain 官方文档](https://python.langchain.com/)
- [Streamlit 官方文档](https://docs.streamlit.io/)
- [Chroma 向量数据库](https://www.trychroma.com/)

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，欢迎提交 Issue！

---

**祝您使用愉快！** 🚀