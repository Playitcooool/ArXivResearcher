# arXiv 研究助手 📚

一个基于 Python 的每日科研助手，自动推荐指定领域的 arXiv 最新论文，并利用本地大模型（Ollama）进行智能总结和问答。

## 功能特性 ✨

- **自动论文获取**: 从 arXiv 获取指定研究领域的最新论文
- **智能总结**: 使用本地大模型对每篇论文进行智能总结
- **研究热点分析**: 自动分析最近的研究趋势和热点
- **交互式问答**: 针对具体论文进行深入问答
- **完全本地化**: 使用 Ollama 实现本地大模型调用，保护数据隐私

## 系统架构 🏗️

```
arxivResearcher/
├── main.py              # 主程序入口
├── arxiv_fetcher.py     # arXiv 论文获取模块
├── ollama_client.py     # Ollama 客户端和总结模块
├── config.yaml          # 配置文件
├── requirements.txt     # Python 依赖
├── papers/              # 论文数据存储目录
│   ├── papers_YYYYMMDD.json
│   └── summaries_YYYYMMDD.json
└── README.md
```

## 安装步骤 🚀

### 1. 安装 Ollama

首先需要安装 Ollama 并下载模型：

**macOS/Linux:**
```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载推荐模型（选择一个）
ollama pull llama3.2        # 轻量级，速度快
ollama pull qwen2.5         # 中文效果好
ollama pull llama3.1:8b     # 综合性能好

# 启动 Ollama 服务（通常会自动启动）
ollama serve
```

**Windows:**
从 [Ollama 官网](https://ollama.com/download) 下载安装包并安装。

### 2. 安装 Python 依赖

```bash
# 克隆或进入项目目录
cd arxivResearcher

# 安装依赖（推荐使用虚拟环境）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 配置 ⚙️

编辑 `config.yaml` 文件来自定义你的设置：

```yaml
# arXiv 配置
arxiv:
  # 研究领域类别（参考：https://arxiv.org/category_taxonomy）
  categories:
    - cs.AI        # 人工智能
    - cs.LG        # 机器学习
    - cs.CV        # 计算机视觉
    - cs.CL        # 自然语言处理
  max_results: 10  # 每日获取论文数量
  query: ""        # 额外搜索关键词（可选）

# Ollama 配置
ollama:
  base_url: "http://localhost:11434"
  model: "qwen3:8b"      # 使用的模型名称
  temperature: 0.7
  max_tokens: 2000

# 输出配置
output:
  save_dir: "./papers"   # 数据保存路径
  download_pdf: false    # 是否下载 PDF
```

### 常用 arXiv 分类

| 分类代码 | 领域 |
|---------|------|
| cs.AI | 人工智能 |
| cs.LG | 机器学习 |
| cs.CV | 计算机视觉 |
| cs.CL | 计算语言学/NLP |
| cs.RO | 机器人 |
| cs.NE | 神经与进化计算 |
| stat.ML | 统计机器学习 |
| cs.CR | 密码学与安全 |
| cs.DC | 分布式计算 |

完整分类列表见：https://arxiv.org/category_taxonomy

## 使用方法 📖

### 1. 每日更新（推荐）

运行完整的每日更新流程：获取论文 → 生成总结 → 分析趋势 → 进入问答

```bash
python main.py
```

### 2. 自定义参数

```bash
# 获取最近 3 天的论文
python main.py --days 3

# 使用自定义配置文件
python main.py --config my_config.yaml

# 只获取论文，不生成总结（节省时间）
python main.py --no-summary
```

### 3. 仅问答模式

如果已经运行过每日更新，可以直接进入问答模式：

```bash
python main.py --qa
```

## 工作流程示例 💡

### 每日使用流程

1. **早上运行每日更新**
```bash
python main.py
```

输出示例：
```
============================================================
📚 获取最新论文
============================================================
正在搜索 arXiv 论文...
类别: cs.AI, cs.LG
时间范围: 2024-01-19 至 2024-01-20
找到 10 篇相关论文

============================================================
🤖 AI 总结与分析
============================================================

[1/10] 正在总结: Advances in Multi-Modal Learning...
完成！
[2/10] 正在总结: Efficient Fine-tuning Methods...
完成！
...

============================================================
📊 每日论文推荐
============================================================

【论文 1】
标题: Advances in Multi-Modal Learning for Vision-Language Tasks
作者: Zhang, Li, Wang...
发布: 2024-01-20
分类: cs.CV, cs.AI, cs.LG
链接: https://arxiv.org/pdf/2401.xxxxx

📝 AI 总结:
本文研究多模态学习中的视觉-语言任务，提出了一种新的对齐方法...
主要贡献包括：1) 设计了高效的跨模态注意力机制...
实验结果表明该方法在多个基准测试上超越了现有方法...

------------------------------------------------------------
...

============================================================
🔥 研究热点分析
============================================================
根据这10篇论文的分析，当前的主要研究热点包括：

1. **多模态大模型**: 视觉-语言模型的对齐和高效训练...
2. **参数高效微调**: LoRA、Adapter 等方法的改进...
3. **长文本处理**: 扩展上下文窗口的新技术...
4. **模型压缩**: 量化和剪枝技术的进展...

主要技术方法包括注意力机制优化、知识蒸馏...
```

2. **交互式问答**

程序会询问是否进入问答模式，选择 `y` 后：

```
============================================================
💬 论文问答模式
============================================================
输入 'list' 查看论文列表
输入 'quit' 或 'exit' 退出问答

请输入命令或问题: list

可用论文:
1. Advances in Multi-Modal Learning for Vision-Language Tasks
2. Efficient Fine-tuning Methods for Large Language Models
3. ...

请输入命令或问题: 1

✅ 已选择论文: Advances in Multi-Modal Learning for Vision-Language Tasks
输入问题开始提问...

请输入命令或问题: 这篇论文的主要创新点是什么？

🤔 思考中...

💡 回答:
这篇论文的主要创新点包括：
1. 提出了一种新的跨模态对齐机制，通过...
2. 设计了参数高效的训练方法，减少了...
3. 在多个基准测试上取得了 SOTA 结果...

请输入命令或问题: quit
👋 退出问答模式
```

## 高级功能 🔧

### 定时任务（Cron/Task Scheduler）

**Linux/macOS (crontab):**
```bash
# 编辑 crontab
crontab -e

# 每天早上 9 点运行
0 9 * * * cd /path/to/arxivResearcher && /path/to/venv/bin/python main.py >> logs/daily.log 2>&1
```

**Windows (Task Scheduler):**
创建一个计划任务，定时运行 `python main.py`

### 自定义提示词

你可以修改 `ollama_client.py` 中的提示词来自定义总结和分析的风格：

```python
# 在 OllamaClient.summarize_paper() 中
prompt = f"""请对以下学术论文进行总结...
[自定义你的提示词]
"""
```

## 故障排除 🔧

### 1. Ollama 连接失败

```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 如果未运行，启动服务
ollama serve
```

### 2. arXiv API 限流

arXiv API 有速率限制，如果遇到问题：
- 减少 `max_results` 数量
- 增加请求间隔时间

### 3. 模型响应慢

- 使用更小的模型（如 `llama3.2`）
- 减少 `max_tokens` 参数
- 考虑使用量化版本的模型

### 4. 中文支持

对于更好的中文支持，推荐使用：
```bash
ollama pull qwen2.5        # 阿里千问
ollama pull glm4           # 智谱 GLM
```

然后在 `config.yaml` 中修改：
```yaml
ollama:
  model: "qwen2.5"
```

## 技术栈 🛠️

- **arXiv API**: 论文数据源
- **Ollama**: 本地大模型推理
- **Python 3.8+**: 主要编程语言
- **PyYAML**: 配置管理
- **Requests**: HTTP 请求

## 贡献与反馈 🤝

欢迎提交 Issue 和 Pull Request！

## 许可证 📄

MIT License

## 致谢 🙏

- [arXiv](https://arxiv.org/) - 开放获取的预印本论文库
- [Ollama](https://ollama.com/) - 简化的本地大模型运行工具
- 所有开源社区贡献者

---

**开始使用**: `python main.py`

**祝你科研顺利！📚✨**
