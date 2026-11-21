"""Đàn cá buổi sáng theo TICKET-02 mục 1.1. Chủ file: Tâm.

Số liệu đọc từ tuning `gather`; ngẫu nhiên chỉ qua `Streams`, duyệt cá theo `sort_by_id`.
Khi `moving=False` (scenario `random_fish:false`) cá đứng yên và không sinh thêm.
"""

import math

from ..ids import sort_by_id

RNG_TURN = "fish_turn"
RNG_SPAWN = "fish_spawn"
TICK = 60.0


class FishSchool:
    def __init__(self, tuning, streams, ids, fish=None, moving=True):
        self.t = tuning
        self.rng = streams
        self.ids = ids
        self.moving = moving
        self.fish = []
        if fish is not None:
            self.fish = [{"id": f["id"], "kind": f["kind"], "pos": [float(c) for c in f["pos"]],
                          "heading_deg": float(f.get("heading_deg", 0)),
                          "age_ticks": f.get("age_ticks", 0)} for f in fish]
            for f in self.fish:
                ids.reserve(f["id"])
        elif moving:
            for _ in range(int(tuning["fish_initial"])):
                self._spawn_one()

    # --- giao diện cho gather ---------------------------------------------------
    def snapshot(self):
        return [{key: f[key] for key in ("id", "pos", "kind", "heading_deg", "age_ticks")}
                for f in sort_by_id(self.fish)]

    def remove(self, fish):
        self.fish.remove(fish)

    def step(self, phase_tick, events):
        """Gọi sau khi xét hết giờ: cá bơi rồi sinh thêm; cá mới tham gia từ bước sau."""
        if not self.moving:
            return
        for f in sort_by_id(self.fish):
            f["age_ticks"] += 1
            if f["age_ticks"] % int(self.t["fish_turn_ticks"]) == 0:
                f["heading_deg"] = self.rng.get(RNG_TURN).uniform(0.0, 360.0)
            self._swim(f)
        if phase_tick % int(self.t["fish_spawn_ticks"]) == 0 and len(self.fish) < int(self.t["fish_max"]):
            f = self._spawn_one()
            if f is not None:
                events.append(("fish_spawned", {"id": f["id"], "kind": f["kind"], "pos": list(f["pos"])}))

    # --- chi tiết ----------------------------------------------------------------
    def _swim(self, f):
        step = float(self.t["fish_speed"]) / TICK
        rad = math.radians(f["heading_deg"])
        direction = [math.cos(rad), math.sin(rad)]
        limits = (self.t["fish_x"], self.t["fish_depths"][f["kind"]])
        flipped = False
        for axis, (lo, hi) in enumerate(limits):
            value = f["pos"][axis] + direction[axis] * step
            # phản xạ phần quãng đường vượt mép; đúng mép cũng đảo thành phần hướng
            while (value >= hi and direction[axis] > 0) or (value <= lo and direction[axis] < 0):
                edge = hi if direction[axis] > 0 else lo
                value = 2 * edge - value
                direction[axis] = -direction[axis]
                flipped = True
            f["pos"][axis] = value
        if flipped:
            f["heading_deg"] = math.degrees(math.atan2(direction[1], direction[0])) % 360

    def _open_points(self):
        """Điểm sinh theo loài, cách mọi đàn đang sống hơn fish_spawn_clearance."""
        clearance = self.t["fish_spawn_clearance"]
        result = {}
        for kind in sorted(self.t["fish_spawn_depths"]):
            points = [[float(x), float(d)] for x in self.t["fish_spawn_x"]
                      for d in self.t["fish_spawn_depths"][kind]
                      if all(math.dist((x, d), f["pos"]) > clearance for f in self.fish)]
            if points:
                result[kind] = points
        return result

    def _spawn_one(self):
        points = self._open_points()
        if not points:
            return None
        r = self.rng.get(RNG_SPAWN)
        kinds = list(points)
        weights = [self.t["fish_weights"][k] for k in kinds]
        roll = r.random() * sum(weights)
        kind = kinds[-1]
        for k, weight in zip(kinds, weights):
            if roll < weight:
                kind = k
                break
            roll -= weight
        pos = r.choice(points[kind])
        f = {"id": self.ids.new("F"), "kind": kind, "pos": pos,
             "heading_deg": r.uniform(0.0, 360.0), "age_ticks": 0}
        self.fish.append(f)
        return f
