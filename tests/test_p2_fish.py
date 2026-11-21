"""Cá bơi và sinh cá theo TICKET-02 mục 1.1."""

import json
import math
import os
import unittest

from helpers import ROOT, Workdir, events, read_jsonl, run_headless, snapshots, write_json

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    G = json.load(f)["tuning"]["gather"]


def play(block, ticks, seed="5"):
    with Workdir() as w:
        args = ["--mode", "gather", "--seed", seed, "--ticks", str(ticks), "--snapshot-every", "1",
                "--out", w.path("o.jsonl")]
        if block is not None:
            args += ["--scenario", write_json(w.path("s.json"), {"gather": block})]
        code, err = run_headless(*args)
        if code:
            raise AssertionError(err)
        return read_jsonl(w.path("o.jsonl"))


class Fish(unittest.TestCase):
    def test_initial_eight_at_distinct_spawn_points(self):
        fish = snapshots(play(None, 0))[0]["fish"]
        self.assertEqual(len(fish), 8)
        self.assertEqual(len({tuple(f["pos"]) for f in fish}), 8)
        for f in fish:
            self.assertIn(f["pos"][0], G["fish_spawn_x"])
            self.assertIn(f["pos"][1], G["fish_spawn_depths"][f["kind"]])

    def test_swims_at_speed_and_stays_in_species_band(self):
        snaps = snapshots(play({"nodes": [], "monsters": []}, 700))
        first, second = snaps[0]["fish"][0], snaps[1]["fish"][0]
        self.assertAlmostEqual(math.dist(first["pos"], second["pos"]), G["fish_speed"] / 60, delta=0.002)
        for s in snaps:
            for f in s["fish"]:
                lo, hi = G["fish_depths"][f["kind"]]
                self.assertTrue(G["fish_x"][0] <= f["pos"][0] <= G["fish_x"][1] and lo <= f["pos"][1] <= hi)

    def test_reflects_remaining_distance_at_edge(self):
        fish = [{"id": "F1", "kind": "ca_linh", "pos": [95.99, 5], "heading_deg": 0}]
        s = snapshots(play({"fish": fish, "nodes": [], "monsters": []}, 1))[-1]["fish"][0]
        self.assertAlmostEqual(s["pos"][0], 96 - (1.5 / 60 - 0.01), delta=0.001)
        self.assertAlmostEqual(s["heading_deg"], 180, delta=0.001)

    def test_spawn_schedule_and_cap(self):
        rows = play({"nodes": [], "monsters": []}, 2200)
        spawned = events(rows, "fish_spawned")
        self.assertEqual([e["tick"] for e in spawned], [360, 720, 1080, 1440])
        self.assertEqual(set(spawned[0]["data"]), {"id", "kind", "pos"})
        self.assertEqual(len(snapshots(rows)[-1]["fish"]), 12)

    def test_random_fish_false_keeps_fixture_still(self):
        fish = [{"id": "F1", "kind": "ca_loc", "pos": [20, 10]}]
        rows = play({"random_fish": False, "fish": fish, "nodes": [], "monsters": []}, 400)
        self.assertEqual(snapshots(rows)[-1]["fish"][0]["pos"], [20, 10])
        self.assertEqual(events(rows, "fish_spawned"), [])


if __name__ == "__main__":
    unittest.main()
