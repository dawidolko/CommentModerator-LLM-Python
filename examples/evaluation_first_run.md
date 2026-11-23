# Evaluation, first run

The first `moderator evaluate` run, before two fixes: the system prompt did not say that spam counts as `toxic`, and in
the RAG mode the `rule` field accepted any string or null. The prediction files of this run were overwritten by the
second run (`examples/evaluation/`); the summary below was copied from its terminal output.

40 labelled comments (22 toxic), text model `qwen2.5:7b`, embeddings `nomic-embed-text`.

| variant | threshold | precision | recall | f1 | category_acc | rule_acc | latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| toxic-bert @0.50 | 0.500 | 1.000 | 0.318 | 0.483 | 0.600 | – | – |
| toxic-bert @PR | 0.056 | 0.636 | 0.636 | 0.636 | 0.475 | – | – |
| LLM zero-shot | – | 0.947 | 0.818 | 0.878 | 0.925 | – | 1.841 |
| LLM few-shot | – | 0.957 | 1.000 | 0.978 | 0.950 | – | 1.853 |
| LLM rag | – | 0.957 | 1.000 | 0.978 | 0.925 | 0.600 | 3.784 |

What went wrong:

- zero-shot marked four spam comments as `toxic: false` while deciding `remove`: without a definition the model reads
  "toxic" as "rude", and spam is not rude;
- RAG answered `rule: null` for 8 violations (threats, swearing, an insult, a sexual message, spam), so the check
  sent them to `review` instead of `remove`, and for 4 clean comments that should cite §2.3; the rule accuracy was
  0.60;
- few-shot and RAG flagged "Kurde, znowu zapomniałem średnika. Klasyka." (a mild exclamation of frustration).
