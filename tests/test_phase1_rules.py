"""Luật lõi Phase 1 theo Test Contract v1.0 mục E, F, G (chạy hộp đen qua headless_cmd)."""

import json
import os
import unittest

from helpers import (IS_V12, Workdir, empty_inventory, events, individual_hold,
                     item_kinds, read_jsonl, run_headless, snapshots, write_json)

DISH = "ca_loc_nuong_trui"
PAYLOAD = {"order_id": "C1", "dish_id": DISH, "base_price": 60}


def play(mode, block, inputs, ticks, inv_out=False):
    with Workdir() as w:
        args = ["--mode", mode, "--seed", "42", "--ticks", str(ticks), "--snapshot-every", "1",
                "--scenario", write_json(w.path("s.json"), {mode: block}),
                "--inputs", write_json(w.path("i.json"), {"frames": inputs}), "--out", w.path("o.jsonl")]
        if inv_out:
            args += ["--inventory-out", w.path("kho.json")]
        code, err = run_headless(*args)
        if code != 0:
            return code, err, None
        inventory = None
        if inv_out and os.path.exists(w.path("kho.json")):
            with open(w.path("kho.json"), encoding="utf-8") as f:
                inventory = json.load(f)
        return code, inventory, read_jsonl(w.path("o.jsonl"))


def river(pos, **extra):
    player = dict({"pos": pos}, **extra.pop("player", {}))
    return dict({"player": player, "nodes": [], "fish": [], "random_fish": False}, **extra)


class GatherRules(unittest.TestCase):
    def run_ok(self, *a, **k):
        code, inventory, rows = play("gather", *a, **k)
        self.assertEqual(code, 0, inventory)
        return rows, inventory

    def test_oxygen_drain_and_refill(self):
        rows, _ = self.run_ok(river([20, 5]), [], 1)
        self.assertEqual(snapshots(rows)[-1]["player"]["oxygen_ticks"], 1799)
        rows, _ = self.run_ok(river([20, 0], player={"oxygen_ticks": 100}), [], 1)
        self.assertEqual(snapshots(rows)[-1]["player"]["oxygen_ticks"], 106)

    def test_first_choke_at_t_plus_59(self):
        rows, _ = self.run_ok(river([20, 5], player={"oxygen_ticks": 1}), [], 61)
        empty = events(rows, "oxygen_empty")[0]
        self.assertEqual(empty["data"], {"oxygen_ticks": 0})
        choke = events(rows, "choke")[0]
        self.assertEqual(choke["tick"], empty["tick"] + 59)
        self.assertEqual(choke["data"], {"hp": 2})

    def test_faint_loses_hold_lifo_and_writes_empty_inventory(self):
        block = river([20, 5], hold=individual_hold("ca_loc", "bong_sung"),
                      player={"oxygen_ticks": 0, "hp": 1, "zero_oxy_ticks": 59})
        rows, inventory = self.run_ok(block, [], 5, inv_out=True)
        faint = events(rows, "faint")[0]["data"]
        self.assertEqual((faint["cause"], item_kinds(faint["lost"]), faint["hp"]),
                         ("choke", ["bong_sung", "ca_loc"], 0))
        self.assertEqual(events(rows, "gather_end")[0]["data"],
                         {"reason": "fainted", "inventory": empty_inventory()})
        self.assertEqual(inventory, empty_inventory())
        self.assertEqual(rows[-1]["reason"], "fainted")

    def test_harvest_at_exact_radius_then_regrow(self):
        node = {"id": "N1", "kind": "bong_sung", "pos": [22, 0]}
        rows, _ = self.run_ok(river([20, 0], nodes=[node]), [{"tick": 0, "interact": True}], 1201)
        self.assertEqual(events(rows, "gather")[0]["data"], {"node_id": "N1", "kind": "bong_sung", "amount": 1})
        self.assertEqual(events(rows, "node_regrown")[0]["tick"], 1201)

    def test_harvest_tie_uses_id_and_ignores_underwater(self):
        nodes = [{"id": "N10", "kind": "bong_sung", "pos": [21, 0]}, {"id": "N2", "kind": "bong_dien_dien", "pos": [19, 0]}]
        rows, _ = self.run_ok(river([20, 0], nodes=nodes), [{"tick": 0, "interact": True}], 1)
        self.assertEqual(events(rows, "gather")[0]["data"]["node_id"], "N2")
        rows, _ = self.run_ok(river([20, 1], nodes=nodes), [{"tick": 0, "interact": True}], 1)
        self.assertEqual(events(rows, "gather"), [])

    def test_harvest_hold_full_keeps_node(self):
        node = {"id": "N1", "kind": "bong_sung", "pos": [21, 0]}
        rows, _ = self.run_ok(river([20, 0], nodes=[node], hold=individual_hold(*(["ca_loc"] * 12))),
                              [{"tick": 0, "interact": True}], 1)
        self.assertEqual(events(rows, "hold_full")[0]["data"],
                         {"action": "gather", "node_id": "N1", "required": 1, "free": 0})
        self.assertTrue(snapshots(rows)[-1]["nodes"][0]["ready"])

    def test_catch_full_yield_and_cooldown(self):
        fish = [{"id": "F1", "kind": "ca_linh", "pos": [21, 5]}, {"id": "F2", "kind": "ca_loc", "pos": [20, 6.5]}]
        presses = [{"tick": 0, "catch": True}, {"tick": 1, "catch": False},
                   {"tick": 29, "catch": True}, {"tick": 30, "catch": False}, {"tick": 31, "catch": True}]
        rows, _ = self.run_ok(river([20, 5], fish=fish), presses, 32)
        caught = events(rows, "fish_caught")
        self.assertEqual(caught[0]["data"], {"fish_id": "F1", "kind": "ca_linh", "yield": 3})
        self.assertEqual([e["tick"] for e in caught], [1, 32])  # cạnh ở bước 29 còn hồi chiêu
        self.assertEqual(item_kinds(snapshots(rows)[-1]["hold"]), ["ca_linh"] * 3 + ["ca_loc"])

    def test_catch_hold_full_keeps_fish_without_cooldown(self):
        fish = [{"id": "F1", "kind": "ca_linh", "pos": [21, 5]}, {"id": "F2", "kind": "ca_loc", "pos": [22, 5]}]
        rows, _ = self.run_ok(river([20, 5], fish=fish, hold=individual_hold(*(["ca_loc"] * 10))),
                              [{"tick": 0, "catch": True}], 1)
        self.assertEqual(events(rows, "hold_full")[0]["data"],
                         {"action": "catch", "fish_id": "F1", "required": 3, "free": 2})
        last = snapshots(rows)[-1]
        self.assertEqual((len(last["fish"]), last["player"]["catch_cd_ticks"], last["hold_count"]), (2, 0, 10))

    def test_catch_ignored_at_surface(self):
        fish = [{"id": "F1", "kind": "ca_loc", "pos": [21, 0.6]}]
        rows, _ = self.run_ok(river([20, 0], fish=fish), [{"tick": 0, "catch": True}], 1)
        self.assertEqual(events(rows, "fish_caught"), [])

    def test_harvest_on_last_step_reaches_inventory(self):
        node = {"id": "N1", "kind": "bong_sung", "pos": [21, 0]}
        rows, inventory = self.run_ok(river([20, 0], nodes=[node], time_left_ticks=1),
                                      [{"tick": 0, "interact": True}], 5, inv_out=True)
        self.assertEqual(item_kinds(inventory["items"]), ["bong_sung"])
        if IS_V12:
            self.assertEqual(inventory["items"][0]["id"], "I1")
        self.assertEqual(rows[-1]["reason"], "time")


class QuanRules(unittest.TestCase):
    def run_ok(self, block, inputs, ticks):
        code, err, rows = play("quan", dict({"random_customers": False}, **block), inputs, ticks)
        self.assertEqual(code, 0, err)
        return rows

    @staticmethod
    def assigned(**extra):
        return dict({"id": "C1", "table_id": "T1", "dish_id": DISH, "order_status": "assigned",
                     "reserved": {}, "base_price": 60}, **extra)

    def test_full_order_flow_and_score(self):
        n = (7 ** 2 + 6 ** 2) ** 0.5
        rows = self.run_ok(
            {"player": {"pos": [2, 8]}, "stock": {"ca_loc": 1},
             "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH}]},
            [{"tick": 0, "interact": True}, {"tick": 1, "interact": False}, {"tick": 365, "interact": True},
             {"tick": 366, "interact": False, "move": [7 / n, -6 / n]}, {"tick": 510, "move": [0, 0]},
             {"tick": 520, "interact": True}], 1200)
        names = [e["name"] for e in events(rows)]
        self.assertEqual(names, ["cook_started", "dish_ready", "dish_picked", "served", "paid"])
        self.assertEqual((rows[-1]["money"], rows[-1]["score"]), (72, 372))
        self.assertAlmostEqual(rows[-1]["reputation"], 3.2, places=2)
        self.assertIn("vel", snapshots(rows)[0]["player"])

    def test_no_tip_below_patience_ratio(self):
        rows = self.run_ok({"player": {"pos": [9, 2]}, "hand": PAYLOAD,
                            "customers": [self.assigned(patience_ticks_left=1799)]},
                           [{"tick": 0, "interact": True}], 1)
        self.assertEqual(events(rows, "served")[0]["data"]["tip"], 0)

    def test_patience_leave_penalty(self):
        rows = self.run_ok({"stock": {"ca_loc": 1}, "customers": [
            {"id": "C1", "table_id": "T1", "dish_id": DISH, "patience_ticks_left": 1}]}, [], 1)
        self.assertEqual(events(rows, "customer_left")[0]["data"],
                         {"order_id": "C1", "table_id": "T1", "reason": "patience", "reputation": 2.5})

    def test_closing_waiting_customer_no_penalty(self):
        rows = self.run_ok({"time_left_ticks": 1, "stock": {"ca_loc": 1}, "customers": [
            {"id": "C1", "table_id": "T1", "dish_id": DISH}]}, [], 1)
        self.assertEqual(events(rows, "customer_left")[0]["data"]["reason"], "closing")
        self.assertEqual(rows[-1]["reputation"], 3.0)

    def test_paid_reason_at_closing(self):
        for eat_left, reason in ((1, "finished_eating"), (5, "closing")):
            with self.subTest(eat_left=eat_left):
                eating = self.assigned(state="eating", order_status="served", eat_ticks_left=eat_left, tip=12)
                rows = self.run_ok({"time_left_ticks": 1, "customers": [eating]}, [], 1)
                self.assertEqual(events(rows, "paid")[0]["data"]["reason"], reason)

    def test_score_floor_survives_repeated_tips(self):
        customers = [self.assigned(state="eating", order_status="served", eat_ticks_left=1, tip=12)]
        rep = 1.0
        for _ in range(5):
            rows = self.run_ok({"reputation": rep, "customers": customers}, [], 1)
            rep = rows[-1]["reputation"]
        self.assertEqual(rep, 2.0)
        self.assertEqual(rows[-1]["score"], 72 + 200)

    def test_customer_schedule_and_no_dish(self):
        code, err, rows = play("quan", {"stock": {"ca_loc": 1}}, [], 121)
        self.assertEqual(code, 0, err)
        self.assertEqual(events(rows, "customer_arrived")[0]["tick"], 120)
        code, err, rows = play("quan", {"stock": {}}, [], 121)
        self.assertEqual(events(rows, "no_dish")[0]["tick"], 120)

    def test_default_reservation_over_stock_exit_2(self):
        code, _, _ = play("quan", {"stock": {}, "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH}]}, [], 0)
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
