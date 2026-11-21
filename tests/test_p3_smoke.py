"""Phase 3: smoke migration có thể chạy trước khi contract v1.2 được bật."""

import unittest
from fractions import Fraction

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inventory import KINDS, read_inventory, write_inventory
from chonoi.items import Freshness, decay, new_item
from chonoi.sim.monsters import MonsterSet
from helpers import Workdir, write_json


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
            {"id": "I1", "kind": "ca_loc", "fresh": 100},
            {"id": "I2", "kind": "bong_sung", "fresh": 80},
            {"id": "I3", "kind": "ca_linh", "fresh": 60},
        ]
        player = Player([60, 24], hold)
        events = []

        monsters.step(player, events)

        hit = next(data for name, data in events if name == "monster_hit")
        self.assertEqual(hit["lost"], [hold[2]])
        self.assertEqual(player.hold, hold[:2])
        self.assertIsInstance(hit["lost"][0], dict)
        self.assertEqual(hit["lost"][0]["fresh"], 60)

    def test_threshold_30_spoils_only_after_crossing(self):
        fr = Freshness(load_contract()["tuning"])
        hold = [{"id": "I1", "kind": "ca_linh", "fresh": Fraction(30)}]

        spoiled = decay(hold, fr.gather_per_tick, fr)

        self.assertEqual([item["id"] for item in spoiled], ["I1"])
        self.assertLess(hold[0]["fresh"], 30)
        self.assertEqual(decay(hold, fr.gather_per_tick, fr), [])

    def test_v12_inventory_file_roundtrip_and_rejects_count_schema(self):
        fr = Freshness(load_contract()["tuning"])
        item = new_item(IdAllocator(), "ca_loc", fr=fr)
        with Workdir() as w:
            path = w.path("inventory.json")
            write_inventory(path, [item])
            loaded = read_inventory(path, KINDS, version="1.2")
            self.assertEqual(loaded, [item])

            legacy = write_json(w.path("legacy.json"), {"items": {"ca_loc": 1}})
            with self.assertRaises(BadInput):
                read_inventory(legacy, KINDS, version="1.2")


if __name__ == "__main__":
    unittest.main()
