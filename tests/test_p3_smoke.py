"""Phase 3: smoke migration có thể chạy trước khi contract v1.2 được bật."""

import unittest

from chonoi.contract import load_contract
from chonoi.sim.monsters import MonsterSet


class Player:
    def __init__(self, pos, hold):
        self.pos = list(pos)
        self.hp = 3
        self.hold = list(hold)
        self.invuln_ticks = 0


class MigrationSmoke(unittest.TestCase):
    def test_monster_lost_preserves_item_objects_in_lifo_order(self):
        """Quái pop trực tiếp cá thể mới; không đổi về chuỗi kind hay làm mất fresh."""
        tuning = load_contract()["tuning"]
        gather = tuning["gather"]
        spawn = {
            "id": "M1", "kind": "ca_sau", "pos": [60, 24],
            "waypoints": [[60, 24], [64, 24]],
        }
        monsters = MonsterSet(gather["monsters"], gather["bounds"], monsters=[spawn])
        hold = [
            {"id": "I1", "kind": "ca_loc", "fresh": 12000},
            {"id": "I2", "kind": "bong_sung", "fresh": 11000},
            {"id": "I3", "kind": "ca_linh", "fresh": 10000},
        ]
        player = Player([60, 24], hold)
        events = []

        monsters.step(player, events)

        hit = next(data for name, data in events if name == "monster_hit")
        self.assertEqual(hit["lost"], [hold[2]])
        self.assertEqual(player.hold, hold[:2])
        self.assertIsInstance(hit["lost"][0], dict)
        self.assertEqual(hit["lost"][0]["fresh"], 10000)


if __name__ == "__main__":
    unittest.main()
