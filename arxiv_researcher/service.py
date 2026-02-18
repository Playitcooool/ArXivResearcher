from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import AppConfig
from .fetcher import ArxivFetcher
from .llm import OllamaClient, PaperSummarizer
from .models import Paper, SummaryResult

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RunArtifacts:
    papers_file: Path
    summaries_file: Path


class ArxivResearchService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.fetcher = ArxivFetcher(
            categories=config.arxiv.categories,
            max_results=config.arxiv.max_results,
            query=config.arxiv.query,
        )
        self.ollama = OllamaClient(
            base_url=config.ollama.base_url,
            model=config.ollama.model,
            timeout_seconds=config.ollama.timeout_seconds,
        )
        self.summarizer = PaperSummarizer(
            client=self.ollama,
            temperature=config.ollama.temperature,
            max_tokens=config.ollama.max_tokens,
        )
        config.save_dir_path.mkdir(parents=True, exist_ok=True)

    def _today_files(self) -> RunArtifacts:
        stamp = datetime.now().strftime("%Y%m%d")
        return RunArtifacts(
            papers_file=self.config.save_dir_path / f"papers_{stamp}.json",
            summaries_file=self.config.save_dir_path / f"summaries_{stamp}.json",
        )

    def run_update(self, days: int = 1, generate_summary: bool = True) -> tuple[list[Paper], SummaryResult | None]:
        papers = self.fetcher.fetch_recent_papers(days=days)
        if not papers:
            logger.warning("no papers found")
            return [], None

        paths = self._today_files()
        self.fetcher.save_papers(papers, paths.papers_file)

        if not generate_summary:
            return papers, None

        result = self.summarizer.process_papers(papers)
        self.summarizer.save_results(result, paths.summaries_file)
        return papers, result

    def load_today(self) -> tuple[list[Paper], SummaryResult | None]:
        paths = self._today_files()
        if not paths.papers_file.exists():
            raise FileNotFoundError(f"未找到论文数据: {paths.papers_file}")

        papers = self.fetcher.load_papers(paths.papers_file)
        summaries = None
        if paths.summaries_file.exists():
            summaries = self.summarizer.load_results(paths.summaries_file)
        return papers, summaries

    def check_system(self) -> int:
        code = 0

        ok, detail = self.ollama.healthcheck()
        if ok:
            logger.info("ollama ok | models=%s", detail or "none")
        else:
            logger.error("ollama unavailable | error=%s", detail)
            code = 1

        return code

    def interactive_qa(self, papers: list[Paper], result: SummaryResult | None) -> None:
        if not papers:
            print("没有论文可供问答")
            return

        print("\n问答模式：输入 list 查看论文，输入编号选择论文，输入 quit 退出")
        current: Paper | None = None

        while True:
            user_input = input("\n问题/命令> ").strip()
            if not user_input:
                continue

            if user_input.lower() in {"quit", "exit", "q"}:
                print("已退出问答模式")
                break

            if user_input.lower() == "list":
                for idx, paper in enumerate(papers, start=1):
                    print(f"{idx}. {paper.title[:100]}")
                continue

            if user_input.isdigit():
                idx = int(user_input) - 1
                if 0 <= idx < len(papers):
                    current = papers[idx]
                    print(f"已选择: {current.title}")
                else:
                    print(f"无效编号，请输入 1-{len(papers)}")
                continue

            if current is None:
                print("请先输入论文编号")
                continue

            context = ""
            if result and result.summaries:
                context = result.summaries.get(current.arxiv_id, "")

            print("思考中...")
            answer = self.ollama.answer_question(current, user_input, context=context)
            print(answer or "模型没有返回内容，请检查 Ollama 服务或模型配置")
