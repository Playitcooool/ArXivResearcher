from __future__ import annotations

import argparse
import logging
import sys

from .config import load_config
from .logging_utils import setup_logging
from .service import ArxivResearchService

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="arXiv 研究助手")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")

    subparsers = parser.add_subparsers(dest="command")

    p_update = subparsers.add_parser("update", help="抓取并生成每日结果")
    p_update.add_argument("--days", type=int, default=1, help="抓取最近几天")
    p_update.add_argument("--no-summary", action="store_true", help="不生成总结")
    p_update.add_argument("--qa", action="store_true", help="更新后进入问答模式")
    p_update.add_argument("--non-interactive", action="store_true", help="不进入交互流程")

    p_qa = subparsers.add_parser("qa", help="加载当日结果并进入问答")
    p_qa.add_argument("--days", type=int, default=1, help="仅在无当日数据时自动抓取的时间窗口")

    subparsers.add_parser("check", help="检查系统可用性")

    return parser


def _print_papers(service: ArxivResearchService, papers, summary_result) -> None:
    print("\n" + "=" * 60)
    print("今日论文推荐")
    print("=" * 60)

    for idx, paper in enumerate(papers, start=1):
        print(f"\n[{idx}] {paper.title}")
        print(f"作者: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
        print(f"发布: {paper.published}")
        print(f"分类: {', '.join(paper.categories[:3])}")
        print(f"PDF: {paper.pdf_url}")

        if summary_result and paper.arxiv_id in summary_result.summaries:
            print("总结:")
            print(summary_result.summaries[paper.arxiv_id])

    if summary_result and summary_result.trend_analysis:
        print("\n" + "=" * 60)
        print("研究趋势")
        print("=" * 60)
        print(summary_result.trend_analysis)



def run(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    command = args.command or "update"

    config = load_config(args.config)
    setup_logging(config.output.log_level, config.output.log_file)

    service = ArxivResearchService(config)

    try:
        if command == "check":
            return service.check_system()

        if command == "qa":
            try:
                papers, result = service.load_today()
            except FileNotFoundError:
                logger.warning("today files not found, auto fetching")
                papers, result = service.run_update(days=args.days, generate_summary=True)
            service.interactive_qa(papers, result)
            return 0

        papers, result = service.run_update(days=args.days, generate_summary=not args.no_summary)
        if not papers:
            return 1

        _print_papers(service, papers, result)

        if args.non_interactive:
            return 0

        if args.qa:
            service.interactive_qa(papers, result)
            return 0

        choice = input("\n进入问答模式？(y/n): ").strip().lower()
        if choice in {"y", "yes"}:
            service.interactive_qa(papers, result)
        return 0

    except KeyboardInterrupt:
        print("\n程序已退出")
        return 130
    except Exception:
        logger.exception("unhandled error")
        return 1


if __name__ == "__main__":
    sys.exit(run())
