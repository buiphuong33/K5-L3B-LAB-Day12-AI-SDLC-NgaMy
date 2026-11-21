"""Độ tươi ở quán và bàn giao kho theo TICKET-03 (hộp đen qua headless_cmd)."""

import json
import unittest

from helpers import Workdir, events, read_jsonl, run_headless, snapshots, write_json

DISH = "ca_loc_nuong_trui"


def item(ident, kind="ca_loc", fresh=100):
    return {"id": ident, "kind": kind, "fresh": fresh}


def customer(ident="C1", table="T1", dish=DISH, **extra):
    return dict({"id": ident, "table_id": table, "dish_id": dish}, **extra)


def play(block, ticks, inputs=()):
    with Workdir() as w:
        scenario = write_json(w.path("s.json"), {"quan": dict({"random_customers": False}, **block)})
        frames = write_json(w.path("i.json"), {"frames": list(inputs)})
        code, err = run_headless("--mode", "quan", "--seed", "42", "--scenario", scenario, "--inputs", frames,
                                 "--ticks", str(ticks), "--snapshot-every", "1", "--out", w.path("o.jsonl"))
        if code:
            raise AssertionError(err)
        return read_jsonl(w.path("o.jsonl"))


class QuanFreshness(unittest.TestCase):
    def test_decay_quarter_point_per_second(self):
        rows = play({"stock": [item("I1")]}, 60)
        self.assertAlmostEqual(snapshots(rows)[-1]["stock"][0]["fresh"], 99.75, delta=0.01)

    def test_spoiled_once_exactly_when_crossing_30(self):
        rows = play({"stock": [item("I2", fresh=30 + 1 / 240), item("I1", fresh=30)]}, 3)
        spoiled = events(rows, "spoiled")
        self.assertEqual([(e["tick"], e["data"]["item_id"]) for e in spoiled], [(1, "I1"), (2, "I2")])
        self.assertEqual(spoiled[0]["data"], {"item_id": "I1", "kind": "ca_loc", "location": "stock"})

    def test_default_reservation_takes_freshest_then_id(self):
        stock = [item("I1", fresh=60), item("I3", fresh=80), item("I2", fresh=80)]
        rows = play({"stock": stock, "customers": [customer()]}, 0)
        self.assertEqual(snapshots(rows)[0]["customers"][0]["reserved"], ["I2"])

    def test_reservation_retries_when_held_item_spoils(self):
        rows = play({"stock": [item("I1", fresh=30), item("I2", fresh=80)],
                     "customers": [customer(reserved=["I1"])]}, 1)
        c = snapshots(rows)[-1]["customers"][0]
        self.assertEqual((c["reserved"], c["order_status"]), (["I2"], "reserved"))

    def test_unfulfillable_when_no_replacement(self):
        rows = play({"stock": [item("I1", fresh=30)], "customers": [customer(reserved=["I1"])]}, 1)
        c = snapshots(rows)[-1]["customers"][0]
        self.assertEqual((c["reserved"], c["order_status"]), ([], "unfulfillable"))

    def test_price_floor_from_average_fresh(self):
        stock = [item("I1", "ca_linh", 90), item("I2", "ca_linh", 80), item("I3", "ca_linh", 70),
                 item("I4", "bong_dien_dien", 60)]
        rows = play({"player": {"pos": [2, 8]}, "stock": stock,
                     "customers": [customer(dish="lau_ca_linh_dien_dien")]}, 1, [{"tick": 0, "interact": True}])
        data = events(rows, "cook_started")[0]["data"]
        self.assertEqual(data["base_price"], 89)  # floor(120 × trung bình ≈ 74.998 / 100)
        self.assertEqual([x["id"] for x in data["items"]], ["I4", "I1", "I2", "I3"])

    def test_spoiled_item_cannot_be_reserved_in_fixture(self):
        with Workdir() as w:
            s = write_json(w.path("s.json"), {"quan": {"stock": [item("I1", fresh=29)],
                                                       "customers": [customer(reserved=["I1"])]}})
            code, _ = run_headless("--mode", "quan", "--seed", "1", "--scenario", s, "--ticks", "0",
                                   "--out", w.path("o.jsonl"))
            self.assertEqual(code, 2)


class Handoff(unittest.TestCase):
    def dock(self, w, fresh):
        s = write_json(w.path("g.json"), {"gather": {"hold": [item("I1", "ca_linh", fresh)],
                                                     "random_fish": False, "monsters": []}})
        i = write_json(w.path("i.json"), {"frames": [{"tick": 0, "interact": True}]})
        code, err = run_headless("--mode", "gather", "--seed", "42", "--scenario", s, "--inputs", i, "--ticks", "1",
                                 "--out", w.path("g.jsonl"), "--inventory-out", w.path("kho.json"))
        self.assertEqual(code, 0, err)
        with open(w.path("kho.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_file_matches_quan_snapshot_exactly(self):
        with Workdir() as w:
            saved = self.dock(w, 100)
            self.assertEqual(saved["items"][0]["fresh"], 100 - 1 / 120)
            code, err = run_headless("--mode", "quan", "--seed", "42", "--inventory", w.path("kho.json"),
                                     "--ticks", "0", "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            self.assertEqual(snapshots(read_jsonl(w.path("q.jsonl")))[0]["stock"], saved["items"])

    def test_reloaded_value_keeps_threshold_branch(self):
        with Workdir() as w:
            self.dock(w, 30 + 1 / 120 + 1 / 240)  # sau bước gather còn đúng 30 + 1/240
            code, err = run_headless("--mode", "quan", "--seed", "42", "--inventory", w.path("kho.json"),
                                     "--ticks", "3", "--snapshot-every", "1", "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            self.assertEqual([e["tick"] for e in events(read_jsonl(w.path("q.jsonl")), "spoiled")], [2])

    def test_count_inventory_rejected(self):
        with Workdir() as w:
            old = write_json(w.path("old.json"), {"items": {"ca_loc": 1}})
            code, _ = run_headless("--mode", "quan", "--seed", "1", "--inventory", old, "--ticks", "0",
                                   "--out", w.path("q.jsonl"))
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
