from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from .models import Paper

logger = logging.getLogger(__name__)


class ArxivFetcher:
    def __init__(self, categories: list[str], max_results: int = 10, query: str = "") -> None:
        self.categories = categories
        self.max_results = max_results
        self.query = query

    def build_query(self) -> str:
        category_query = " OR ".join([f"cat:{cat}" for cat in self.categories])
        if self.query.strip():
            return f"({self.query}) AND ({category_query})"
        return category_query

    def fetch_recent_papers(self, days: int = 1) -> list[Paper]:
        if days <= 0:
            raise ValueError("days 必须大于 0")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        query = self.build_query()

        logger.info("searching arXiv | query=%s | days=%s", query, days)

        import arxiv

        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        papers: list[Paper] = []
        for result in client.results(search):
            published_naive = result.published.replace(tzinfo=None)
            if published_naive < start_date:
                continue

            paper = Paper(
                title=result.title,
                authors=[author.name for author in result.authors],
                summary=result.summary.replace("\n", " "),
                pdf_url=result.pdf_url,
                published=result.published.strftime("%Y-%m-%d"),
                categories=result.categories,
                arxiv_id=result.entry_id.split("/")[-1],
            )
            papers.append(paper)

        logger.info("fetched papers=%s", len(papers))
        return papers

    @staticmethod
    def save_papers(papers: list[Paper], filepath: str | Path) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in papers], f, ensure_ascii=False, indent=2)
        logger.info("papers saved: %s", path)

    @staticmethod
    def load_papers(filepath: str | Path) -> list[Paper]:
        path = Path(filepath)
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return [Paper.from_dict(item) for item in payload]
