"""Cá Sấu Năm Chèo theo TICKET-02 mục 1.2. Chủ file: Huyền.

Số liệu đọc từ `tuning.gather.monsters`. `step` cập nhật quái theo id rồi xét tối đa một hit.
Ngất do gather xử lý sau khi `step` trả về, để giữ đúng thứ tự event của mục 4.5.
"""

import math

from ..ids import sort_by_id

TICK = 60.0


class MonsterSet:
    def __init__(self, config, bounds, monsters=None, day=1):
        self.config = config
        self.species = config["species"]
        self.bounds = bounds
        if monsters is None:
            monsters = [m for m in config["spawns"] if m.get("from_day", 1) <= day]
        self.monsters = sort_by_id([{
            "id": m["id"], "kind": m["kind"], "pos": [float(c) for c in m["pos"]],
            "waypoints": [[float(c) for c in w] for w in m["waypoints"]],
            "target_idx": m.get("target_idx", 1), "state": m.get("state", "patrol"),
            "state_ticks_left": m.get("state_ticks_left", 0), "recoil_dir": m.get("recoil_dir"),
        } for m in monsters])

    def snapshot(self):
        return [{k: (list(v) if k == "pos" else v) for k, v in m.items()} for m in self.monsters]

    def step(self, player, events):
        """`player` cần pos, hp, hold, invuln_ticks. Trả id quái vừa gây hit hoặc None."""
        can_hit = []
        for m in self.monsters:
            if m["state"] == "recoil":
                self._recoil_step(m)
            else:
                self._update(m, player.pos)
                can_hit.append(m)
        return self._resolve_hit(can_hit, player, events)

    # --- di chuyển ---------------------------------------------------------------
    def _update(self, m, player_pos):
        s = self.species[m["kind"]]
        distance = math.dist(m["pos"], player_pos)
        in_depth = player_pos[1] >= s["depths"][0]
        if m["state"] == "patrol" and in_depth and distance <= s["detect_radius"]:
            m["state"] = "chase"
        elif m["state"] == "chase" and (distance > s["exit_radius"] or not in_depth):
            m["state"] = "patrol"
        if m["state"] == "chase":
            self._toward(m, player_pos, s["chase_speed"])
        else:
            target = m["waypoints"][m["target_idx"]]
            if self._toward(m, target, s["patrol_speed"]):
                m["target_idx"] = 1 - m["target_idx"]
        self._clamp(m)

    @staticmethod
    def _toward(m, target, speed) -> bool:
        """Đi tới `target`; trả True nếu đã đến nơi trong bước này."""
        step = float(speed) / TICK
        distance = math.dist(m["pos"], target)
        if distance <= step:
            m["pos"] = list(target)
            return True
        m["pos"][0] += (target[0] - m["pos"][0]) / distance * step
        m["pos"][1] += (target[1] - m["pos"][1]) / distance * step
        return False

    def _recoil_step(self, m):
        s = self.species[m["kind"]]
        amount = float(s["recoil_dist"]) / int(s["recoil_ticks"])
        m["pos"][0] += m["recoil_dir"][0] * amount
        m["pos"][1] += m["recoil_dir"][1] * amount
        self._clamp(m)
        m["state_ticks_left"] -= 1
        if m["state_ticks_left"] <= 0:
            m.update(state="patrol", state_ticks_left=0, recoil_dir=None)

    def _clamp(self, m):
        lo_d, hi_d = self.species[m["kind"]]["depths"]
        x_lo, x_hi = self.bounds["x"]
        m["pos"][0] = min(max(m["pos"][0], x_lo), x_hi)
        m["pos"][1] = min(max(m["pos"][1], max(lo_d, self.bounds["d"][0])), min(hi_d, self.bounds["d"][1]))

    # --- chạm --------------------------------------------------------------------
    def _resolve_hit(self, candidates, player, events):
        if player.invuln_ticks > 0:
            return None
        best, best_distance = None, None
        for m in candidates:  # đã theo id, nên hòa khoảng cách thì id nhỏ thắng
            s = self.species[m["kind"]]
            distance = math.dist(m["pos"], player.pos)
            if player.pos[1] >= s["depths"][0] and distance <= s["hit_radius"]:
                if best is None or distance < best_distance:
                    best, best_distance = m, distance
        if best is None:
            return None
        player.hp = max(0, player.hp - 1)
        lost = [player.hold.pop() for _ in range(math.floor(len(player.hold) * self.config["loss_ratio"]))]
        player.invuln_ticks = int(self.config["invuln_ticks"])
        events.append(("monster_hit", {"monster_id": best["id"], "hp": player.hp, "lost": lost,
                                       "pos": list(player.pos)}))
        dx, dd = best["pos"][0] - player.pos[0], best["pos"][1] - player.pos[1]
        length = math.hypot(dx, dd)
        direction = [dx / length, dd / length] if length > 0 else [1.0, 0.0]
        best.update(state="recoil", state_ticks_left=int(self.species[best["kind"]]["recoil_ticks"]),
                    recoil_dir=direction)
        return best["id"]
