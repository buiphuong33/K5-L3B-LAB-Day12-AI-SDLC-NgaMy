"""Cá Sấu theo TICKET-02 mục 1.2 (viết lại vì API cũ chưa có waypoint, recoil 60 bước, mất nửa giỏ)."""

import unittest

from chonoi.contract import load_contract
from chonoi.sim.monsters import MonsterSet
from helpers import Workdir, events, read_jsonl, run_headless, snapshots, write_json

GATHER = load_contract()["tuning"]["gather"]


def croc(ident="M1", pos=(60, 24), **extra):
    return dict({"id": ident, "kind": "ca_sau", "pos": list(pos), "waypoints": [[60, 24], [64, 24]]}, **extra)


def play(block, ticks, frames=()):
    with Workdir() as w:
        scenario = write_json(w.path("s.json"), {"gather": dict({"random_fish": False, "nodes": []}, **block)})
        inputs = write_json(w.path("i.json"), {"frames": list(frames)})
        code, err = run_headless("--mode", "gather", "--seed", "3", "--scenario", scenario, "--inputs", inputs,
                                 "--ticks", str(ticks), "--snapshot-every", "1", "--out", w.path("o.jsonl"))
        if code:
            raise AssertionError(err)
        return read_jsonl(w.path("o.jsonl"))


class Monsters(unittest.TestCase):
    def test_default_layout_day_1(self):
        s = snapshots(play({}, 0))[0]
        self.assertEqual([m["id"] for m in s["monsters"]], ["M1"])

    def test_patrol_speed_and_switch_waypoint(self):
        rows = play({"player": {"pos": [20, 0]}, "monsters": [croc()]}, 241)
        last = snapshots(rows)[-1]["monsters"][0]
        self.assertEqual(last["target_idx"], 0)
        self.assertAlmostEqual(last["pos"][0], 64 - 1 / 60, delta=0.02)

    def test_chase_when_deep_not_when_shallow(self):
        rows = play({"player": {"pos": [55, 24]}, "monsters": [croc()]}, 1)
        self.assertEqual(snapshots(rows)[-1]["monsters"][0]["state"], "chase")
        rows = play({"player": {"pos": [58, 9]}, "monsters": [croc()]}, 1)
        self.assertEqual(snapshots(rows)[-1]["monsters"][0]["state"], "patrol")

    def test_hit_drops_half_lifo_sets_invuln_and_recoil(self):
        hold = ["ca_loc", "bong_sung", "ca_linh", "keo_neo", "ca_keo"]
        rows = play({"player": {"pos": [60, 24]}, "hold": hold, "monsters": [croc()]}, 1)
        data = events(rows, "monster_hit")[0]["data"]
        self.assertEqual((data["monster_id"], data["hp"], data["lost"]), ("M1", 2, ["ca_keo", "keo_neo"]))
        self.assertEqual(data["pos"], [60, 24])
        last = snapshots(rows)[-1]
        self.assertEqual(last["player"]["invuln_ticks"], 90)
        self.assertEqual((last["monsters"][0]["state"], last["monsters"][0]["state_ticks_left"]), ("recoil", 60))

    def test_one_hit_per_step_nearest_then_id(self):
        monsters = [croc("M10", (60, 24)), croc("M2", (60, 24))]
        rows = play({"player": {"pos": [60, 24]}, "monsters": monsters}, 1)
        self.assertEqual([e["data"]["monster_id"] for e in events(rows, "monster_hit")], ["M2"])

    def test_recoil_lasts_60_steps_then_patrol(self):
        m = croc(pos=(60, 24), state="recoil", state_ticks_left=60, recoil_dir=[1, 0])
        rows = play({"player": {"pos": [20, 0]}, "monsters": [m]}, 60)
        last = snapshots(rows)[-1]["monsters"][0]
        self.assertEqual(last["state"], "patrol")
        self.assertAlmostEqual(last["pos"][0], 62, delta=0.01)

    def test_lethal_hit_faints_with_remaining_hold(self):
        rows = play({"player": {"pos": [60, 24], "hp": 1}, "hold": ["ca_loc", "ca_linh", "ca_keo"],
                     "monsters": [croc()]}, 5)
        self.assertEqual(events(rows, "monster_hit")[0]["data"]["lost"], ["ca_keo"])
        self.assertEqual(events(rows, "faint")[0]["data"], {"cause": "monster", "lost": ["ca_linh", "ca_loc"], "hp": 0})
        self.assertEqual(rows[-1]["reason"], "fainted")

    def test_default_spawns_follow_from_day_and_id_order(self):
        make = lambda **k: MonsterSet(GATHER["monsters"], GATHER["bounds"], **k)
        self.assertEqual([m["id"] for m in make(day=1).snapshot()], ["M1"])
        self.assertEqual([m["id"] for m in make(day=3).snapshot()], ["M1", "M2"])
        custom = make(monsters=[croc("M10", (80, 20)), croc("M2", (70, 20))])
        self.assertEqual([m["id"] for m in custom.snapshot()], ["M2", "M10"])

    def test_chase_exits_beyond_exit_radius(self):
        m = croc(state="chase")
        rows = play({"player": {"pos": [40, 24]}, "monsters": [m]}, 1)
        self.assertEqual(snapshots(rows)[-1]["monsters"][0]["state"], "patrol")

    def test_invulnerability_blocks_hit(self):
        rows = play({"player": {"pos": [60, 24], "invuln_ticks": 5}, "monsters": [croc()]}, 1)
        self.assertEqual(events(rows, "monster_hit"), [])
        self.assertEqual(snapshots(rows)[-1]["player"]["hp"], 3)

    def test_stunned_stays_still_and_cannot_hit(self):
        m = croc(state="stunned", state_ticks_left=2)
        rows = play({"player": {"pos": [60, 24]}, "monsters": [m]}, 1)
        self.assertEqual(events(rows, "monster_hit"), [])
        self.assertEqual(snapshots(rows)[-1]["monsters"][0]["pos"], [60, 24])

    def test_bad_monster_scenario_exits_2(self):
        with Workdir() as w:
            scenario = write_json(w.path("bad.json"), {"gather": {"monsters": [
                {"id": "M1", "kind": "ca_sau", "pos": [60, 24]},
            ]}})
            code, _ = run_headless("--mode", "gather", "--seed", "1", "--ticks", "0",
                                   "--scenario", scenario, "--out", w.path("out.jsonl"))
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
