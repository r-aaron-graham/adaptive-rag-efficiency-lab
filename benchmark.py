"""Compare fixed and identifier-aware lexical retrieval on synthetic runbooks."""

import argparse
import json
from pathlib import Path
import re
from statistics import quantiles
from time import perf_counter_ns

STOP_WORDS = {"a", "an", "and", "are", "for", "in", "the", "to", "we", "when", "should"}


def words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def retrieve(query, documents, index, adaptive, *, require_term_coverage=False):
    query_words = set(words(query)) - STOP_WORDS
    identifiers = query_words & documents.keys()
    if adaptive and len(identifiers) == 1:
        doc_id = next(iter(identifiers))
        if not require_term_coverage or query_words <= index[doc_id]:
            return [doc_id]

    scored = [
        (len(query_words & tokens), doc_id)
        for doc_id, tokens in index.items()
    ]
    return [doc_id for score, doc_id in sorted(scored, key=lambda x: (-x[0], x[1]))[:3]
            if score >= 2 or doc_id in identifiers]


def evaluate(dataset, adaptive, repeats, *, require_term_coverage=False):
    documents = dataset["documents"]
    index = {doc_id: set(words(f"{doc_id} {body}")) for doc_id, body in documents.items()}
    rows = []
    samples = []
    for case in dataset["cases"]:
        for _ in range(repeats):
            start = perf_counter_ns()
            citations = retrieve(
                case["query"], documents, index, adaptive,
                require_term_coverage=require_term_coverage,
            )
            samples.append(perf_counter_ns() - start)
        expected = set(case["expected"])
        rows.append({
            **case, "citations": citations, "exact": set(citations) == expected,
            "context_words": sum(len(words(documents[doc_id])) for doc_id in citations),
        })

    abstention = [row for row in rows if not row["expected"]]
    return {
        "exact_citations": sum(row["exact"] for row in rows),
        "cases": len(rows),
        "correct_abstentions": sum(row["exact"] for row in abstention),
        "abstention_cases": len(abstention),
        "mean_context_words": sum(row["context_words"] for row in rows) / len(rows),
        "retrieval_latency_ns": {
            "p50": round(quantiles(samples, n=100)[49]),
            "p95": round(quantiles(samples, n=100)[94]),
        },
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=200)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    dataset = json.loads(Path(__file__).with_name("dataset-v1.json").read_text())
    results = {label: evaluate(dataset, adaptive, args.repeats)
               for label, adaptive in (("fixed", False), ("adaptive", True))}
    results["guarded_adaptive"] = evaluate(
        dataset, True, args.repeats, require_term_coverage=True,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
