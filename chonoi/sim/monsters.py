"""Cá sấu Phase 2: patrol, chase, recoil và va chạm với người chơi.

Module nhận cấu hình đã chuẩn hóa thay vì đọc trực tiếp ``game.contract.json``. Bên tích
hợp ánh xạ tuning v1.1 vào ``settings`` và danh sách ``monsters``; nhờ vậy luật không
hard-code số gameplay và không phụ thuộc cách contract nhóm các khóa.
"""

import math

from ..ids import sort_by_id


class MonsterSet:
    """Quản lý M1/M2 và xét tối đa một va chạm mỗi tick theo thứ tự id."""

    REQUIRED_SETTINGS = {
        "tick_hz", "patrol_speed", "chase_speed", "chase_radius", "hit_radius",
        "recoil_distance", "hit_damage", "drop_count", "invuln_ticks",
    }

    def __init__(self, monsters, settings, bounds):
        missing = self.REQUIRED_SETTINGS - set(settings)
        if missing:
            raise ValueError(f"thiếu tuning monsters: {sorted(missing)}")
        self.settings = dict(settings)
        self.bounds = bounds
        self.monsters = []
        for source in monsters:
            if "patrol_x" not in source:
                raise ValueError(f"monster {source.get('id', '?')} thiếu patrol_x")
            monster = {
                "id": source["id"],
                "kind": source.get("kind", "ca_sau"),
                "pos": [float(c) for c in source["pos"]],
                "heading_deg": float(source.get("heading_deg", 0)),
                "patrol_x": [float(c) for c in source["patrol_x"]],
                "state": source.get("state", "patrol"),
            }
            self.monsters.append(monster)
        self.monsters = sort_by_id(self.monsters)

    def snapshot(self):
        return [
            {key: monster[key] for key in ("id", "kind", "pos", "heading_deg", "state")}
            for monster in sort_by_id(self.monsters)
        ]

    def step(self, player, events):
        """Cập nhật chuyển động rồi xét hit; trả id quái đánh trúng hoặc ``None``."""
        for monster in sort_by_id(self.monsters):
            self._move(monster, player.pos)

        if player.invuln_ticks > 0:
            return None
        for monster in sort_by_id(self.monsters):
            if math.dist(monster["pos"], player.pos) <= self.settings["hit_radius"]:
                self._hit(monster, player, events)
                return monster["id"]
        return None

    def _move(self, monster, player_pos):
        distance = math.dist(monster["pos"], player_pos)
        if distance <= self.settings["chase_radius"]:
            monster["state"] = "chase"
            self._move_toward(monster, player_pos, self.settings["chase_speed"])
        else:
            monster["state"] = "patrol"
            self._patrol(monster)
        self._clamp(monster["pos"])

    def _move_toward(self, monster, target, speed):
        dx = target[0] - monster["pos"][0]
        dd = target[1] - monster["pos"][1]
        distance = math.hypot(dx, dd)
        if distance == 0:
            return
        step = min(float(speed) / float(self.settings["tick_hz"]), distance)
        monster["pos"][0] += dx / distance * step
        monster["pos"][1] += dd / distance * step
        monster["heading_deg"] = math.degrees(math.atan2(dd, dx)) % 360

    def _patrol(self, monster):
        lo, hi = monster["patrol_x"]
        direction = 1 if math.cos(math.radians(monster["heading_deg"])) >= 0 else -1
        x = monster["pos"][0] + direction * (
            float(self.settings["patrol_speed"]) / float(self.settings["tick_hz"])
        )
        while x < lo or x > hi:
            if x > hi:
                x = hi - (x - hi)
                direction = -1
            elif x < lo:
                x = lo + (lo - x)
                direction = 1
        monster["pos"][0] = x
        monster["heading_deg"] = 0.0 if direction > 0 else 180.0

    def _hit(self, monster, player, events):
        player.hp = max(0, player.hp - int(self.settings["hit_damage"]))
        lost = []
        for _ in range(min(int(self.settings["drop_count"]), len(player.hold))):
            lost.append(player.hold.pop())
        player.invuln_ticks = int(self.settings["invuln_ticks"])
        events.append(("monster_hit", {
            "monster_id": monster["id"], "hp": player.hp, "lost": lost,
        }))
        self._recoil(monster, player.pos)

        if player.hp > 0:
            return
        faint_lost = list(reversed(player.hold))
        player.hold.clear()
        events.append(("faint", {
            "cause": "monster", "monster_id": monster["id"], "lost": faint_lost, "hp": 0,
        }))
        if hasattr(player, "_finish"):
            player._finish("fainted", events)

    def _recoil(self, monster, player_pos):
        dx = monster["pos"][0] - player_pos[0]
        dd = monster["pos"][1] - player_pos[1]
        distance = math.hypot(dx, dd)
        if distance == 0:
            angle = math.radians(monster["heading_deg"] + 180)
            dx, dd, distance = math.cos(angle), math.sin(angle), 1.0
        amount = float(self.settings["recoil_distance"])
        monster["pos"][0] += dx / distance * amount
        monster["pos"][1] += dd / distance * amount
        monster["heading_deg"] = math.degrees(math.atan2(dd, dx)) % 360
        monster["state"] = "recoil"
        self._clamp(monster["pos"])

    def _clamp(self, pos):
        pos[0] = min(max(pos[0], self.bounds["x"][0]), self.bounds["x"][1])
        pos[1] = min(max(pos[1], self.bounds["d"][0]), self.bounds["d"][1])
