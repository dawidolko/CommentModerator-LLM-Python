# Evaluation

40 labelled comments (22 toxic), text model `qwen2.5:7b`, embeddings `nomic-embed-text`.

## Toxic class, all comments

| variant | threshold | precision | recall | f1 | category_acc | rule_acc | latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| toxic-bert @0.50 | 0.500 | 1.000 | 0.318 | 0.483 | 0.600 | – | – |
| toxic-bert @PR | 0.056 | 0.636 | 0.636 | 0.636 | 0.475 | – | – |
| LLM zero-shot | – | 0.957 | 1.000 | 0.978 | 0.925 | – | 1.655 |
| LLM few-shot | – | 0.957 | 1.000 | 0.978 | 0.950 | – | 1.808 |
| LLM rag | – | 0.957 | 1.000 | 0.978 | 0.950 | 0.850 | 3.812 |

## By language

| variant | subset | precision | recall | f1 |
| --- | --- | --- | --- | --- |
| toxic-bert @0.50 | en | 1.000 | 0.556 | 0.714 |
| toxic-bert @0.50 | pl | 1.000 | 0.154 | 0.267 |
| toxic-bert @PR | en | 0.750 | 0.667 | 0.706 |
| toxic-bert @PR | pl | 0.571 | 0.615 | 0.593 |
| LLM zero-shot | en | 1.000 | 1.000 | 1.000 |
| LLM zero-shot | pl | 0.929 | 1.000 | 0.963 |
| LLM few-shot | en | 1.000 | 1.000 | 1.000 |
| LLM few-shot | pl | 0.929 | 1.000 | 0.963 |
| LLM rag | en | 1.000 | 1.000 | 1.000 |
| LLM rag | pl | 0.929 | 1.000 | 0.963 |

## Finding the right paragraph of the rules

| retriever | recall@1 | recall@3 | mrr |
| --- | --- | --- | --- |
| bm25 | 0.350 | 0.650 | 0.546 |
| dense | 0.525 | 0.850 | 0.682 |
| hybrid | 0.500 | 0.775 | 0.670 |
