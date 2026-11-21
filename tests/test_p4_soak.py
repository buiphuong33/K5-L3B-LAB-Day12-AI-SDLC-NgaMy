"""Phase 4 soak runner: deterministic 10-day integration through DaySim."""

import json
import tempfile
import unittest
from pathlib import Path

from chonoi.contract import load_contract
from chonoi.soak import MAX_DAYS, _extend_day_plans, _ingredient_fixture, main, run_soak


class SoakTests(unittest.TestCase):
    def test_day_plans_repeat_first_five(self):
        tuning = load_contract()["tuning"]
        extended = _extend_day_plans(tuning, MAX_DAYS)

        self.assertEqual([plan["day"] for plan in extended["day_plan"]], list(range(1, 11)))
        for day in range(1, 6):
            self.assertEqual(extended["day_plan"][day - 1]["dishes"],
                             extended["day_plan"][day + 4]["dishes"])
            self.assertEqual(extended["day_plan"][day - 1]["ingredients"],
                             extended["day_plan"][day + 4]["ingredients"])

    def test_fixture_contains_exact_planned_ingredients(self):
        tuning = load_contract()["tuning"]
        for plan in tuning["day_plan"]:
            fixture = _ingredient_fixture(tuning, plan)
            counts = {}
            for item in fixture:
                counts[item["kind"]] = counts.get(item["kind"], 0) + 1
            self.assertEqual(counts, plan["ingredients"])
            self.assertEqual(len(fixture), sum(plan["ingredients"].values()))
            self.assertTrue(all(item["fresh"] == tuning["freshness"]["initial"] for item in fixture))

    def test_ten_day_soak_is_deterministic_and_finishes(self):
        first = run_soak(seed=17, days=MAX_DAYS)
        second = run_soak(seed=17, days=MAX_DAYS)

        self.assertEqual(first["days"], MAX_DAYS)
        self.assertEqual(first["days_completed"], MAX_DAYS)
        self.assertEqual(first["crashes"], 0)
        self.assertEqual([result["day"] for result in first["results"]], list(range(1, 11)))
        for result in first["results"]:
            self.assertEqual(set(result), {"day", "earned", "reputation", "score"})
        self.assertEqual(first["results"], second["results"])

    def test_cli_writes_contract_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "soak.json"
            self.assertEqual(main(["--seed", "2", "--days", "1", "--out", str(output)]), 0)
            result = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(set(result), {"days", "days_completed", "crashes", "results", "duration_s"})
        self.assertEqual(result["days_completed"], 1)
        self.assertEqual(result["crashes"], 0)


if __name__ == "__main__":
    unittest.main()
