"""Phase 3 — lát 1: schema kho cá thể, độ tươi, bàn giao (chủ: Phương).

Kiểm trực tiếp `chonoi.items` và `chonoi.inventory` (không cần gather/quan v1.2), nên chạy được ngay
khi contract còn 1.1. Smoke hộp đen qua headless nằm ở tests/test_p3_smoke.py (Huyền).
"""

import json
import os
import unittest
from fractions import Fraction

from helpers import Workdir, write_json

from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inventory import KINDS, read_inventory, write_inventory
from chonoi import items as I

FR = I.Freshness({"freshness": {"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30}})


class Freshness(unittest.TestCase):
    def test_p3_inv_01_rates_exact(self):
        self.assertEqual(FR.gather_per_tick, Fraction(1, 120))   # 0.5/s
        self.assertEqual(FR.quan_per_tick, Fraction(1, 240))     # 0.25/s

    def test_p3_inv_02_spoil_at_exactly_30_on_first_step(self):
        """Ticket: cá thể bắt đầu đúng fresh 30 thì ươn ở bước đầu; spoiled đúng một lần."""
        hold = [{"id": "I1", "kind": "ca_linh", "fresh": Fraction(30)}]
        self.assertFalse(FR.is_spoiled(hold[0]))
        self.assertEqual([i["id"] for i in I.decay(hold, FR.gather_per_tick, FR)], ["I1"])
        self.assertTrue(FR.is_spoiled(hold[0]))
        self.assertEqual(I.decay(hold, FR.gather_per_tick, FR), [])  # không phát lần hai

    def test_p3_inv_03_spoiled_sorted_by_id_and_clamped(self):
        st = [{"id": "I10", "kind": "ca_loc", "fresh": Fraction(30)},
              {"id": "I2", "kind": "ca_loc", "fresh": Fraction(30)},
              {"id": "I3", "kind": "ca_loc", "fresh": Fraction(0)}]
        self.assertEqual([i["id"] for i in I.decay(st, FR.quan_per_tick, FR)], ["I2", "I10"])
        self.assertEqual(st[2]["fresh"], 0)

    def test_p3_inv_04_100_to_30_takes_exact_ticks(self):
        it = [{"id": "I1", "kind": "ca_loc", "fresh": Fraction(100)}]
        n = 0
        while not I.decay(it, FR.gather_per_tick, FR):
            n += 1
        self.assertEqual(n + 1, 70 * 120 + 1)  # 30 đúng sau 8400 bước, ươn ở bước 8401

    def test_p3_inv_05_new_ids_continue(self):
        ids = IdAllocator()
        I.reserve_ids(ids, [{"id": "I7", "kind": "ca_loc", "fresh": Fraction(1)}])
        a, b = I.new_item(ids, "ca_loc", fr=FR), I.new_item(ids, "bong_sung", fr=FR)
        self.assertEqual((a["id"], b["id"], a["fresh"]), ("I8", "I9", 100))

    def test_p3_inv_06_price_and_freshest(self):
        used = [{"id": "I1", "kind": "ca_linh", "fresh": Fraction(100)},
                {"id": "I2", "kind": "ca_linh", "fresh": Fraction("97.5")}]
        self.assertEqual(I.fresh_price(120, used), 118)   # floor(120 × 98.75 / 100) = 118.5 → 118
        pool = [{"id": "I3", "kind": "ca_loc", "fresh": Fraction(80)},
                {"id": "I1", "kind": "ca_loc", "fresh": Fraction(80)},
                {"id": "I2", "kind": "ca_loc", "fresh": Fraction(29)},   # ươn
                {"id": "I4", "kind": "ca_loc", "fresh": Fraction(90)}]
        self.assertEqual([i["id"] for i in I.freshest(pool, "ca_loc", 2, FR)], ["I4", "I1"])
        self.assertIsNone(I.freshest(pool, "ca_loc", 4, FR))


class InventoryFile(unittest.TestCase):
    def test_p3_inv_10_roundtrip_sorted_exact(self):
        with Workdir() as w:
            p = w.path("k.json")
            src = [{"id": "I10", "kind": "ca_loc", "fresh": Fraction(97.5)},
                   {"id": "I2", "kind": "ca_linh", "fresh": Fraction(100) - 7 * Fraction(1, 120)},
                   {"id": "I3", "kind": "bong_sung", "fresh": Fraction(29)}]
            write_inventory(p, src)
            raw = json.load(open(p, encoding="utf-8"))
            self.assertEqual([i["id"] for i in raw["items"]], ["I2", "I3", "I10"])
            back = read_inventory(p, KINDS, version="1.2")
            self.assertEqual({i["id"]: float(i["fresh"]) for i in back}, {i["id"]: float(i["fresh"]) for i in src})
            self.assertTrue(FR.is_spoiled([i for i in back if i["id"] == "I3"][0]))  # hàng ươn vẫn nhận

    def test_p3_inv_11_empty(self):
        with Workdir() as w:
            p = w.path("k.json")
            write_inventory(p, [])
            self.assertEqual(open(p, encoding="utf-8").read().strip(), '{"items":[]}')
            self.assertEqual(read_inventory(p, KINDS, version="1.2"), [])

    def test_p3_inv_12_v12_rejects_bad(self):
        bad = [{"items": {"ca_loc": 1}},                                         # kho đếm
               {"items": [{"id": "I1", "kind": "ca_ro", "fresh": 50}]},          # kind lạ
               {"items": [{"id": "I1", "kind": "ca_loc", "fresh": 50}] * 2},     # id trùng
               {"items": [{"id": "I1", "kind": "ca_loc", "fresh": 100.5}]},      # fresh ngoài miền
               {"items": [{"id": "I1", "kind": "ca_loc", "fresh": -1}]},
               {"items": [{"id": "", "kind": "ca_loc", "fresh": 1}]},            # id rỗng
               {"items": [{"id": "I1", "kind": "ca_loc"}]},                      # thiếu fresh
               {"items": [{"id": "I1", "kind": "ca_loc", "fresh": True}]},
               {"items": [], "extra": 1}]
        with Workdir() as w:
            for i, obj in enumerate(bad):
                p = write_json(w.path(f"b{i}.json"), obj)
                with self.assertRaises(BadInput, msg=obj):
                    read_inventory(p, KINDS, version="1.2")

    def test_p3_inv_13_v11_still_counts(self):
        with Workdir() as w:
            p = write_json(w.path("c.json"), {"items": {"ca_loc": 1}})
            self.assertEqual(read_inventory(p, KINDS, version="1.1"), {"ca_loc": 1})

    def test_p3_inv_14_atomic_write_keeps_dir_clean(self):
        with Workdir() as w:
            p = w.path("k.json")
            write_inventory(p, [{"id": "I1", "kind": "ca_loc", "fresh": Fraction(100)}])
            self.assertEqual(sorted(os.listdir(os.path.dirname(p))), ["k.json"])


if __name__ == "__main__":
    unittest.main()
