"""Quán v1.1: 2 bếp, 4 bàn, 6 món, khách theo lịch."""

import unittest

from helpers import Workdir, events, read_jsonl, run_headless, snapshots, write_json


def play(block, ticks):
    with Workdir() as w:
        s = write_json(w.path("s.json"), {"quan": block})
        code, err = run_headless("--mode", "quan", "--seed", "9", "--scenario", s, "--ticks", str(ticks),
                                 "--out", w.path("o.jsonl"))
        if code:
            raise AssertionError(err)
        return read_jsonl(w.path("o.jsonl"))


class Quan(unittest.TestCase):
    def test_layout(self):
        s = snapshots(play({}, 0))[0]
        self.assertEqual([x["id"] for x in s["stoves"]], ["B1", "B2"])
        self.assertEqual([x["id"] for x in s["tables"]], ["T1", "T2", "T3", "T4"])

    def test_new_dish_is_accepted(self):
        stock = {"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1}
        rows = play({"stock": stock, "random_customers": False,
                     "customers": [{"id": "C1", "table_id": "T4", "dish_id": "lau_mam"}]}, 0)
        self.assertEqual(snapshots(rows)[0]["customers"][0]["reserved"], stock)

    def test_arrivals_use_smallest_free_table_on_schedule(self):
        rows = play({"stock": {"ca_loc": 9}}, 1021)
        arrived = events(rows, "customer_arrived")
        self.assertEqual([(e["tick"], e["data"]["table_id"]) for e in arrived], [(120, "T1"), (1020, "T2")])


if __name__ == "__main__":
    unittest.main()
