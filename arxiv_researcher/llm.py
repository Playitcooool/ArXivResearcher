from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import requests

from .models import Paper, SummaryResult

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3:8b",
        timeout_seconds: int = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def healthcheck(self) -> tuple[bool, str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            payload = response.json()
            models = [m.get("name", "") for m in payload.get("models", [])]
            return True, ", ".join([m for m in models if m])
        except requests.RequestException as exc:
            return False, str(exc)

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        url = f"{self.base_url}/api/generate"
        data: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            response = requests.post(url, json=data, timeout=self.timeout_seconds)
            response.raise_for_status()
            result = response.json()
            return str(result.get("response", "")).strip()
        except requests.RequestException:
            logger.exception("ollama generate failed")
            return ""

    def summarize_paper(self, paper: Paper, temperature: float, max_tokens: int) -> str:
        prompt = f"""请对以下学术论文进行总结，包括：
1. 研究问题和动机
2. 主要方法
3. 关键贡献
4. 实验结果（如果提到）

论文标题：{paper.title}

摘要：{paper.summary}

请用中文简洁总结（200字以内）。"""
        return self.generate(prompt, temperature=temperature, max_tokens=max_tokens)

    def analyze_research_trends(
        self,
        papers: list[Paper],
        summaries: dict[str, str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        items = []
        for paper in papers:
            summary = summaries.get(paper.arxiv_id) or paper.summary[:200]
            items.append(f"- {paper.title}\n  {summary}\n")

        prompt = f"""以下是最近发表的 {len(papers)} 篇学术论文的标题和总结：

{"\n".join(items)}

请分析：
1. 当前研究热点
2. 主要技术路线
3. 新兴方向
4. 共同挑战

请用中文输出 300-500 字分析。"""
        return self.generate(prompt, temperature=temperature, max_tokens=max_tokens)

    def answer_question(self, paper: Paper, question: str, context: str = "") -> str:
        context_text = f"\n\n论文总结：{context}" if context else ""
        prompt = f"""基于以下论文信息回答问题。

论文标题：{paper.title}
作者：{', '.join(paper.authors[:5])}
摘要：{paper.summary}{context_text}

问题：{question}

请用中文回答。"""
        return self.generate(prompt, temperature=0.6, max_tokens=1500)


class PaperSummarizer:
    def __init__(self, client: OllamaClient, temperature: float, max_tokens: int) -> None:
        self.client = client
        self.temperature = temperature
        self.max_tokens = max_tokens

    def process_papers(self, papers: list[Paper]) -> SummaryResult:
        summaries: dict[str, str] = {}
        total = len(papers)

        for idx, paper in enumerate(papers, start=1):
            logger.info("summarizing %s/%s: %s", idx, total, paper.title[:80])
            summaries[paper.arxiv_id] = self.client.summarize_paper(
                paper,
                temperature=min(self.temperature, 0.7),
                max_tokens=min(self.max_tokens, 1200),
            )

        trend = self.client.analyze_research_trends(
            papers,
            summaries,
            temperature=self.temperature,
            max_tokens=min(self.max_tokens + 1000, 4000),
        )
        return SummaryResult(summaries=summaries, trend_analysis=trend)

    @staticmethod
    def save_results(result: SummaryResult, filepath: str | Path) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info("summary saved: %s", path)

    @staticmethod
    def load_results(filepath: str | Path) -> SummaryResult:
        path = Path(filepath)
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return SummaryResult.from_dict(payload)
