"""Cá thể nguyên liệu có độ tươi (Test Contract v1.2). Chủ file: Phương.

Giao diện chung cho gather (Tâm), quan (Nga), day/runner/inventory (Phương), scenario (Nga):

    item = {"id": "I1", "kind": "ca_linh", "fresh": Fraction(100)}   # dạng NỘI BỘ

- `fresh` lưu bằng `fractions.Fraction` → phép trừ mỗi tick và so ngưỡng 30 CHÍNH XÁC
  (0.5/s = 1/120 mỗi tick ở giỏ, 0.25/s = 1/240 mỗi tick ở kho quán; tương đương 240 đơn vị/điểm,
  trừ 2 và 1 đơn vị/tick như ticket gợi ý, nhưng nhận được cả fresh lẻ trong fixture).
- Xuất JSON bằng `to_json` (float, repr Python đọc lại ra đúng giá trị).
- Mọi danh sách cá thể truyền giữa các pha (gather_end → quán, trong `day`) là list item NỘI BỘ,
  không làm tròn, không hao thêm.
- Id cá thể cấp bằng `IdAllocator` chung với tiền tố "I" (`new_item`), tăng xuyên pha và Ngày.
"""

import math
from fractions import Fraction

from .errors import BadInput
from .ids import sort_by_id

PREFIX = "I"
TICK_HZ = 60

# Mặc định theo ticket; luôn ưu tiên đọc từ tuning["freshness"] qua `Freshness(tuning)`.
DEFAULT_FRESHNESS = {"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30}


def _frac(v):
    return Fraction(v) if isinstance(v, int) else Fraction(str(v)) if isinstance(v, float) else Fraction(v)


class Freshness:
    """Thông số độ tươi đọc từ tuning (khối `freshness`, v1.2)."""

    def __init__(self, tuning=None):
        f = dict(DEFAULT_FRESHNESS)
        if tuning and isinstance(tuning.get("freshness"), dict):
            f.update(tuning["freshness"])
        self.initial = _frac(f["initial"])
        self.spoiled_below = _frac(f["spoiled_below"])
        self.gather_per_tick = _frac(f["gather_decay_per_s"]) / TICK_HZ
        self.quan_per_tick = _frac(f["quan_decay_per_s"]) / TICK_HZ

    def is_spoiled(self, item) -> bool:
        return item["fresh"] < self.spoiled_below

    def usable(self, item) -> bool:
        return not self.is_spoiled(item)


# --- tạo / đọc / xuất -------------------------------------------------------------------------------
def new_item(ids, kind, fresh=None, fr: Freshness = None):
    """Cá thể mới (bắt/hái): fresh = initial (100), id kế tiếp họ "I"."""
    if fresh is None:
        fresh = (fr or Freshness()).initial
    return {"id": ids.new(PREFIX), "kind": kind, "fresh": _frac(fresh)}


def to_json(item) -> dict:
    f = item["fresh"]
    v = int(f) if f.denominator == 1 else float(f)
    return {"id": item["id"], "kind": item["kind"], "fresh": v}


def list_to_json(items) -> list:
    """Xuất theo thứ tự đang có (giỏ: thứ tự vào giỏ). Muốn sắp theo id thì gọi `sorted_by_id` trước."""
    return [to_json(i) for i in items]


def sorted_by_id(items) -> list:
    return sort_by_id(items)


def from_json(obj, kinds, where="item"):
    """Kiểm một cá thể JSON {id, kind, fresh} → item nội bộ. Sai → BadInput (mã 2)."""
    if not isinstance(obj, dict) or set(obj) != {"id", "kind", "fresh"}:
        raise BadInput(f"{where}: cá thể phải có đúng {{id, kind, fresh}}")
    iid, kind, fresh = obj["id"], obj["kind"], obj["fresh"]
    if not isinstance(iid, str) or not iid:
        raise BadInput(f"{where}: id phải là chuỗi khác rỗng")
    if kind not in kinds:
        raise BadInput(f"{where}.{iid}: kind lạ {kind!r}")
    if isinstance(fresh, bool) or not isinstance(fresh, (int, float)) or not math.isfinite(fresh) or not 0 <= fresh <= 100:
        raise BadInput(f"{where}.{iid}: fresh phải hữu hạn trong [0, 100]")
    return {"id": iid, "kind": kind, "fresh": _frac(fresh)}


def list_from_json(arr, kinds, where="items", seen=None):
    """Kiểm mảng cá thể; `seen` (set) dùng chung để bắt id trùng GIỮA các nơi chứa (giỏ, kho, tay...)."""
    if not isinstance(arr, list):
        raise BadInput(f"{where} phải là mảng cá thể {{id, kind, fresh}}")
    seen = set() if seen is None else seen
    out = []
    for i, obj in enumerate(arr):
        it = from_json(obj, kinds, f"{where}[{i}]")
        if it["id"] in seen:
            raise BadInput(f"{where}: id cá thể trùng {it['id']}")
        seen.add(it["id"])
        out.append(it)
    return out


def reserve_ids(ids, items):
    for it in items:
        ids.reserve(it["id"])


def clone(items):
    return [dict(i) for i in items]


# --- hao tươi -----------------------------------------------------------------------------------------
def decay(items, per_tick, fr: Freshness):
    """Trừ `per_tick` cho mọi cá thể (kẹp 0). Trả danh sách cá thể VỪA ươn (≥ ngưỡng → < ngưỡng), sắp theo id."""
    newly = []
    for it in items:
        before = it["fresh"]
        after = before - per_tick
        if after < 0:
            after = Fraction(0)
        it["fresh"] = after
        if before >= fr.spoiled_below > after:
            newly.append(it)
    return sort_by_id(newly)


# --- tiện ích cho quán ----------------------------------------------------------------------------------
def freshest(items, kind, n, fr: Freshness, exclude=()):
    """n cá thể khả dụng (chưa ươn, không nằm trong `exclude` id) tươi nhất của `kind`, hòa theo id. Thiếu → None."""
    from .ids import id_key
    pool = [i for i in items if i["kind"] == kind and fr.usable(i) and i["id"] not in exclude]
    pool.sort(key=lambda i: (-i["fresh"], id_key(i["id"])))
    return pool[:n] if len(pool) >= n else None


def fresh_price(list_price, used_items):
    """base_price = floor(giá niêm yết × trung bình fresh / 100), tính chính xác."""
    if not used_items:
        return int(list_price)
    avg = sum((i["fresh"] for i in used_items), Fraction(0)) / len(used_items)
    return math.floor(Fraction(list_price) * avg / 100)


def counts(items) -> dict:
    """Đếm theo loại (cho HUD / tương thích)."""
    c = {}
    for i in items:
        c[i["kind"]] = c.get(i["kind"], 0) + 1
    return dict(sorted(c.items()))
