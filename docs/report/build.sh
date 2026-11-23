#!/usr/bin/env bash
# =============================================================================
# Builds the course report from the LaTeX sections: the PDF with tectonic and
# the DOCX with pandoc (sprawozdanie_docx.tex swaps the screenshot macro for a
# plain figure that pandoc understands). Both land in docs/ next to this folder.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")"

tectonic -X compile sprawozdanie.tex
mv sprawozdanie.pdf ../Sprawozdanie_Projekt_LLM.pdf

pandoc sprawozdanie_docx.tex -f latex -t docx --toc --toc-depth=2 --resource-path=.:img \
  -M lang=pl-PL -M toc-title="Spis treści" -o ../Sprawozdanie_Projekt_LLM.docx

echo "docs/Sprawozdanie_Projekt_LLM.pdf and docs/Sprawozdanie_Projekt_LLM.docx are ready"
