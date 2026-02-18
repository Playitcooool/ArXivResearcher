from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class ArxivConfig:
    categories: list[str] = field(default_factory=lambda: ["cs.AI", "cs.LG"])
    max_results: int = 10
    query: str = ""


@dataclass(slots=True)
class OllamaConfig:
    base_url: str = "http://localhost:11434"
    model: str = "qwen3:8b"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout_seconds: int = 120


@dataclass(slots=True)
class OutputConfig:
    save_dir: str = "./papers"
    log_level: str = "INFO"
    log_file: str = ""


@dataclass(slots=True)
class AppConfig:
    arxiv: ArxivConfig = field(default_factory=ArxivConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    @property
    def save_dir_path(self) -> Path:
        return Path(self.output.save_dir)


def _deep_update(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _deep_update(base[key], value)
        else:
            base[key] = value
    return base


def _as_dict(config: AppConfig) -> dict[str, Any]:
    return {
        "arxiv": {
            "categories": config.arxiv.categories,
            "max_results": config.arxiv.max_results,
            "query": config.arxiv.query,
        },
        "ollama": {
            "base_url": config.ollama.base_url,
            "model": config.ollama.model,
            "temperature": config.ollama.temperature,
            "max_tokens": config.ollama.max_tokens,
            "timeout_seconds": config.ollama.timeout_seconds,
        },
        "output": {
            "save_dir": config.output.save_dir,
            "log_level": config.output.log_level,
            "log_file": config.output.log_file,
        },
    }


def _apply_env_overrides(data: dict[str, Any]) -> dict[str, Any]:
    mapping = {
        "ARXIV_CATEGORIES": ("arxiv", "categories"),
        "ARXIV_MAX_RESULTS": ("arxiv", "max_results"),
        "ARXIV_QUERY": ("arxiv", "query"),
        "OLLAMA_BASE_URL": ("ollama", "base_url"),
        "OLLAMA_MODEL": ("ollama", "model"),
        "OLLAMA_TEMPERATURE": ("ollama", "temperature"),
        "OLLAMA_MAX_TOKENS": ("ollama", "max_tokens"),
        "OLLAMA_TIMEOUT_SECONDS": ("ollama", "timeout_seconds"),
        "OUTPUT_SAVE_DIR": ("output", "save_dir"),
        "LOG_LEVEL": ("output", "log_level"),
        "LOG_FILE": ("output", "log_file"),
    }

    for env_key, path in mapping.items():
        raw = os.getenv(env_key)
        if raw is None or raw == "":
            continue

        section, key = path
        if env_key == "ARXIV_CATEGORIES":
            value: Any = [x.strip() for x in raw.split(",") if x.strip()]
        elif env_key in {"ARXIV_MAX_RESULTS", "OLLAMA_MAX_TOKENS", "OLLAMA_TIMEOUT_SECONDS"}:
            value = int(raw)
        elif env_key == "OLLAMA_TEMPERATURE":
            value = float(raw)
        else:
            value = raw

        data.setdefault(section, {})[key] = value

    return data


def _validate(config: AppConfig) -> None:
    if not config.arxiv.categories:
        raise ValueError("`arxiv.categories` 不能为空")
    if config.arxiv.max_results <= 0:
        raise ValueError("`arxiv.max_results` 必须大于 0")
    if not config.ollama.base_url.startswith(("http://", "https://")):
        raise ValueError("`ollama.base_url` 必须是 HTTP/HTTPS 地址")
    if config.ollama.max_tokens <= 0:
        raise ValueError("`ollama.max_tokens` 必须大于 0")
    if config.ollama.timeout_seconds <= 0:
        raise ValueError("`ollama.timeout_seconds` 必须大于 0")


def load_config(config_path: str | Path | None = None) -> AppConfig:
    base = _as_dict(AppConfig())

    if config_path:
        p = Path(config_path)
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                payload = yaml.safe_load(f) or {}
            if not isinstance(payload, dict):
                raise ValueError("配置文件格式错误，顶层必须是字典")
            base = _deep_update(base, payload)

    base = _apply_env_overrides(base)

    config = AppConfig(
        arxiv=ArxivConfig(**base.get("arxiv", {})),
        ollama=OllamaConfig(**base.get("ollama", {})),
        output=OutputConfig(**base.get("output", {})),
    )
    _validate(config)
    return config
