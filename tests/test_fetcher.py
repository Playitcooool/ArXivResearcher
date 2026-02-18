from arxiv_researcher.fetcher import ArxivFetcher


def test_build_query_with_keyword() -> None:
    fetcher = ArxivFetcher(categories=["cs.AI", "cs.LG"], max_results=5, query="transformer")
    query = fetcher.build_query()
    assert "transformer" in query
    assert "cat:cs.AI" in query
    assert "cat:cs.LG" in query


def test_build_query_without_keyword() -> None:
    fetcher = ArxivFetcher(categories=["cs.CV"], max_results=5, query="")
    assert fetcher.build_query() == "cat:cs.CV"
