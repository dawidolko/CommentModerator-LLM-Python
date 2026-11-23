# Parameter experiment

Output of `python scripts/parameter_experiment.py` with `qwen2.5:7b`; the raw answers are in
[parameters.json](parameters.json). The seed is left out unless a test says otherwise, so the natural variation of the
model is visible. What each parameter means is in [docs/parameters.md](../../docs/parameters.md).

| Test | Result |
| --- | --- |
| `temperature` 0 / 0.7 / 1.5, verdict on "Kurde, znowu zapomniałem średnika. Klasyka." five times, with the JSON schema | `review`, severity 1, every time at every temperature |
| `seed` at temperature 0.9, three free-text answers | seed 42: 1 distinct answer of 3; no seed: 3 of 3 |
| `top_p` 0.1 / 1.0 at temperature 1.0, five answers | 1 / 5 distinct answers |
| `top_k` 1 / 100 at temperature 1.0, five answers | 1 / 5 distinct answers |
| `num_predict` 15 | the JSON is cut in the middle: `{ "toxic": false, "categories": ["none"], "severity` |
| `format` none / `"json"` / schema, five comments | complete verdicts: 0 / 0 / 5 of 5; without the schema the model answered e.g. `{"toxic": true, "reason": "insult"}` |
| `num_ctx` 2048 / 16384, short prompt, second call | 1.26 s / 1.26 s: the window size matters for long input and memory, not for a short prompt |
| `stop` `[","]` | the answer ends right before its first comma |

The decision stays the same even at temperature 1.5 because the schema and a clear prompt leave the model little room;
temperature, `top_p` and `top_k` change free text a lot. That is why moderation uses the schema and temperature 0.1,
and the chat a slightly higher 0.3, both with a fixed seed.
