#!/usr/bin/env bash
# =============================================================================
# Packs the project for the course submission as Imie_Nazwisko_Album_Projekt_LLM.zip:
# every file tracked by git (code, data, examples, docs with the report in PDF and
# DOCX), without the virtual environment, the models or the runtime output.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

NAME="Dawid_Olko_125148_Projekt_LLM"
mkdir -p dist
rm -f "dist/$NAME.zip"
git archive --format=zip --prefix="$NAME/" -o "dist/$NAME.zip" HEAD
echo "dist/$NAME.zip ($(du -h "dist/$NAME.zip" | cut -f1))"
