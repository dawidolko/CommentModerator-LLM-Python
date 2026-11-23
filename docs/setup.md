# Setup

Two ways to run the project: everything in Docker, or Python on the host. Both use the same three models.

| Role | Model | Size | Why this one |
|---|---|---|---|
| text | `qwen2.5:7b` | 4.7 GB | handles Polish and English well, follows a JSON schema |
| vision | `gemma3:4b` | 3.3 GB | reads text from images, small enough for 16–18 GB of RAM |
| embeddings | `nomic-embed-text` | 0.3 GB | dense search over the paragraphs of the forum rules |

The baseline `unitary/toxic-bert` (Hugging Face, about 440 MB) is downloaded on its first use.

## 1. Docker (any system)

Requirements: Docker Desktop (or Docker Engine with Compose v2), about 12 GB of free disk and 8 GB of memory for Docker.

```bash
git clone https://github.com/dawidolko/CommentModerator-LLM-Python.git
cd CommentModerator-LLM-Python
docker compose -f .tools/docker/docker-compose.yml up --build
```

The stack has three services:

- `ollama` serves the models on port 11434 inside the Compose network; the models live in the `ollama` volume,
- `models` runs once, pulls the three models and exits,
- `app` waits for `models`, then serves the web app on <http://localhost:7860>.

The CLI runs in the same container:

```bash
docker compose -f .tools/docker/docker-compose.yml exec app moderator check
docker compose -f .tools/docker/docker-compose.yml exec app moderator rag "Kup tanie konto premium, kod RABAT50!"
```

Files written by the app (`out/`) are bind-mounted back to the host.

### macOS: use the GPU

Docker on macOS has no access to the Apple GPU, so Ollama inside a container runs on the CPU only. With Ollama installed
natively ([ollama.com/download](https://ollama.com/download)) the container can use it instead:

```bash
ollama pull qwen2.5:7b && ollama pull gemma3:4b && ollama pull nomic-embed-text
OLLAMA_HOST=http://host.docker.internal:11434 \
  docker compose -f .tools/docker/docker-compose.yml up --build --no-deps app
```

`./start.sh` does this automatically when it finds Ollama running on a Mac.

## 2. Python on the host

Requirements: Python 3.11 or newer and Ollama.

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env                  # Windows: copy .env.example .env
ollama pull qwen2.5:7b
ollama pull gemma3:4b
ollama pull nomic-embed-text
moderator check
```

`moderator check` lists the three models and says which one is missing.

## 3. Configuration

`config.yaml` holds the model parameters and paths; `.env` (or environment variables) overrides the Ollama address and
the model names:

| Variable | Default | Meaning |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | where Ollama listens |
| `TEXT_MODEL` | `qwen2.5:7b` | the model that classifies and chats |
| `VISION_MODEL` | `gemma3:4b` | the model that reads images |
| `EMBED_MODEL` | `nomic-embed-text` | the model behind dense search |
| `HF_HUB_DISABLE_XET` | `1` | avoids failed downloads from Hugging Face seen during the labs |

What every generation parameter does is described in [parameters.md](parameters.md).

## 4. Tests

```bash
pytest
```

The tests replace Ollama with a fake model, so they run without any model pulled.
