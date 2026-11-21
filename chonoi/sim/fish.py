"""Đàn cá buổi sáng (`gather`, Phase 2). CHỦ FILE: Tâm.

KHUNG — dựng trước khi có TICKET-02 / contract v1.1. Chỗ cần đặc tả ghi `TODO(ticket)`.

Giao diện đã chốt trong TEAM.md ("fish.py → gather.py"):
  - nhận `Streams` (RNG tách luồng) và `IdAllocator` (cấp id cá mới);
  - `step(phase_tick, events)`: cá bơi, phản xạ mép, đổi hướng theo seed, sinh cá theo `phase_tick`;
  - `fish` là danh sách dict {id, kind, pos, heading_deg} — CÙNG dạng gather đang dùng, nên
    `_catch` / `snapshot` của gather không phải đổi.

Quy tắc vàng: số liệu chỉ đọc từ tuning (`game.contract.json`), ngẫu nhiên chỉ qua `Streams`,
duyệt cá theo `sort_by_id`. Thiếu khóa tuning (contract v1.0) -> cá đứng yên, không sinh: giữ
nguyên hành vi Phase 1.
"""

import math

from ..ids import sort_by_id

TICK = 60.0

# Luồng RNG riêng cho cá: thêm luồng khác (quái...) không làm lệch chuỗi của cá.
RNG_TURN = "fish_turn"
RNG_SPAWN = "fish_spawn"

# TODO(ticket): đổi tên khóa cho khớp contract v1.1 khi Phương đẩy lên. Chỉ sửa ở đây.
KEYS = {
    "speed": "fish_speed",                        # đơn vị/giây; số hoặc {kind: số}
    "turn_interval": "fish_turn_interval_ticks",  # bao nhiêu tick đổi hướng một lần
    "turn_max_deg": "fish_turn_max_deg",          # biên độ đổi hướng tối đa mỗi lần (±)
    "spawn_interval": "fish_spawn_interval_ticks",  # TEAM.md: 360
    "cap": "fish_cap",                            # TEAM.md: trần 12 đàn
    "spawn_kinds": "fish_spawn_kinds",            # loài được sinh (có cá kèo)
    "initial": "fish_initial",                    # TEAM.md: 8 đàn đầu ca (v1.0 có 6)
}


class FishSchool:
    """Tập đàn cá của một buổi sáng."""

    def __init__(self, tuning_gather, streams, ids, initial):
        self.t = tuning_gather
        self.rng = streams
        self.ids = ids
        self.fish = [{"id": f["id"], "kind": f["kind"], "pos": [float(c) for c in f["pos"]],
                      "heading_deg": float(f.get("heading_deg", 0))} for f in initial]
        for f in self.fish:
            ids.reserve(f["id"])

    # --- đọc tuning ------------------------------------------------------------
    def _get(self, name, default=None):
        return self.t.get(KEYS[name], default)

    def _speed(self, kind) -> float:
        s = self._get("speed", 0.0)
        return float(s.get(kind, 0.0) if isinstance(s, dict) else s)

    def _bounds(self):
        """Vùng cá bơi: [x_lo, x_hi], [d_lo, d_hi]. Cá luôn ở DƯỚI mặt nước."""
        b = self.t["bounds"]
        # TODO(ticket): mép trên của cá là surface_depth hay một độ sâu tối thiểu riêng?
        return (b["x"][0], b["x"][1]), (self.t["surface_depth"], b["d"][1])

    # --- một bước --------------------------------------------------------------
    def step(self, phase_tick, events):
        """Gọi MỘT lần mỗi bước gather, đúng chỗ mục 4.5 quy định (TODO(ticket))."""
        for f in sort_by_id(self.fish):
            self._turn(f, phase_tick)
            self._swim(f)
        self._spawn(phase_tick, events)

    def _turn(self, f, phase_tick):
        every = self._get("turn_interval")
        span = self._get("turn_max_deg")
        if not every or span is None or phase_tick % int(every) != 0:
            return
        # TODO(ticket): phân phối đổi hướng (đều trong ±span? chọn từ tập hướng?) và có rút số
        #   cho mọi đàn mỗi lần hay không — ảnh hưởng tất định, phải đúng đặc tả.
        delta = self.rng.get(RNG_TURN).uniform(-float(span), float(span))
        f["heading_deg"] = (f["heading_deg"] + delta) % 360

    def _swim(self, f):
        v = self._speed(f["kind"])
        if v == 0.0:
            return
        rad = math.radians(f["heading_deg"])
        f["pos"][0] += v * math.cos(rad) / TICK
        f["pos"][1] += v * math.sin(rad) / TICK
        self._reflect(f)

    def _reflect(self, f):
        """Chạm mép thì kẹp lại trong vùng và phản xạ hướng như gương."""
        (xlo, xhi), (dlo, dhi) = self._bounds()
        h = f["heading_deg"]
        x, d = f["pos"]
        if x < xlo or x > xhi:
            # TODO(ticket): kẹp về mép hay gập phần vượt quá vào trong?
            f["pos"][0] = float(min(max(x, xlo), xhi))
            h = 180.0 - h          # đảo thành phần x
        if d < dlo or d > dhi:
            f["pos"][1] = float(min(max(d, dlo), dhi))
            h = -h                 # đảo thành phần d
        f["heading_deg"] = h % 360

    def _spawn(self, phase_tick, events):
        every = self._get("spawn_interval")
        cap = self._get("cap")
        kinds = self._get("spawn_kinds")
        if not every or cap is None or not kinds:
            return
        if phase_tick == 0 or phase_tick % int(every) != 0 or len(self.fish) >= int(cap):
            return
        r = self.rng.get(RNG_SPAWN)
        (xlo, xhi), (dlo, dhi) = self._bounds()
        # TODO(ticket): chọn loài (đều? có trọng số?), vị trí và hướng xuất hiện; thứ tự rút số.
        kind = kinds[r.randrange(len(kinds))]
        pos = [r.uniform(xlo, xhi), r.uniform(dlo, dhi)]
        heading = r.choice((0.0, 180.0))
        f = {"id": self.ids.new("F"), "kind": kind, "pos": pos, "heading_deg": heading}
        self.fish.append(f)
        # TODO(ticket): data của fish_spawned theo mục E của TICKET-02.
        events.append(("fish_spawned", {"fish_id": f["id"], "kind": kind, "pos": list(pos)}))

    # --- tiện ích cho gather --------------------------------------------------
    def remove(self, fish_id):
        self.fish = [f for f in self.fish if f["id"] != fish_id]

    def snapshot(self) -> list:
        return [{"id": f["id"], "pos": f["pos"], "kind": f["kind"], "heading_deg": f["heading_deg"]}
                for f in sort_by_id(self.fish)]
