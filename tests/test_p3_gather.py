"""Phase 3 — độ tươi buổi sáng (gather) theo TICKET-03 mục 1. Chủ lát: Tâm.

Hai lớp test:
  - `GatherFreshUnit`: gọi thẳng `Session` với tuning của contract + `contract_version` "1.2" +
    khối `freshness` theo ticket, chạy được cả khi contract trên `main` còn 1.1 (gather bật kho cá thể
    theo `tuning["contract_version"]`, ADR 0001 mục 5).
  - `GatherFreshHeadless`: hộp đen qua `headless_cmd` với fixture của ticket; tự bỏ qua tới khi
    `game.contract.json` có `contract_version` "1.2".
"""

import copy
import json
import os
import unittest

from helpers import ROOT, Workdir, events, read_jsonl, run_headless, snapshots, write_json

from chonoi.inputs import InputPlayer
from chonoi.runner import Session

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    CONTRACT = json.load(f)

# Khối freshness theo TICKET-03 (dùng khi contract chưa có; có rồi thì dùng của contract).
TICKET_FRESHNESS = {"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30}
TUNING = copy.deepcopy(CONTRACT["tuning"])
TUNING.setdefault("freshness", TICKET_FRESHNESS)
TUNING["contract_version"] = "1.2"  # gather đọc version từ tuning để bật kho cá thể
FRESH = TUNING["freshness"]
TICK_HZ = TUNING.get("tick_hz", 60)
STEP = FRESH["gather_decay_per_s"] / TICK_HZ  # điểm tươi mất mỗi tick ở giỏ
QUIET = {"random_fish": False, "monsters": []}
IS_V12 = CONTRACT.get("contract_version") == "1.2"


def item(ident, kind, fresh):
    return {"id": ident, "kind": kind, "fresh": fresh}


def run(scenario, ticks, frames=(), seed=1):
    """Chạy gather tới `ticks` bước hoặc tới khi kết thúc; trả (sim, [(tick, name, data)])."""
    sess = Session("gather", TUNING, scenario, seed)
    player = InputPlayer(list(frames))
    out = []
    while sess.tick < ticks and not sess.done:
        out += [(e["tick"], e["name"], e["data"]) for e in sess.step(player.advance(sess.tick))]
    return sess.sim, out


def named(evs, name):
    return [(t, d) for t, n, d in evs if n == name]


class GatherFreshUnit(unittest.TestCase):
    def test_ticket_threshold_fixture_spoils_on_first_step(self):
        sim, evs = run({**QUIET, "hold": [item("I1", "ca_linh", 30)]}, 1)
        self.assertEqual(evs, [(1, "spoiled", {"item_id": "I1", "kind": "ca_linh", "location": "hold"})])
        self.assertAlmostEqual(sim.hold[0]["fresh"], 30 - STEP, delta=1e-9)

    def test_spoiled_once_and_item_keeps_its_slot(self):
        sim, evs = run({**QUIET, "hold": [item("I1", "ca_linh", 30)]}, 300)
        self.assertEqual(len(named(evs, "spoiled")), 1)
        self.assertEqual([e["id"] for e in sim.hold], ["I1"])

    def test_not_spoiled_while_at_or_above_threshold(self):
        # 30.5 biểu diễn chính xác: sau đúng 0.5 / STEP bước (60 tick) còn đúng 30.0 -> chưa ươn;
        # bước kế mới ươn. (Dùng số không biểu diễn chính xác như 30 + 0.5/60 sẽ lệch ngưỡng.)
        n = round(0.5 / STEP)
        sim, evs = run({**QUIET, "hold": [item("I1", "ca_loc", 30.5)]}, n)
        self.assertEqual(evs, [])
        self.assertEqual(sim.hold[0]["fresh"], 30)
        _, evs = run({**QUIET, "hold": [item("I1", "ca_loc", 30.5)]}, n + 1)
        self.assertEqual(named(evs, "spoiled"), [(n + 1, {"item_id": "I1", "kind": "ca_loc", "location": "hold"})])

    def test_many_spoil_same_tick_in_id_order(self):
        hold = [item("I10", "ca_loc", 30), item("I2", "ca_linh", 30)]
        _, evs = run({**QUIET, "hold": hold}, 1)
        self.assertEqual([d["item_id"] for _, d in named(evs, "spoiled")], ["I2", "I10"])

    def test_clamped_at_zero(self):
        sim, _ = run({**QUIET, "hold": [item("I1", "ca_loc", STEP / 2)]}, 3)
        self.assertEqual(sim.hold[0]["fresh"], 0.0)

    def test_harvest_new_id_full_fresh_decays_from_next_step(self):
        nodes = [{"id": "N1", "kind": "bong_sung", "pos": [20, 0]}]
        scn = {**QUIET, "player": {"pos": [20, 0]}, "nodes": nodes,
               "hold": [item("I1", "ca_loc", 80), item("I2", "ca_loc", 80)]}
        press = [{"tick": 0, "interact": True}]
        sim, _ = run(scn, 1, press)
        self.assertEqual(sim.hold[-1], item("I3", "bong_sung", float(FRESH["initial"])))
        self.assertAlmostEqual(sim.hold[0]["fresh"], 80 - STEP, delta=1e-9)
        sim, _ = run(scn, 2, press)
        self.assertAlmostEqual(sim.hold[-1]["fresh"], FRESH["initial"] - STEP, delta=1e-9)

    def test_catch_gives_consecutive_ids_per_individual(self):
        fish = [{"id": "F1", "kind": "ca_linh", "pos": [20, 6.5]}]
        sim, _ = run({**QUIET, "player": {"pos": [20, 6]}, "fish": fish}, 1, [{"tick": 0, "catch": True}])
        n = TUNING["gather"]["fish_yield"]["ca_linh"]
        self.assertEqual([e["id"] for e in sim.hold], [f"I{i}" for i in range(1, n + 1)])
        self.assertTrue(all(e["fresh"] == FRESH["initial"] for e in sim.hold))

    def test_faint_loses_all_individuals_lifo_and_empty_inventory(self):
        hold = [item("I1", "ca_loc", 90), item("I2", "bong_sung", 50)]
        player = {"pos": [20, 10], "oxygen_ticks": 0, "hp": 1, "zero_oxy_ticks": 59}
        _, evs = run({**QUIET, "player": player, "hold": hold}, 1)
        (_, faint), = named(evs, "faint")
        self.assertEqual([e["id"] for e in faint["lost"]], ["I2", "I1"])
        self.assertEqual(set(faint["lost"][0]), {"id", "kind", "fresh"})
        self.assertEqual(evs[-1][1:], ("gather_end", {"reason": "fainted", "inventory": {"items": []}}))

    def test_monster_hit_loses_individuals_lifo(self):
        monsters = [{"id": "M1", "kind": "ca_sau", "pos": [20.5, 10], "waypoints": [[20.5, 10], [24, 10]]}]
        hold = [item("I1", "ca_loc", 90), item("I2", "bong_sung", 50)]
        _, evs = run({"random_fish": False, "monsters": monsters, "player": {"pos": [20, 10]}, "hold": hold}, 1)
        (_, hit), = named(evs, "monster_hit")
        self.assertEqual([e["id"] for e in hit["lost"]], ["I2"])

    def test_docked_inventory_is_individual_array_by_id_after_decay(self):
        hold = [item("I9", "ca_loc", 50), item("I3", "ca_linh", 70)]
        _, evs = run({**QUIET, "player": {"pos": [3, 0]}, "hold": hold}, 1, [{"tick": 0, "interact": True}])
        (_, end), = named(evs, "gather_end")
        self.assertEqual(end["reason"], "docked")
        items = end["inventory"]["items"]
        self.assertEqual([e["id"] for e in items], ["I3", "I9"])
        self.assertAlmostEqual(items[0]["fresh"], 70 - STEP, delta=1e-9)

    def test_same_seed_same_snapshot(self):
        a = json.dumps(run({}, 2000, seed=4)[0].snapshot())
        b = json.dumps(run({}, 2000, seed=4)[0].snapshot())
        self.assertEqual(a, b)


@unittest.skipUnless(IS_V12, "chờ game.contract.json bật contract_version 1.2")
class GatherFreshHeadless(unittest.TestCase):
    FIXTURE = {"gather": {"hold": [item("I1", "ca_linh", 30)], "random_fish": False, "monsters": []}}

    def test_ticket_threshold_event_line(self):
        with Workdir() as w:
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1",
                                     "--scenario", write_json(w.path("s.json"), self.FIXTURE),
                                     "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            spoiled = [e for e in events(read_jsonl(w.path("o.jsonl"))) if e["name"] == "spoiled"]
        self.assertEqual(spoiled, [{"type": "event", "tick": 1, "phase": "gather", "name": "spoiled",
                                    "data": {"item_id": "I1", "kind": "ca_linh", "location": "hold"}}])

    def test_smoke_inventory_file_into_quan(self):
        fixture = {"gather": {"hold": [item("I1", "ca_linh", 100)], "random_fish": False, "monsters": []}}
        with Workdir() as w:
            inputs = write_json(w.path("i.json"), {"frames": [{"tick": 0, "interact": True}]})
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "10",
                                     "--scenario", write_json(w.path("s.json"), fixture), "--inputs", inputs,
                                     "--out", w.path("g.jsonl"), "--inventory-out", w.path("kho.json"))
            self.assertEqual(code, 0, err)
            with open(w.path("kho.json"), encoding="utf-8") as f:
                kho = json.load(f)
            self.assertEqual(kho["items"][0]["id"], "I1")
            self.assertAlmostEqual(kho["items"][0]["fresh"], 100 - STEP, delta=0.01)
            code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0",
                                     "--inventory", w.path("kho.json"), "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            stock = snapshots(read_jsonl(w.path("q.jsonl")))[0]["stock"]
        self.assertEqual([(e["id"], e["kind"]) for e in stock], [("I1", "ca_linh")])
        self.assertAlmostEqual(stock[0]["fresh"], kho["items"][0]["fresh"], delta=0.01)


if __name__ == "__main__":
    unittest.main()
