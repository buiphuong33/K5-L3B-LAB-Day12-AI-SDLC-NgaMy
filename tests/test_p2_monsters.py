"""Cá Sấu theo TICKET-02 mục 1.2 (viết lại vì API cũ chưa có waypoint, recoil 60 bước, mất nửa giỏ)."""

import unittest

from helpers import Workdir, events, read_jsonl, run_headless, snapshots, write_json


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


if __name__ == "__main__":
    unittest.main()
