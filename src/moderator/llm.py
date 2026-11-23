"""
Thin client over the Ollama API: chat with an optional JSON schema, streamed chat, a request with an image and
embeddings. keep_alive keeps the model loaded between the comments of a file.
"""

from pathlib import Path

import ollama

from moderator.config import Settings


class LLM:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = ollama.Client(host=settings.ollama_host, timeout=600)

    def models(self) -> list[str]:
        return sorted(model.model for model in self.client.list().models)

    def missing_models(self) -> list[str]:
        available = set(self.models())
        wanted = [self.settings.text_model, self.settings.vision_model, self.settings.embed_model]
        return [name for name in wanted if name not in available and f"{name}:latest" not in available]

    def chat(
        self,
        messages: list[dict],
        options: dict | None = None,
        format: dict | str | None = None,
        model: str | None = None,
    ) -> str:
        response = self.client.chat(
            model=model or self.settings.text_model,
            messages=messages,
            options=options if options is not None else self.settings.generation,
            format=format,
            keep_alive="30m",
        )
        return response.message.content

    def stream(self, messages: list[dict], options: dict | None = None):
        for part in self.client.chat(
            model=self.settings.text_model,
            messages=messages,
            options=options if options is not None else self.settings.chat,
            stream=True,
            keep_alive="30m",
        ):
            yield part.message.content

    def look(self, image: Path | bytes, prompt: str) -> str:
        return self.chat(
            [{"role": "user", "content": prompt, "images": [image]}],
            options={**self.settings.generation, "num_predict": 400},
            model=self.settings.vision_model,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        return list(self.client.embed(model=self.settings.embed_model, input=texts).embeddings)
