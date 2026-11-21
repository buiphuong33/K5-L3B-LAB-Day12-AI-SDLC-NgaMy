"""Đàn cá buổi sáng (`gather`, Phase 2). CHỦ FILE: Tâm.

KHUNG — dựng trước khi có TICKET-02 / contract v1.1. Chỗ cần đặc tả ghi `TODO(ticket)`.

Cùng kiểu với `monsters.py`: module nhận cấu hình ĐÃ CHUẨN HÓA (`settings`) thay vì đọc thẳng
`game.contract.json`. Bên tích hợp (`gather.py`) ánh xạ tuning v1.1 vào `settings`; đổi tên khóa
contract chỉ sửa một chỗ đó. Contract chưa có phần cá thì gather KHÔNG dựng FishSchool (cá đứng yên
như Phase 1).

Giao diện đã chốt trong TEAM.md ("fish.py → gather.py"):
  - nhận `Streams` (RNG tách luồng) và `IdAllocator` (cấp id cá mới);
  - `step(phase_tick, events)`: đổi hướng theo seed, bơi, phản xạ mép, sinh cá theo `phase_tick`;
  - `fish` là danh sách dict {id, kind, pos, heading_deg}, cùng dạng gather đang dùng.

Quy tắc vàng: không hard-code số; ngẫu nhiên chỉ qua `Streams`; duyệt cá theo `sort_by_id`.
"""

import math

from ..ids import sort_by_id

# Luồng RNG riêng cho cá: thêm luồng khác (quái...) không làm lệch chuỗi của cá.
RNG_TURN = "fish_turn"
RNG_SPAWN = "fish_spawn"


class FishSchool:
    """Quản lý các đàn cá của một buổi sáng."""

    REQUIRED_SETTINGS = {
        "tick_hz",               # tick mỗi giây
        "speed",                 # đơn vị/giây; số hoặc {kind: số}
        "turn_interval_ticks",   # bao nhiêu tick đổi hướng một lần
        "turn_max_deg",          # biên độ đổi hướng tối đa mỗi lần (±)
        "spawn_interval_ticks",  # TEAM.md: 360
        "cap",                   # TEAM.md: trần 12 đàn
        "spawn_kinds",           # loài được sinh (có cá kèo)
        "min_depth",             # mép trên vùng cá bơi (cá luôn dưới mặt nước)
    }

    def __init__(self, fish, settings, bounds, streams, ids):
        missing = self.REQUIRED_SETTINGS - set(settings)
        if missing:
            raise ValueError(f"thiếu tuning fish: {sorted(missing)}")
        if not settings["spawn_kinds"]:
            raise ValueError("fish spawn_kinds rỗng")
        self.settings = dict(settings)
        self.bounds = bounds
        self.rng = streams
        self.ids = ids
        self.fish = [{"id": f["id"], "kind": f["kind"], "pos": [float(c) for c in f["pos"]],
                      "heading_deg": float(f.get("heading_deg", 0))} for f in fish]
        for f in self.fish:
            ids.reserve(f["id"])

    # --- giao diện cho gather ---------------------------------------------------
    def snapshot(self):
        return [{key: f[key] for key in ("id", "kind", "pos", "heading_deg")}
                for f in sort_by_id(self.fish)]

    def remove(self, fish_id):
        self.fish = [f for f in self.fish if f["id"] != fish_id]

    def step(self, phase_tick, events):
        """Gọi MỘT lần mỗi bước gather, đúng chỗ mục 4.5 quy định (TODO(ticket))."""
        for f in sort_by_id(self.fish):
            self._turn(f, phase_tick)
            self._swim(f)
        self._spawn(phase_tick, events)

    # --- chi tiết ----------------------------------------------------------------
    def _speed(self, kind):
        s = self.settings["speed"]
        return float(s.get(kind, 0.0) if isinstance(s, dict) else s)

    def _area(self):
        """Vùng cá bơi: (x_lo, x_hi), (d_lo, d_hi)."""
        return ((float(self.bounds["x"][0]), float(self.bounds["x"][1])),
                (float(self.settings["min_depth"]), float(self.bounds["d"][1])))

    def _turn(self, f, phase_tick):
        every = int(self.settings["turn_interval_ticks"])
        if every <= 0 or phase_tick % every != 0:
            return
        # TODO(ticket): phân phối đổi hướng (đều trong ±span? chọn từ tập hướng?) và có rút số
        #   cho mọi đàn mỗi lần hay không — ảnh hưởng tất định, phải đúng đặc tả.
        span = float(self.settings["turn_max_deg"])
        delta = self.rng.get(RNG_TURN).uniform(-span, span)
        f["heading_deg"] = (f["heading_deg"] + delta) % 360

    def _swim(self, f):
        v = self._speed(f["kind"])
        if v == 0.0:
            return
        step = v / float(self.settings["tick_hz"])
        rad = math.radians(f["heading_deg"])
        f["pos"][0] += step * math.cos(rad)
        f["pos"][1] += step * math.sin(rad)
        self._reflect(f)

    def _reflect(self, f):
        """Chạm mép thì kẹp lại trong vùng và phản xạ hướng như gương."""
        (xlo, xhi), (dlo, dhi) = self._area()
        h = f["heading_deg"]
        x, d = f["pos"]
        if x < xlo or x > xhi:
            # TODO(ticket): kẹp về mép hay gập phần vượt quá vào trong (như patrol của quái)?
            f["pos"][0] = min(max(x, xlo), xhi)
            h = 180.0 - h          # đảo thành phần x
        if d < dlo or d > dhi:
            f["pos"][1] = min(max(d, dlo), dhi)
            h = -h                 # đảo thành phần d
        f["heading_deg"] = h % 360

    def _spawn(self, phase_tick, events):
        every = int(self.settings["spawn_interval_ticks"])
        if every <= 0 or phase_tick == 0 or phase_tick % every != 0:
            return
        if len(self.fish) >= int(self.settings["cap"]):
            return
        r = self.rng.get(RNG_SPAWN)
        (xlo, xhi), (dlo, dhi) = self._area()
        kinds = self.settings["spawn_kinds"]
        # TODO(ticket): chọn loài (đều? có trọng số?), vị trí và hướng xuất hiện; thứ tự rút số.
        kind = kinds[r.randrange(len(kinds))]
        pos = [r.uniform(xlo, xhi), r.uniform(dlo, dhi)]
        heading = r.choice((0.0, 180.0))
        f = {"id": self.ids.new("F"), "kind": kind, "pos": pos, "heading_deg": heading}
        self.fish.append(f)
        # TODO(ticket): data của fish_spawned theo mục E của TICKET-02.
        events.append(("fish_spawned", {"fish_id": f["id"], "kind": kind, "pos": list(pos)}))
