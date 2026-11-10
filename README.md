# Adaptive RAG efficiency lab · v0.1.0

An offline retrieval experiment inspired by AMIE and RadCopilot. The fixed baseline ranks runbook snippets by lexical overlap. The adaptive variant bypasses ranking when it finds a single known runbook ID. Both use the same synthetic corpus, queries, relevance labels, and abstention rules.

## Reproduce

Python 3.11 or later. No third-party dependencies or credentials.

```bash
python -m unittest -q
python benchmark.py
```

See [results-v1.json](results-v1.json) for exact citation sets, abstentions, retrieved context size, and p50/p95 retrieval latency across repeated runs. Word count is a proxy for input size. This build measures retrieval only and uses no model tokenizer or generation provider.

The single-ID shortcut can lose relevant context when the query also asks about a second runbook. The dataset includes this case explicitly. With six synthetic documents, timings describe this local run and can vary with hardware and process load.

## Guarded shortcut experiment

The guarded variant takes the single-ID shortcut only when the referenced
document also contains every non-stop-word query term. Otherwise it uses the
fixed ranking. For `r04 restore drills`, this fallback retrieves both labeled
documents (`r03` and `r04`).

| Strategy | Exact citation sets | Correct abstentions | Mean context words |
| --- | ---: | ---: | ---: |
| Fixed | 10/10 | 2/2 | 10.9 |
| Adaptive | 9/10 | 2/2 | 9.9 |
| Guarded adaptive | 10/10 | 2/2 | 10.9 |

[Raw results](results-guarded-v1.json) include per-query evidence and timings.
This is a regression check on the existing synthetic cases. It does not
establish that the guard generalizes or improves latency.
