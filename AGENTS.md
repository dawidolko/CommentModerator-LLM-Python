# AGENTS.md

Guide for agents working on Comment Moderator. Add a section per area as conventions emerge — do not pad sections with
content that is not established yet.

## What this project is

A Python application that moderates forum comments with a local LLM served by Ollama: one comment, images, whole files,
a chat about a file and RAG over the forum rules, with a Typer CLI and a Gradio web app on one shared `Moderator`
class. It is the final project of a university course on large language models.

Read [README.md](README.md) first — it documents the architecture and the commands used day to day.

## Language

**Code, names, comments, the README and `docs/*.md` are English.** The course report in `docs/report/` is Polish, and
so are the sample comments and the fictional forum rules in `data/`.

## Comments

Every code file starts with one multi-line block comment (a module docstring in Python) that says what the file does
and why it looks the way it does. There are no other comments in the code; CLI help texts live in the `HELP` tables.

## Results

Every number in the README, the report and `examples/` comes from a real run. After changing a prompt, the schema or
the retriever, run `moderator evaluate` again and update the numbers, or say clearly that they are from an older run.

## Before finishing

- [ ] `ruff check .` and `ruff format --check .` pass.
- [ ] `pytest` passes (no Ollama needed).
- [ ] `docker compose -f .tools/docker/docker-compose.yml build` succeeds.
- [ ] No `.env`, models or `out/` committed.
