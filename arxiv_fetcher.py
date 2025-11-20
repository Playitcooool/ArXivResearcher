"""
arXiv 论文获取模块
用于从 arXiv API 获取指定领域的最新论文
"""

import arxiv
from datetime import datetime, timedelta
from typing import List, Dict
import json


class ArxivFetcher:
    """arXiv 论文获取器"""

    def __init__(self, categories: List[str], max_results: int = 10, query: str = ""):
        """
        初始化 arXiv 获取器

        Args:
            categories: arXiv 类别列表，如 ['cs.AI', 'cs.LG']
            max_results: 每次获取的最大论文数量
            query: 额外的搜索查询条件
        """
        self.categories = categories
        self.max_results = max_results
        self.query = query

    def fetch_recent_papers(self, days: int = 1) -> List[Dict]:
        """
        获取最近几天的论文

        Args:
            days: 获取最近几天的论文

        Returns:
            论文信息列表
        """
        # 构建搜索查询
        category_query = " OR ".join([f"cat:{cat}" for cat in self.categories])

        if self.query:
            search_query = f"({self.query}) AND ({category_query})"
        else:
            search_query = category_query

        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        print(f"正在搜索 arXiv 论文...")
        print(f"类别: {', '.join(self.categories)}")
        print(f"时间范围: {start_date.date()} 至 {end_date.date()}")

        # 搜索论文
        client = arxiv.Client()
        search = arxiv.Search(
            query=search_query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        papers = []
        for result in client.results(search):
            # 检查提交日期是否在范围内
            if result.published.replace(tzinfo=None) < start_date:
                continue

            paper_info = {
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'summary': result.summary.replace('\n', ' '),
                'pdf_url': result.pdf_url,
                'published': result.published.strftime('%Y-%m-%d'),
                'categories': result.categories,
                'arxiv_id': result.entry_id.split('/')[-1]
            }
            papers.append(paper_info)

        print(f"找到 {len(papers)} 篇相关论文")
        return papers

    def save_papers(self, papers: List[Dict], filepath: str):
        """
        保存论文信息到文件

        Args:
            papers: 论文信息列表
            filepath: 保存路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        print(f"论文信息已保存到: {filepath}")

    def load_papers(self, filepath: str) -> List[Dict]:
        """
        从文件加载论文信息

        Args:
            filepath: 文件路径

        Returns:
            论文信息列表
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        return papers


if __name__ == "__main__":
    # 测试代码
    fetcher = ArxivFetcher(categories=['cs.AI', 'cs.LG'], max_results=5)
    papers = fetcher.fetch_recent_papers(days=7)

    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   作者: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
        print(f"   发布时间: {paper['published']}")
