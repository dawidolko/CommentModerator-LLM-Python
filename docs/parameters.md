# Ollama parameters

Every call to Ollama takes an `options` object. The values used by the app are in `config.yaml`: `generation` for
moderation (short, repeatable JSON answers) and `chat` for the conversation (longer, a little more varied text).

| Parameter | App value | What it does | When to change it |
|---|---|---|---|
| `temperature` | 0.1 (chat 0.3) | Divides the logits before sampling. Low values make the most likely token win almost every time, high values flatten the distribution. | Keep it low for decisions; raise it for creative text. |
| `top_p` | 0.9 | Nucleus sampling: samples only from the smallest set of tokens whose probabilities add up to `top_p`. | Lower it to cut off unlikely words. |
| `top_k` | 40 | Samples only from the `top_k` most likely tokens. `top_k = 1` is greedy decoding. | Lower for stable output, higher for variety. |
| `seed` | 42 | Fixes the random generator, so the same prompt and options give the same answer. | Remove it to see the natural variation of the model. |
| `num_ctx` | 4096 (chat 8192) | Context window in tokens: prompt, examples, rules and answer must fit in it. A larger window takes more memory and time. | Raise it for long files in the chat. |
| `num_predict` | 300 (chat 700) | Maximum number of generated tokens. Too low cuts the answer in the middle. | Lower for speed, never below the length of the JSON answer. |
| `repeat_penalty` | 1.1 | Lowers the probability of tokens that already appeared, against loops like the ones GPT-2 produced in Lab 1. | Raise if the model repeats itself. |
| `stop` | none | Generation stops when one of these strings appears. | Cut the answer at a marker, e.g. a new `User:` line. |
| `format` | JSON schema | Constrains generation to valid JSON that matches the schema of `Verdict`. | Always for answers that code parses. |
| `keep_alive` | 30m | How long the model stays loaded after the last call (a request parameter, not an option). | Shorter on a machine with little memory. |

## Experiment

`python scripts/parameter_experiment.py` sends the same requests with different options to `qwen2.5:7b` and writes
[examples/parameters/parameters.json](../examples/parameters/parameters.json). The results of the run used in the
report are summarised in [examples/parameters/README.md](../examples/parameters/README.md).
