import json
from pathlib import Path
import unittest

from benchmark import evaluate


class RetrievalTests(unittest.TestCase):
    def test_identifier_route_and_its_failure_mode(self):
        dataset = json.loads(Path(__file__).with_name("dataset-v1.json").read_text())
        fixed = evaluate(dataset, False, 1)
        adaptive = evaluate(dataset, True, 1)
        self.assertTrue(adaptive["rows"][1]["exact"])
        self.assertTrue(fixed["rows"][-1]["exact"])
        self.assertFalse(adaptive["rows"][-1]["exact"])
        self.assertEqual(adaptive["correct_abstentions"], 2)

    def test_guard_falls_back_for_mixed_intent(self):
        dataset = json.loads(Path(__file__).with_name("dataset-v1.json").read_text())
        guarded = evaluate(dataset, True, 1, require_term_coverage=True)
        self.assertEqual(guarded["rows"][-1]["citations"], ["r03", "r04"])
        self.assertEqual(guarded["rows"][1]["citations"], ["r02"])
        self.assertEqual(guarded["correct_abstentions"], 2)

    def test_checked_in_report_matches_reproducible_fields(self):
        directory = Path(__file__).parent
        dataset = json.loads((directory / "dataset-v1.json").read_text())
        expected = json.loads((directory / "results-guarded-v1.json").read_text())
        results = {
            "fixed": evaluate(dataset, False, 1),
            "adaptive": evaluate(dataset, True, 1),
            "guarded_adaptive": evaluate(dataset, True, 1, require_term_coverage=True),
        }
        for strategy, result in results.items():
            with self.subTest(strategy=strategy):
                expected_fields = dict(expected[strategy])
                del expected_fields["retrieval_latency_ns"]
                del result["retrieval_latency_ns"]
                self.assertEqual(result, expected_fields)
