"""Đàn cá buổi sáng (`gather`, Phase 2, contract v1.1). CHỦ FILE: Tâm.

Cùng kiểu với `monsters.py`: module nhận cấu hình ĐÃ CHUẨN HÓA (`settings`); `gather.py` ánh xạ
tuning v1.1 (`fish_*`) vào `settings` ở một chỗ (`FISH_TUNING`).

Luật (theo contract v1.1; chỗ đặc tả chưa rõ là GIẢ ĐỊNH, ghi ở docs/clarify.md #8–#13):
  - Cá bơi NGANG với tốc độ `speed`, hướng 0° (sang phải) hoặc 180° (sang trái); độ sâu giữ nguyên
    (`fish_depths` theo loài không dùng trong luật bơi; để `scenario.py` kiểm `fish[]`).
  - Mép `x_range` (fish_x): phần vượt quá gập ngược vào trong và đảo hướng (cùng cách patrol quái).
  - Mỗi `turn_ticks` tick: duyệt cá theo id, mỗi đàn rút 1 số luồng `fish_turn`, < 0.5 thì đảo hướng.
  - Mỗi `spawn_ticks` tick, nếu còn dưới `max` đàn: rút từ luồng `fish_spawn` theo thứ tự
    loài (theo `weights`) -> độ sâu (đều trong `spawn_depths[loài]`) -> x (chọn đều trong các ô
    `spawn_x` cách mọi đàn ≥ `spawn_clearance`) -> hướng (0/180). Không còn ô hợp lệ thì bỏ lượt.
    Đàn mới lấy id từ `IdAllocator` ("F"), phát `fish_spawned`.

Quy tắc vàng: không hard-code số; ngẫu nhiên chỉ qua `Streams`; duyệt cá theo `sort_by_id`.
"""

import math

from ..ids import sort_by_id

# Luồng RNG riêng cho cá: thêm luồng khác (quái...) không làm lệch chuỗi của cá.
RNG_TURN = "fish_turn"
RNG_SPAWN = "fish_spawn"
TURN_PROB = 0.5  # GIẢ ĐỊNH (clarify #10): xác suất đảo hướng mỗi lần xét


class FishSchool:
    """Quản lý các đàn cá của một buổi sáng."""

    REQUIRED_SETTINGS = {
        "tick_hz", "speed", "x_range", "turn_ticks", "max",
        "spawn_ticks", "spawn_x", "spawn_depths", "spawn_clearance", "weights",
    }

    def __init__(self, fish, settings, streams, ids, spawn=True):
        missing = self.REQUIRED_SETTINGS - set(settings)
        if missing:
            raise ValueError(f"thiếu tuning fish: {sorted(missing)}")
        self.settings = dict(settings)
        self.rng = streams
        self.ids = ids
        self.spawn_enabled = spawn
        # `fish` là list dùng CHUNG với gather (gather._catch xóa trực tiếp): không gán lại list này.
        self.fish = [{"id": f["id"], "kind": f["kind"], "pos": [float(c) for c in f["pos"]],
                      "heading_deg": float(f.get("heading_deg", 0))} for f in fish]
        for f in self.fish:
            ids.reserve(f["id"])

    # --- giao diện cho gather ---------------------------------------------------
    def snapshot(self):
        return [{key: f[key] for key in ("id", "kind", "pos", "heading_deg")}
                for f in sort_by_id(self.fish)]

    def step(self, phase_tick, events):
        """Một bước: đổi hướng (theo nhịp) -> bơi + phản xạ mép -> sinh cá (theo nhịp)."""
        turn = int(self.settings["turn_ticks"])
        turning = turn > 0 and phase_tick % turn == 0
        for f in sort_by_id(self.fish):
            if turning and self.rng.get(RNG_TURN).random() < TURN_PROB:
                f["heading_deg"] = self._flip(f["heading_deg"])
            self._swim(f)
        if self.spawn_enabled:
            self._spawn(phase_tick, events)

    # --- chi tiết ----------------------------------------------------------------
    @staticmethod
    def _dir(heading):
        return 1 if math.cos(math.radians(heading)) >= 0 else -1

    def _flip(self, heading):
        return 180.0 if self._dir(heading) > 0 else 0.0

    def _swim(self, f):
        lo, hi = (float(c) for c in self.settings["x_range"])
        direction = self._dir(f["heading_deg"])
        x = f["pos"][0] + direction * float(self.settings["speed"]) / float(self.settings["tick_hz"])
        while x < lo or x > hi:  # gập phần vượt mép vào trong và đảo hướng
            if x > hi:
                x, direction = hi - (x - hi), -1
            else:
                x, direction = lo + (lo - x), 1
        f["pos"][0] = x
        f["heading_deg"] = 0.0 if direction > 0 else 180.0

    def _spawn(self, phase_tick, events):
        every = int(self.settings["spawn_ticks"])
        if every <= 0 or phase_tick == 0 or phase_tick % every != 0:
            return
        if len(self.fish) >= int(self.settings["max"]):
            return
        r = self.rng.get(RNG_SPAWN)
        kind = self._pick_kind(r.random())
        d_lo, d_hi = (float(c) for c in self.settings["spawn_depths"][kind])
        d = r.uniform(d_lo, d_hi)
        gap = float(self.settings["spawn_clearance"])
        free = [float(x) for x in self.settings["spawn_x"]
                if all(math.dist((x, d), f["pos"]) >= gap for f in self.fish)]
        if not free:
            return
        x = free[r.randrange(len(free))]
        heading = r.choice((0.0, 180.0))
        f = {"id": self.ids.new("F"), "kind": kind, "pos": [x, d], "heading_deg": heading}
        self.fish.append(f)
        events.append(("fish_spawned", {"fish_id": f["id"], "kind": kind, "pos": [x, d],
                                        "heading_deg": heading}))

    def _pick_kind(self, u):
        """Chọn loài theo trọng số, duyệt loài theo tên để tất định."""
        weights = self.settings["weights"]
        kinds = sorted(k for k in weights if weights[k] > 0)
        total = sum(weights[k] for k in kinds)
        acc = 0.0
        for k in kinds:
            acc += weights[k] / total
            if u < acc:
                return k
        return kinds[-1]
