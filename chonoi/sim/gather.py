"""Buổi sáng — Lặn & Hái (`gather`). KHUNG: bơi, chặn mép, đồng hồ, cập bến, xuất kho.

Mặt cắt dòng sông nhìn NGANG: vị trí `[x, d]` (x sang phải, `d` độ sâu hướng xuống, d = 0 là mặt nước).
`move = [x, d]`: thành phần thứ hai DƯƠNG = bơi xuống. Hướng mặt là góc từ +x, dương = xuống.

Đã làm sẵn để smoke test chạy được: bơi + tăng/giảm tốc, chặn mép (d không âm), đồng hồ và hết giờ,
cập bến (`interact` trong vùng bến -> `gather_end` reason `docked`), xuất kho, snapshot đầy đủ trường gather.

Nhóm viết tiếp (đúng thứ tự một bước trong PRD mục 13.8, "Gather"):
  ĐÃ LÀM (lát 1, Tâm): bơi + oxy + biên + giỏ — xem `_update_oxygen`, `_faint`, `_hold_push/_hold_pop`
      - oxy: dưới nước (d > surface_depth) trừ 1 tick/tick, mặt nước hồi oxygen_refill_per_tick, kẹp [0, max]
      - ngạt: oxy = 0 và đang dưới nước -> đếm zero_oxy_ticks, đủ choke_interval_ticks thì -1 Máu (choke)
      - Máu về 0 -> ngất (faint, gather_end reason `fainted`, mất toàn bộ giỏ, kho rỗng)
      - sự kiện dive / surface / oxygen_empty / choke / faint
      - giỏ: thứ tự nhặt (LIFO), sức chứa hold_capacity
  ĐÃ LÀM (lát 2): hái + bắt cá + cập bến + kho — xem `_harvest`, `_catch`
      - hái nút ở mặt nước (gather, hold_full), nút mọc lại (node_regrown đã có phần đếm ngược)
      - bắt đàn cá bằng `catch` (fish_caught, hold_full, hồi chiêu catch_cd_ticks, chỉ khi dưới nước)
      - cập bến xét TRƯỚC hái (đã có); ghi kho đúng một lần do runner lo
Các tính năng của phase sau chưa nằm trong khung này.
"""

import math
from fractions import Fraction

from .. import items as it
from ..ids import sort_by_id
from ..inventory import hold_to_items
from .fish import FishSchool
from .monsters import MonsterSet
from .ramp import ramp_velocity

TICK = 60.0
AXES = ("x", "d")


def is_v12(tuning) -> bool:
    """Kho cá thể bật theo `contract_version` (ADR 0001 mục 5), KHÔNG theo việc có khối `freshness`."""
    return str(tuning.get("contract_version", "1.1")) >= "1.2"


def _item_in(e):
    """Cá thể từ scenario / mẫu day (fresh là số JSON) hoặc đã ở dạng nội bộ (Fraction) -> dạng nội bộ."""
    f = e["fresh"]
    fresh = f if isinstance(f, Fraction) else Fraction(str(f)) if isinstance(f, float) else Fraction(f)
    return {"id": e["id"], "kind": e["kind"], "fresh": fresh}


def _jsonable(e):
    """Cá thể nội bộ -> JSON {id, kind, fresh}; phần tử đã là JSON / tên loài (v1.1) giữ nguyên."""
    return it.to_json(e) if isinstance(e, dict) and isinstance(e.get("fresh"), Fraction) else e


class GatherSim:
    mode = "gather"
    phase = "gather"

    def __init__(self, tuning, scenario, streams, ids):
        t = tuning["gather"]
        self.t = t
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        self.heading = float(p.get("heading_deg", t["start_heading_deg"]))
        self.oxygen_max = int(round(t["oxygen_max_s"] * TICK))
        self.oxygen_ticks = p.get("oxygen_ticks", self.oxygen_max)
        self.hp = p.get("hp", t["hp_max"])
        self.zero_oxy_ticks = p.get("zero_oxy_ticks", 0)
        self.invuln_ticks = p.get("invuln_ticks", 0)
        self.catch_cd_ticks = p.get("catch_cd_ticks", 0)
        # Độ tươi (TICKET-03, ADR 0001): contract >= 1.2 -> giỏ chứa cá thể NỘI BỘ của `chonoi.items`
        # {id, kind, fresh: Fraction}; contract 1.1 -> giỏ là mảng tên loài như cũ.
        self._fr = it.Freshness(tuning) if is_v12(tuning) else None
        self.hold = []  # thứ tự vào giỏ, cuối mảng là mới nhất (LIFO khi mất hàng)
        for e in scenario.get("hold", []):
            if self._fr is None:
                self.hold.append(e)
            else:
                ids.reserve(e["id"])
                self.hold.append(_item_in(e))
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))
        # nút và đàn cá: scenario THAY THẾ danh sách mặc định; random_fish=false tắt cá mặc định
        src_nodes = scenario["nodes"] if "nodes" in scenario else t["nodes"]
        self.nodes = [{"id": n["id"], "kind": n["kind"], "pos": [float(c) for c in n["pos"]],
                       "regrow_ticks": n.get("regrow_ticks", 0)} for n in src_nodes]
        for n in self.nodes:
            ids.reserve(n["id"])
        # random_fish=false: chỉ có cá fixture và đứng yên; bật thì `fish` thay đàn đầu ca, vẫn bơi/sinh
        moving = scenario.get("random_fish", True)
        src_fish = scenario.get("fish", None if moving else [])
        self.school = FishSchool(t, streams, ids, fish=src_fish, moving=moving)
        self.monster_set = MonsterSet(t["monsters"], t["bounds"], monsters=scenario.get("monsters"),
                                      day=t.get("current_day", 1))
        self._phase_tick = 0
        self.money = 0
        self.earned = 0
        self.reputation = tuning["quan"]["reputation_initial"]
        self.done = False
        self.reason = None

    # --- giao diện cho runner -------------------------------------------------
    def inventory_items(self):
        """v1.2: list cá thể NỘI BỘ sắp theo id (write_inventory / day tự xuất JSON). v1.1: object đếm."""
        if self._fr is None:
            return hold_to_items(self.hold)
        return it.clone(it.sorted_by_id(self.hold))

    def snapshot(self) -> dict:
        return {
            "player": {"pos": self.pos, "vel": self.vel, "heading_deg": self.heading,
                       "oxygen_ticks": self.oxygen_ticks, "oxygen_max_ticks": self.oxygen_max,
                       "hp": self.hp, "hp_max": self.t["hp_max"], "zero_oxy_ticks": self.zero_oxy_ticks,
                       "invuln_ticks": self.invuln_ticks, "catch_cd_ticks": self.catch_cd_ticks,
                       "at_surface": self._at_surface()},
            "hold": [_jsonable(e) for e in self.hold], "hold_count": len(self.hold),
            "hold_capacity": self.t["hold_capacity"],
            "nodes": [{"id": n["id"], "pos": n["pos"], "kind": n["kind"],
                       "ready": n["regrow_ticks"] == 0, "regrow_ticks": n["regrow_ticks"]}
                      for n in sort_by_id(self.nodes)],
            "fish": self.school.snapshot(),
            "monsters": self.monster_set.snapshot(),
        }

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        events = []
        self._phase_tick += 1
        # 1. đồng hồ và hàng có sẵn: giảm bộ đếm, nút mọc lại
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        self.invuln_ticks = max(0, self.invuln_ticks - 1)
        self.catch_cd_ticks = max(0, self.catch_cd_ticks - 1)
        for n in sort_by_id(self.nodes):
            if n["regrow_ticks"] > 0:
                n["regrow_ticks"] -= 1
                if n["regrow_ticks"] == 0:
                    events.append(("node_regrown", {"node_id": n["id"]}))
        # 1b. độ tươi của hàng CÓ SẴN đầu bước (hàng mới vào trong bước này hao từ bước sau)
        self._decay(events)
        # 2. bơi + chặn mép; so phân vùng đầu/cuối bước -> dive / surface
        was_surface = self._at_surface()
        self._move(inp)
        now_surface = self._at_surface()
        if was_surface and not now_surface:
            events.append(("dive", {"pos": list(self.pos)}))
        elif now_surface and not was_surface:
            events.append(("surface", {"pos": list(self.pos)}))
        # 2b. oxy theo d CUỐI bước, ngạt, Máu, ngất
        if self._update_oxygen(now_surface, events):
            return events
        # 2c. thủy quái theo id, tối đa một hit (lost là cá thể nội bộ -> đổi sang JSON để ghi JSONL)
        first = len(events)
        self.monster_set.step(self, events)
        for _, data in events[first:]:
            if isinstance(data, dict) and isinstance(data.get("lost"), list):
                data["lost"] = [_jsonable(e) for e in data["lost"]]
        if self.hp <= 0:
            self._faint(events, cause="monster")
            return events
        # 3. interact: bến trước, rồi hái
        if inp.pressed("interact"):
            if self._in_dock():
                self._finish("docked", events)
                return events
            if now_surface:
                self._harvest(events)
        # 4. bắt cá
        if inp.pressed("catch") and self.catch_cd_ticks == 0 and not now_surface:
            self._catch(events)
        # 5. hết giờ
        if self.time_left_ticks <= 0:
            self._finish("time", events)
            return events
        # 6. còn giờ: cá bơi rồi sinh thêm (bắt cá ở trên dùng vị trí trước khi bơi)
        self.school.step(self._phase_tick, events)
        return events

    # --- lát 1: oxy, ngạt, Máu, giỏ ---------------------------------------------
    def _update_oxygen(self, at_surface, events) -> bool:
        """Cập nhật oxy / ngạt / Máu sau khi bơi. Trả True nếu vừa ngất (buổi đã kết thúc)."""
        if at_surface:
            self.oxygen_ticks = min(self.oxygen_max, self.oxygen_ticks + int(self.t["oxygen_refill_per_tick"]))
            self.zero_oxy_ticks = 0
            return False
        before = self.oxygen_ticks
        self.oxygen_ticks = max(0, self.oxygen_ticks - 1)
        if before > 0 and self.oxygen_ticks == 0:
            events.append(("oxygen_empty", {"oxygen_ticks": 0}))
        if self.oxygen_ticks > 0:
            self.zero_oxy_ticks = 0
            return False
        self.zero_oxy_ticks += 1
        if self.zero_oxy_ticks < int(self.t["choke_interval_ticks"]):
            return False
        self.zero_oxy_ticks = 0
        self.hp = max(0, self.hp - 1)
        events.append(("choke", {"hp": self.hp}))
        if self.hp > 0:
            return False
        self._faint(events)
        return True

    def _faint(self, events, cause="choke"):
        """Máu về 0: mất toàn bộ giỏ, kết thúc buổi với kho rỗng."""
        lost = [_jsonable(e) for e in reversed(self.hold)]  # thứ tự bỏ: nhặt sau bỏ trước
        self.hold = []
        events.append(("faint", {"cause": cause, "lost": lost, "hp": 0}))
        self._finish("fainted", events)

    # --- lát 2: hái, bắt cá -----------------------------------------------------
    def _free_slots(self) -> int:
        return int(self.t["hold_capacity"]) - len(self.hold)

    def _nearest(self, entities, radius):
        """Thực thể gần nhất trong bán kính (tính cả đúng mép), hòa thì id nhỏ trước."""
        in_range = [e for e in sort_by_id(entities) if math.dist(self.pos, e["pos"]) <= radius]
        return min(in_range, key=lambda e: math.dist(self.pos, e["pos"])) if in_range else None

    def _harvest(self, events):
        node = self._nearest([n for n in self.nodes if n["regrow_ticks"] == 0], self.t["interact_radius"])
        if node is None:
            return
        amount = int(self.t["node_yield"])
        free = self._free_slots()
        if free < amount:
            events.append(("hold_full", {"action": "gather", "node_id": node["id"],
                                         "required": amount, "free": free}))
            return
        self._add(node["kind"], amount)
        node["regrow_ticks"] = int(round(self.t["regrow_s"] * TICK))
        events.append(("gather", {"node_id": node["id"], "kind": node["kind"], "amount": amount}))

    def _catch(self, events):
        fish = self._nearest(self.school.fish, self.t["catch_radius"])
        if fish is None:
            return
        amount = int(self.t["fish_yield"][fish["kind"]])
        free = self._free_slots()
        if free < amount:
            events.append(("hold_full", {"action": "catch", "fish_id": fish["id"],
                                         "required": amount, "free": free}))
            return
        self._add(fish["kind"], amount)
        self.school.remove(fish)
        self.catch_cd_ticks = int(round(self.t["catch_cooldown_s"] * TICK))
        events.append(("fish_caught", {"fish_id": fish["id"], "kind": fish["kind"], "yield": amount}))

    # --- Phase 3: độ tươi (dùng chonoi/items.py theo ADR 0001) -----------------------
    def _add(self, kind, amount):
        """Thêm `amount` món vào giỏ; v1.2 cấp id `I…` theo thứ tự vào giỏ, fresh = initial."""
        for _ in range(amount):
            if self._fr is None:
                self.hold.append(kind)
            else:
                self.hold.append(it.new_item(self.ids, kind, fr=self._fr))

    def _decay(self, events):
        """Hao tươi hàng có sẵn trong giỏ (kẹp 0); phát `spoiled` theo id cho cá thể vừa qua ngưỡng."""
        if self._fr is None or not self.hold:
            return
        for e in it.decay(self.hold, self._fr.gather_per_tick, self._fr):
            events.append(("spoiled", {"item_id": e["id"], "kind": e["kind"], "location": "hold"}))

    # --- tiện ích ---------------------------------------------------------------
    def _at_surface(self) -> bool:
        return self.pos[1] <= self.t["surface_depth"]

    def _in_dock(self) -> bool:
        return math.dist(self.pos, self.t["dock_pos"]) <= self.t["dock_radius"]

    def _finish(self, reason, events):
        self.done = True
        self.reason = reason
        inv = self.inventory_items()
        if self._fr is not None:
            inv = it.list_to_json(inv)  # event JSONL theo schema file kho; runner/day dùng bản nội bộ
        events.append(("gather_end", {"reason": reason, "inventory": {"items": inv}}))

    def _move(self, inp):
        speed = self.t["swim_speed"]
        mx, md = inp.move
        self.vel = ramp_velocity(self, (mx * speed, md * speed), int(self.t["ramp_max_ticks"]))
        if (mx, md) != (0.0, 0.0):
            self.heading = math.degrees(math.atan2(md, mx)) % 360
        b = self.t["bounds"]
        for i, axis in enumerate(AXES):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i] = lo
                self.vel[i] = max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i] = hi
                self.vel[i] = min(0.0, self.vel[i])
