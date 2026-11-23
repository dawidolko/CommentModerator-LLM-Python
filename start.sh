#!/usr/bin/env bash
# =============================================================================
# Starts Comment Moderator in Docker. On a Mac with Ollama already running, the
# app container uses that Ollama (GPU through Metal) instead of a CPU-only one.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")"

COMPOSE=(docker compose -f .tools/docker/docker-compose.yml)

if [[ "$(uname)" == "Darwin" ]] && curl -sf http://localhost:11434/api/tags >/dev/null; then
  echo "Ollama is running on this Mac, the app will use it (GPU through Metal)."
  for model in qwen2.5:7b gemma3:4b nomic-embed-text; do
    ollama list | grep -q "^${model%%:*}" || ollama pull "$model"
  done
  OLLAMA_HOST=http://host.docker.internal:11434 "${COMPOSE[@]}" up --build --no-deps -d app
else
  "${COMPOSE[@]}" up --build -d
fi

echo "Waiting for http://localhost:7860 ..."
until curl -sf http://localhost:7860/ >/dev/null; do sleep 3; done
echo "Comment Moderator is ready: http://localhost:7860"
echo "CLI in the container: ${COMPOSE[*]} exec app moderator --help"
