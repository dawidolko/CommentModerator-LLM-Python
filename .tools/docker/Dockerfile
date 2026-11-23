# syntax=docker/dockerfile:1

# =============================================================================
# Comment Moderator: the Python app (web UI and CLI). Ollama runs in its own
# container from docker-compose.yml, or natively on the host on macOS.
#
# PyTorch comes from the CPU index: the default wheel bundles CUDA and is
# several times larger, while toxic-bert is the only model this image runs.
# =============================================================================

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml README.md config.yaml ./
COPY src ./src
COPY data ./data
COPY scripts ./scripts
COPY tests ./tests
COPY examples ./examples
RUN pip install --no-cache-dir --no-deps -e .

RUN useradd --create-home --uid 1000 moderator \
    && mkdir -p /app/out /app/.cache \
    && chown -R moderator:moderator /app
USER moderator

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/.cache/huggingface \
    HF_HUB_DISABLE_XET=1 \
    GRADIO_ANALYTICS_ENABLED=False \
    MPLCONFIGDIR=/tmp/matplotlib

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:7860/')" || exit 1

CMD ["moderator", "web", "--host", "0.0.0.0", "--port", "7860"]
