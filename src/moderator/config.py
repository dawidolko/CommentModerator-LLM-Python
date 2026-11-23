"""
Settings of the app. config.yaml holds the model options and paths; environment variables (or .env) override the
Ollama address and the model names, so the same image runs against Ollama in Docker or on the host.
"""

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    ollama_host: str
    text_model: str
    vision_model: str
    embed_model: str
    generation: dict = field(default_factory=dict)
    chat: dict = field(default_factory=dict)
    retrieval: dict = field(default_factory=dict)
    baseline: dict = field(default_factory=dict)
    paths: dict = field(default_factory=dict)

    def path(self, key: str) -> Path:
        value = Path(self.paths[key])
        return value if value.is_absolute() else ROOT / value

    @property
    def output_dir(self) -> Path:
        directory = self.path("output")
        directory.mkdir(parents=True, exist_ok=True)
        return directory


def load_settings(config_file: Path | None = None) -> Settings:
    load_dotenv(ROOT / ".env")
    raw = yaml.safe_load((config_file or ROOT / "config.yaml").read_text(encoding="utf-8"))
    models = raw["models"]
    return Settings(
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        text_model=os.getenv("TEXT_MODEL", models["text"]),
        vision_model=os.getenv("VISION_MODEL", models["vision"]),
        embed_model=os.getenv("EMBED_MODEL", models["embed"]),
        generation=raw.get("generation", {}),
        chat=raw.get("chat", {}),
        retrieval=raw.get("retrieval", {}),
        baseline=raw.get("baseline", {}),
        paths=raw.get("paths", {}),
    )


@lru_cache
def settings() -> Settings:
    return load_settings()
