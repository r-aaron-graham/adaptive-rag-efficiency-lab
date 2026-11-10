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
