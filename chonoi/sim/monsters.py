"""Cá sấu Phase 2: tuần tra, truy đuổi, recoil và va chạm."""

import math

from ..ids import sort_by_id


class MonsterSet:
    """Quản lý quái của một buổi gather và xét tối đa một hit mỗi tick."""

    def __init__(self, config, bounds, tick_hz, current_day=1, monsters=None):
        self.config = config
        self.species = config["species"]
        self.bounds = bounds
        self.tick_hz = float(tick_hz)
        sources = monsters if monsters is not None else [
            item for item in config["spawns"] if item.get("from_day", 1) <= current_day
        ]
        self.monsters = [self._build(item) for item in sources]
        self.monsters = sort_by_id(self.monsters)

    @staticmethod
    def _build(source):
        state = source.get("state", "patrol")
        return {
            "id": source["id"],
            "kind": source["kind"],
            "pos": [float(c) for c in source["pos"]],
            "waypoints": [[float(c) for c in point] for point in source["waypoints"]],
            "target_idx": int(source.get("target_idx", 1)),
            "state": state,
            "state_ticks_left": int(source.get("state_ticks_left", 0)),
            "recoil_dir": (list(source["recoil_dir"])
                           if source.get("recoil_dir") is not None else None),
        }

    def snapshot(self):
        result = []
        for monster in sort_by_id(self.monsters):
            row = {
                "id": monster["id"], "kind": monster["kind"],
                "pos": list(monster["pos"]),
                "waypoints": [list(point) for point in monster["waypoints"]],
                "target_idx": monster["target_idx"], "state": monster["state"],
                "state_ticks_left": monster["state_ticks_left"],
            }
            if monster["recoil_dir"] is not None:
                row["recoil_dir"] = list(monster["recoil_dir"])
            result.append(row)
        return result

    def step(self, player, events):
        """Cập nhật quái theo id rồi xét hit; trả id quái đánh trúng hoặc ``None``."""
        for monster in sort_by_id(self.monsters):
            self._move(monster, player.pos)

        if player.invuln_ticks > 0:
            return None
        for monster in sort_by_id(self.monsters):
            setting = self.species[monster["kind"]]
            if math.dist(monster["pos"], player.pos) <= setting["hit_radius"]:
                self._hit(monster, player, events)
                return monster["id"]
        return None

    def _move(self, monster, player_pos):
        setting = self.species[monster["kind"]]
        if monster["state"] in {"recoil", "stunned"}:
            self._timed_state(monster, setting)
            return

        distance = math.dist(monster["pos"], player_pos)
        if monster["state"] == "chase":
            if distance > setting["exit_radius"]:
                monster["state"] = "patrol"
            else:
                self._move_toward(monster["pos"], player_pos, setting["chase_speed"])
                return
        if monster["state"] == "patrol" and distance <= setting["detect_radius"]:
            monster["state"] = "chase"
            self._move_toward(monster["pos"], player_pos, setting["chase_speed"])
            return
        self._patrol(monster, setting["patrol_speed"])

    def _patrol(self, monster, speed):
        target = monster["waypoints"][monster["target_idx"]]
        reached = self._move_toward(monster["pos"], target, speed)
        if reached:
            monster["target_idx"] = 1 - monster["target_idx"]

    def _timed_state(self, monster, setting):
        if monster["state"] == "recoil":
            per_tick = float(setting["recoil_dist"]) / int(setting["recoil_ticks"])
            direction = monster["recoil_dir"]
            monster["pos"][0] += direction[0] * per_tick
            monster["pos"][1] += direction[1] * per_tick
            self._clamp(monster["pos"])
        monster["state_ticks_left"] = max(0, monster["state_ticks_left"] - 1)
        if monster["state_ticks_left"] == 0:
            monster["state"] = "patrol"
            monster["recoil_dir"] = None

    def _move_toward(self, pos, target, speed):
        dx, dd = target[0] - pos[0], target[1] - pos[1]
        distance = math.hypot(dx, dd)
        if distance == 0:
            return True
        step = min(float(speed) / self.tick_hz, distance)
        pos[0] += dx / distance * step
        pos[1] += dd / distance * step
        self._clamp(pos)
        return step == distance

    def _hit(self, monster, player, events):
        setting = self.species[monster["kind"]]
        player.hp = max(0, player.hp - 1)
        drop_count = math.ceil(len(player.hold) * float(self.config["loss_ratio"]))
        lost = [player.hold.pop() for _ in range(drop_count)]
        player.invuln_ticks = int(self.config["invuln_ticks"])
        events.append(("monster_hit", {
            "monster_id": monster["id"], "hp": player.hp, "lost": lost,
        }))
        self._start_recoil(monster, player.pos, setting)

        if player.hp > 0:
            return
        faint_lost = list(reversed(player.hold))
        player.hold.clear()
        events.append(("faint", {
            "cause": "monster", "monster_id": monster["id"], "lost": faint_lost, "hp": 0,
        }))
        if hasattr(player, "_finish"):
            player._finish("fainted", events)

    def _start_recoil(self, monster, player_pos, setting):
        dx = monster["pos"][0] - player_pos[0]
        dd = monster["pos"][1] - player_pos[1]
        distance = math.hypot(dx, dd)
        if distance == 0:
            target = monster["waypoints"][1 - monster["target_idx"]]
            dx = target[0] - monster["pos"][0]
            dd = target[1] - monster["pos"][1]
            distance = math.hypot(dx, dd)
        if distance == 0:
            dx, dd, distance = -1.0, 0.0, 1.0
        monster["state"] = "recoil"
        monster["state_ticks_left"] = int(setting["recoil_ticks"])
        monster["recoil_dir"] = [dx / distance, dd / distance]

    def _clamp(self, pos):
        pos[0] = min(max(pos[0], self.bounds["x"][0]), self.bounds["x"][1])
        pos[1] = min(max(pos[1], self.bounds["d"][0]), self.bounds["d"][1])
