from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class Paper:
    title: str
    authors: list[str]
    summary: str
    pdf_url: str
    published: str
    categories: list[str]
    arxiv_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Paper":
        return cls(
            title=str(data.get("title", "")),
            authors=[str(x) for x in data.get("authors", [])],
            summary=str(data.get("summary", "")),
            pdf_url=str(data.get("pdf_url", "")),
            published=str(data.get("published", "")),
            categories=[str(x) for x in data.get("categories", [])],
            arxiv_id=str(data.get("arxiv_id", "")),
        )


@dataclass(slots=True)
class SummaryResult:
    summaries: dict[str, str]
    trend_analysis: str

    def to_dict(self) -> dict[str, Any]:
        return {"summaries": self.summaries, "trend_analysis": self.trend_analysis}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SummaryResult":
        return cls(
            summaries={str(k): str(v) for k, v in data.get("summaries", {}).items()},
            trend_analysis=str(data.get("trend_analysis", "")),
        )
