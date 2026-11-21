"""Unit test lát cá sấu Phase 2 bằng fixture riêng, không hard-code vào luật."""

import unittest

from chonoi.sim.monsters import MonsterSet


SETTINGS = {
    "tick_hz": 10,
    "patrol_speed": 10,
    "chase_speed": 20,
    "chase_radius": 5,
    "hit_radius": 0.25,
    "recoil_distance": 2,
    "hit_damage": 1,
    "drop_count": 2,
    "invuln_ticks": 90,
}
BOUNDS = {"x": [0, 20], "d": [0, 10]}


def monster(ident, pos, heading=0, patrol=(1, 19)):
    return {"id": ident, "pos": pos, "heading_deg": heading, "patrol_x": list(patrol)}


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
    def test_snapshot_uses_numeric_id_order_and_patrol_reflects(self):
        monsters = MonsterSet(
            [monster("M10", [18.5, 8]), monster("M2", [1.5, 8], heading=180)],
            SETTINGS, BOUNDS,
        )
        monsters.step(Player([10, 0]), [])
        snapshot = monsters.snapshot()
        self.assertEqual([item["id"] for item in snapshot], ["M2", "M10"])
        self.assertEqual([item["pos"][0] for item in snapshot], [1.5, 18.5])
        self.assertEqual([item["heading_deg"] for item in snapshot], [0.0, 180.0])

    def test_chase_moves_toward_player(self):
        monsters = MonsterSet([monster("M1", [5, 5])], SETTINGS, BOUNDS)
        player = Player([8, 5])
        monsters.step(player, [])
        state = monsters.snapshot()[0]
        self.assertEqual(state["state"], "chase")
        self.assertEqual(state["pos"], [7.0, 5.0])
        self.assertEqual(state["heading_deg"], 0.0)

    def test_only_lowest_id_hits_drops_lifo_and_sets_invulnerability(self):
        settings = dict(SETTINGS, chase_speed=0, hit_radius=1)
        monsters = MonsterSet(
            [monster("M10", [5, 5]), monster("M2", [5, 5])], settings, BOUNDS,
        )
        player = Player([5, 5], hold=["first", "second", "third"])
        events = []
        self.assertEqual(monsters.step(player, events), "M2")
        self.assertEqual(player.hp, 2)
        self.assertEqual(player.hold, ["first"])
        self.assertEqual(player.invuln_ticks, 90)
        self.assertEqual(events, [("monster_hit", {
            "monster_id": "M2", "hp": 2, "lost": ["third", "second"],
        })])
        self.assertEqual(monsters.snapshot()[0]["state"], "recoil")

    def test_invulnerability_blocks_hit(self):
        monsters = MonsterSet([monster("M1", [5, 5])], dict(SETTINGS, chase_speed=0), BOUNDS)
        player = Player([5, 5], invuln=1)
        events = []
        self.assertIsNone(monsters.step(player, events))
        self.assertEqual((player.hp, events), (3, []))

    def test_lethal_hit_faints_and_clears_remaining_hold(self):
        settings = dict(SETTINGS, chase_speed=0, drop_count=1)
        monsters = MonsterSet([monster("M1", [5, 5])], settings, BOUNDS)
        player = Player([5, 5], hp=1, hold=["a", "b", "c"])
        events = []
        monsters.step(player, events)
        self.assertEqual(events[:2], [
            ("monster_hit", {"monster_id": "M1", "hp": 0, "lost": ["c"]}),
            ("faint", {"cause": "monster", "monster_id": "M1", "lost": ["b", "a"], "hp": 0}),
        ])
        self.assertEqual(events[2][0], "gather_end")
        self.assertEqual((player.hold, player.done, player.reason), ([], True, "fainted"))

    def test_missing_tuning_is_rejected(self):
        with self.assertRaises(ValueError):
            MonsterSet([monster("M1", [5, 5])], {"tick_hz": 60}, BOUNDS)


if __name__ == "__main__":
    unittest.main()
