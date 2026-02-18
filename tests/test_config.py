from arxiv_researcher.config import load_config


def test_load_default_config() -> None:
    config = load_config(None)
    assert config.arxiv.max_results > 0
    assert config.ollama.base_url.startswith("http")


def test_load_config_file(tmp_path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
arxiv:
  categories: [cs.CL]
  max_results: 3
ollama:
  model: qwen3:8b
  timeout_seconds: 30
output:
  save_dir: ./tmp_papers
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_file)
    assert config.arxiv.categories == ["cs.CL"]
    assert config.arxiv.max_results == 3
    assert config.ollama.timeout_seconds == 30
