# arXiv Researcher

工程化的 arXiv 论文助手：抓取最新论文、调用本地 Ollama 生成总结、支持问答与系统检查。

## 目录结构

```text
ArXivResearcher/
├── arxiv_researcher/
│   ├── __main__.py
│   ├── cli.py
│   ├── config.py
│   ├── fetcher.py
│   ├── llm.py
│   ├── logging_utils.py
│   ├── models.py
│   └── service.py
├── tests/
├── config.yaml
├── main.py
└── pyproject.toml
```

## 快速开始

1. 安装依赖

```bash
cd ArXivResearcher
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. 启动 Ollama 并拉取模型

```bash
ollama serve
ollama pull qwen3:8b
```

3. 运行每日更新

```bash
python main.py update --days 1
```

## CLI 用法

### `update` 抓取 + 总结

```bash
python main.py update --days 1
python main.py update --days 3 --no-summary
python main.py update --qa
python main.py update --non-interactive
```

### `qa` 仅问答模式

```bash
python main.py qa
```

如果当天没有缓存数据，会自动先抓取并总结。

### `check` 系统检查

```bash
python main.py check
```

## 配置

默认读取 `config.yaml`，也支持环境变量覆盖。

### 关键配置项

- `arxiv.categories`
- `arxiv.max_results`
- `arxiv.query`
- `ollama.base_url`
- `ollama.model`
- `ollama.temperature`
- `ollama.max_tokens`
- `ollama.timeout_seconds`
- `output.save_dir`
- `output.log_level`
- `output.log_file`

### 常用环境变量

- `ARXIV_CATEGORIES=cs.AI,cs.LG`
- `ARXIV_MAX_RESULTS=10`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `OLLAMA_MODEL=qwen3:8b`
- `OUTPUT_SAVE_DIR=./papers`
- `LOG_LEVEL=INFO`
- `LOG_FILE=./logs/arxiv_researcher.log`

## 输出

- `papers/papers_YYYYMMDD.json`
- `papers/summaries_YYYYMMDD.json`
- `logs/arxiv_researcher.log`（可配置）

## 测试

```bash
pytest -q
```

## 入口说明

- 推荐入口：`python main.py`
