"""Phase 2: cá sấu theo tuning v1.1 và fixture scenario chuẩn."""

import unittest

from chonoi.contract import load_contract
from chonoi.sim.monsters import MonsterSet
from helpers import Workdir, run_headless, write_json


TUNING = load_contract()["tuning"]
GATHER = TUNING["gather"]
CONFIG = GATHER["monsters"]
TICK_HZ = TUNING["tick_hz"]


def monster(ident, pos, waypoints=None, **extra):
    return dict({
        "id": ident, "kind": "ca_sau", "pos": list(pos),
        "waypoints": waypoints or [list(pos), [pos[0] + 4, pos[1]]],
    }, **extra)


class Player:
    def __init__(self, pos, hp=3, hold=None, invuln=0):
        self.pos = list(pos)
        self.hp = hp
        self.hold = list(hold or [])
        self.invuln_ticks = invuln
        self.done = False
        self.reason = None

    def _finish(self, reason, events):
        self.done = True
        self.reason = reason
        events.append(("gather_end", {"reason": reason, "inventory": {"items": {}}}))


class MonsterRules(unittest.TestCase):
    def make(self, monsters=None, day=1):
        return MonsterSet(CONFIG, GATHER["bounds"], TICK_HZ, current_day=day, monsters=monsters)

    def test_default_spawns_follow_from_day_and_snapshot_id_order(self):
        self.assertEqual([m["id"] for m in self.make(day=1).snapshot()], ["M1"])
        self.assertEqual([m["id"] for m in self.make(day=3).snapshot()], ["M1", "M2"])
        custom = self.make([monster("M10", [80, 20]), monster("M2", [70, 20])])
        self.assertEqual([m["id"] for m in custom.snapshot()], ["M2", "M10"])

    def test_patrol_moves_between_waypoints(self):
        monsters = self.make([monster("M1", [60, 24], [[60, 24], [64, 24]])])
        monsters.step(Player([0, 0]), [])
        state = monsters.snapshot()[0]
        self.assertEqual(state["state"], "patrol")
        self.assertAlmostEqual(state["pos"][0], 60 + 1 / TICK_HZ)
        self.assertEqual(state["target_idx"], 1)

    def test_chase_uses_detect_and_exit_hysteresis(self):
        monsters = self.make([monster("M1", [60, 24])])
        player = Player([69, 24])
        monsters.step(player, [])
        self.assertEqual(monsters.snapshot()[0]["state"], "chase")
        player.pos = [90, 24]
        monsters.step(player, [])
        self.assertEqual(monsters.snapshot()[0]["state"], "patrol")

    def test_only_lowest_id_hits_and_loss_ratio_is_lifo(self):
        monsters = self.make([monster("M10", [70, 20]), monster("M2", [70, 20])])
        player = Player([70, 20], hold=["a", "b", "c"])
        events = []
        self.assertEqual(monsters.step(player, events), "M2")
        self.assertEqual(player.hp, 2)
        self.assertEqual(player.hold, ["a"])
        self.assertEqual(player.invuln_ticks, CONFIG["invuln_ticks"])
        self.assertEqual(events, [("monster_hit", {
            "monster_id": "M2", "hp": 2, "lost": ["c", "b"],
        })])

    def test_recoil_runs_for_contract_ticks_and_distance(self):
        start = [70, 20]
        monsters = self.make([monster("M1", start)])
        player = Player(start, invuln=0)
        monsters.step(player, [])
        player.invuln_ticks = CONFIG["invuln_ticks"]
        species = CONFIG["species"]["ca_sau"]
        for _ in range(species["recoil_ticks"]):
            monsters.step(player, [])
        state = monsters.snapshot()[0]
        self.assertEqual(state["state"], "patrol")
        self.assertEqual(state["state_ticks_left"], 0)
        self.assertAlmostEqual(math_dist(state["pos"], start), species["recoil_dist"], places=6)

    def test_invulnerability_blocks_hit(self):
        monsters = self.make([monster("M1", [70, 20])])
        player = Player([70, 20], invuln=1)
        events = []
        self.assertIsNone(monsters.step(player, events))
        self.assertEqual((player.hp, events), (3, []))

    def test_lethal_hit_faints_and_clears_remaining_hold(self):
        monsters = self.make([monster("M1", [70, 20])])
        player = Player([70, 20], hp=1, hold=["a", "b", "c", "d"])
        events = []
        monsters.step(player, events)
        self.assertEqual(events[:2], [
            ("monster_hit", {"monster_id": "M1", "hp": 0, "lost": ["d", "c"]}),
            ("faint", {"cause": "monster", "monster_id": "M1", "lost": ["b", "a"], "hp": 0}),
        ])
        self.assertEqual(events[2][0], "gather_end")
        self.assertEqual((player.hold, player.done, player.reason), ([], True, "fainted"))

    def test_bad_monster_scenario_exits_2(self):
        with Workdir() as w:
            scenario = write_json(w.path("bad.json"), {"gather": {"monsters": [
                {"id": "M1", "kind": "ca_sau", "pos": [60, 24]},
            ]}})
            code, _ = run_headless("--mode", "gather", "--seed", "1", "--ticks", "0",
                                   "--scenario", scenario, "--out", w.path("out.jsonl"))
            self.assertEqual(code, 2)


def math_dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


if __name__ == "__main__":
    unittest.main()
