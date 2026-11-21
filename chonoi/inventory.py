"""File kho (Contract G). Chọn schema theo contract_version (chủ: Phương):

  v1.0–v1.1 — kho ĐẾM:    {"items": {"ca_loc": 1, ...}}
  v1.2      — kho CÁ THỂ: {"items": [{"id": "I1", "kind": "ca_linh", "fresh": 100}, ...]}  (sắp theo id)
              kho đếm, sai schema, kind lạ, id trùng, fresh ngoài [0, 100] → BadInput (mã 2).

Đọc: từ chối sai schema / id lạ / số âm (BadInput -> mã 2).
Ghi: bỏ mục bằng 0, qua file tạm cùng thư mục rồi thay thế, byte-ổn-định.
"""

import json
import os
import tempfile

from .errors import BadInput

KINDS = ("ca_loc", "ca_linh", "ca_keo", "bong_dien_dien", "bong_sung", "keo_neo")  # v1.1: 6 nguyên liệu
KINDS_P1 = KINDS  # tên cũ, giữ để không vỡ import


def validate_items(items, kinds=KINDS_P1):
    if not isinstance(items, dict):
        raise BadInput("items phải là object")
    out = {}
    for k, v in items.items():
        if k not in kinds:
            raise BadInput(f"nguyên liệu lạ: {k}")
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise BadInput(f"số lượng không hợp lệ cho {k}: {v!r}")
        if v > 0:
            out[k] = v
    return out


def is_v12(version) -> bool:
    try:
        return tuple(int(x) for x in str(version).split(".")[:2]) >= (1, 2)
    except ValueError:
        return False


def read_inventory(path: str, kinds=KINDS_P1, version="1.1"):
    """v1.1 → dict đếm; v1.2 → list cá thể NỘI BỘ (chonoi.items), giữ nguyên id/fresh kể cả hàng ươn."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được file kho {path}: {e}")
    if not isinstance(data, dict) or set(data.keys()) != {"items"}:
        raise BadInput("file kho chỉ được có khóa gốc 'items'")
    if is_v12(version):
        from .items import list_from_json
        if not isinstance(data["items"], list):
            raise BadInput("contract v1.2: file kho phải là mảng cá thể (kho đếm không còn hợp lệ)")
        return list_from_json(data["items"], kinds, "items")
    return validate_items(data["items"], kinds)


def hold_to_items(hold: list) -> dict:
    """Khoang (mảng id theo thứ tự nhặt) -> object đếm, sắp theo id nguyên liệu."""
    counts = {}
    for k in hold:
        counts[k] = counts.get(k, 0) + 1
    return {k: counts[k] for k in sorted(counts)}


def write_inventory(path: str, items):
    """dict đếm (v1.1) hoặc list cá thể nội bộ (v1.2, xuất sắp theo id). Ghi file tạm rồi thay nguyên tử."""
    if isinstance(items, list):
        from .items import list_to_json, sorted_by_id
        items = list_to_json(sorted_by_id(items))
    else:
        items = {k: items[k] for k in sorted(items) if items[k] > 0}
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".inv-", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"items": items}, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
