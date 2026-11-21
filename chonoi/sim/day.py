"""Vòng ngày (`--mode day`, Test Contract v1.1). Chủ file: Phương.

DayIntro → gather → EveningIntro → quan → DayResult → Shop → Ngày kế (hoặc hết sau Ngày `days`).
Headless không có màn Intro/Result (chỉ là UI); mô phỏng chỉ có ba pha: gather, quan, shop.

Thứ tự đổi pha (mục 4.5):
  day_start → day_plan → phase_start(gather) ở cùng tick;
  gather_end → dựng quán → phase_start(quan) cùng tick (kể cả khi ngất);
  quan_end → dựng Shop → phase_start(shop) cùng tick;
  Shop: một `buy` trước cạnh `shop_done`; hết `max_ticks` → shop_end(time).
  Đóng Shop: days_completed += 1, rồi kết thúc hoặc dựng Ngày kế ngay tick đó.
  Chỉ khi dựng Ngày mới mới sao `upgrades` (đã mua) sang `active_upgrades` (đang áp dụng).

Giao ước với gather/quan (không sửa file của Tâm/Nga):
  - gather đọc `tuning.gather.current_day` để chọn quái theo `from_day` (thiếu = Ngày 1).
  - Cấp oxygen/hp áp bằng cách ghi đè `oxygen_max_s` / `hp_max` trong bản sao tuning của Ngày.
  - Quán chỉ thấy các món trong kế hoạch Ngày (lọc `menu` theo id món trước khi lọc nguyên liệu).
"""

import copy

from ..ids import IdAllocator, sort_by_id
from ..items import PREFIX, list_to_json
from .gather import GatherSim
from .quan import QuanSim

UPGRADE_FIELD = {"oxygen": "oxygen_max_s", "hp": "hp_max"}


def plan_ingredients(menu, dishes):
    need = {}
    for dish_id in sorted(dishes):
        for kind, n in menu[dish_id]["recipe"].items():
            need[kind] = need.get(kind, 0) + n * dishes[dish_id]
    return dict(sorted(need.items()))


class DaySim:
    mode = "day"

    def __init__(self, tuning, scenario, streams, days=1):
        self.tuning = tuning
        self.streams = streams
        self.ids = IdAllocator()
        self.days = days
        d = scenario.get("day", {})
        self.money = d.get("money", 0)
        self.earned = d.get("earned", 0)
        self.reputation = d.get("reputation", tuning["quan"]["reputation_initial"])
        self.upgrades = dict(d.get("upgrades", {}))
        self.active_upgrades = {}
        self.plan = {p["day"]: {"day": p["day"], "dishes": dict(p["dishes"]), "ingredients": dict(p["ingredients"])}
                     for p in tuning["day_plan"]}
        for p in d.get("day_plan", []):
            self.plan[p["day"]] = {"day": p["day"], "dishes": dict(p["dishes"]),
                                   "ingredients": plan_ingredients(tuning["menu"], p["dishes"])}
        self.g_template = scenario.get("gather", {})
        self.q_template = scenario.get("quan", {})
        self.day = 0
        self.days_completed = 0
        self.sub = None
        self.phase = "gather"
        self.phase_tick = 0
        self.shop_left = 0
        self.leftover = {}
        self.done = False
        self.reason = None
        self.pending = []  # event tick 0 (day_start ...) — Session ghi trước snapshot tick 0
        self._start_day(self.pending)

    # --- dựng từng pha -------------------------------------------------------------------------
    def _level_value(self, uid):
        lv = self.active_upgrades.get(uid, 0)
        if lv <= 0:
            return None
        return self.tuning["shop"]["upgrades"][uid][lv - 1][UPGRADE_FIELD[uid]]

    def _emit(self, events, name, data, phase=None):
        events.append((name, data, phase or self.phase, self.day))

    def _start_day(self, events):
        self.day += 1
        self.active_upgrades = dict(self.upgrades)
        t = copy.deepcopy(self.tuning)
        t["gather"]["current_day"] = self.day
        for uid, field in UPGRADE_FIELD.items():
            v = self._level_value(uid)
            if v is not None:
                t["gather"][field] = v
        self.day_tuning = t
        self.phase = "gather"
        self.phase_tick = 0
        self._emit(events, "day_start", {})
        p = self.plan[self.day]
        self._emit(events, "day_plan", {"dishes": dict(p["dishes"]), "ingredients": dict(p["ingredients"])})
        self.sub = GatherSim(t, self._gather_template(), self.streams, self.ids)
        self._emit(events, "phase_start", {})

    def _gather_template(self):
        """v1.2: Ngày 1 giữ nguyên id trong mẫu gather.hold; Ngày kế cấp id mới (họ "I") theo thứ tự mảng,
        giữ kind/fresh ban đầu. Mẫu kiểu cũ (mảng kind) để nguyên cho gather tự xử lý."""
        g = copy.deepcopy(self.g_template)
        hold = g.get("hold")
        if isinstance(hold, list) and hold and isinstance(hold[0], dict):
            if self.day == 1:
                for it in hold:
                    self.ids.reserve(it["id"])
            else:
                g["hold"] = [dict(it, id=self.ids.new(PREFIX)) for it in hold]
        return g

    def _start_quan(self, events, inventory):
        """Bàn giao trong CÙNG tick: truyền nguyên list cá thể nội bộ (không làm tròn, không hao thêm)."""
        t = copy.deepcopy(self.day_tuning)
        dishes = self.plan[self.day]["dishes"]
        t["menu"] = {k: v for k, v in t["menu"].items() if k in dishes}
        q = QuanSim(t, copy.deepcopy(self.q_template), self.streams, self.ids, inventory=inventory)
        q.money, q.earned, q.reputation = self.money, self.earned, self.reputation
        self.sub = q
        self.phase = "quan"
        self.phase_tick = 0
        self._emit(events, "phase_start", {})

    def _start_shop(self, events):
        q = self.sub
        self.money, self.earned, self.reputation = q.money, q.earned, q.reputation
        if isinstance(q.stock, list):  # v1.2: kho dư là cá thể, Shop không hao tươi
            self.leftover = sort_by_id([dict(i) for i in q.stock])
        else:
            self.leftover = {k: v for k, v in sorted(q.stock.items()) if v > 0}
        self.sub = None
        self.phase = "shop"
        self.phase_tick = 0
        self.shop_left = self.tuning["shop"]["max_ticks"]
        self._emit(events, "phase_start", {})

    # --- bước -----------------------------------------------------------------------------------
    def step(self, inp):
        events = []
        self.phase_tick += 1
        if self.phase == "shop":
            self._step_shop(inp, events)
            return events
        for name, data in self.sub.step(inp):
            self._emit(events, name, data)
        if self.sub.done:
            if self.phase == "gather":
                self._start_quan(events, self.sub.inventory_items())
            else:
                self._start_shop(events)
        return events

    def _step_shop(self, inp, events):
        self.shop_left -= 1
        buy = getattr(inp, "buy", None)
        if buy is not None:
            self._buy(buy, events)
        if inp.pressed("shop_done"):
            self._close_shop("done", events)
        elif self.shop_left <= 0:
            self._close_shop("time", events)

    def _buy(self, action, events):
        levels = self.tuning["shop"]["upgrades"].get(action)
        if levels is None:
            self._emit(events, "buy_failed", {"action": action, "reason": "unknown"})
            return
        cur = self.upgrades.get(action, 0)
        if cur >= len(levels):
            self._emit(events, "buy_failed", {"action": action, "reason": "max_level"})
            return
        price = levels[cur]["price"]
        if self.money < price:
            self._emit(events, "buy_failed", {"action": action, "reason": "funds"})
            return
        self.money -= price
        self.upgrades[action] = cur + 1
        self._emit(events, "bought", {"upgrade": action, "level": cur + 1, "price": price, "money": self.money})

    def _close_shop(self, reason, events):
        self._emit(events, "shop_end", {"reason": reason})
        self.days_completed += 1
        self.leftover = {}
        if self.day >= self.days:
            self.done = True
            self.reason = "days_complete"
        else:
            self._start_day(events)

    # --- trạng thái đọc ra ------------------------------------------------------------------------
    @property
    def time_left_ticks(self):
        return self.shop_left if self.phase == "shop" else self.sub.time_left_ticks

    def live(self):
        """(money, earned, reputation) đang chạy: trong ca lấy từ sim con."""
        if self.phase == "quan" and self.sub is not None:
            return self.sub.money, self.sub.earned, self.sub.reputation
        return self.money, self.earned, self.reputation

    def snapshot(self) -> dict:
        p = self.plan[self.day]
        s = {"day": self.day, "day_plan": {"dishes": dict(p["dishes"]), "ingredients": dict(p["ingredients"])},
             "upgrades": dict(sorted(self.upgrades.items())),
             "active_upgrades": dict(sorted(self.active_upgrades.items())),
             "days_completed": self.days_completed}
        if self.phase == "shop":
            s["stock"] = list_to_json(self.leftover) if isinstance(self.leftover, list) else dict(self.leftover)
        else:
            s.update(self.sub.snapshot())
        return s


# --- scenario cho --mode day (Phương gửi quy tắc; dùng lại bộ kiểm gather/quan của Nga) -----------
def load_day_scenario(path, tuning):
    import json

    from ..errors import BadInput
    from ..scenario import GATHER_KEYS, QUAN_KEYS, _validate_gather, _validate_quan

    if path is None:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được scenario {path}: {e}")
    if not isinstance(data, dict) or not set(data) <= {"day", "gather", "quan"}:
        raise BadInput("scenario --mode day chỉ nhận khối day, gather, quan")
    for k, keys in (("gather", GATHER_KEYS), ("quan", QUAN_KEYS)):
        b = data.get(k, {})
        if not isinstance(b, dict) or set(b) - keys:
            raise BadInput(f"khối {k} sai hoặc có trường lạ")
    q = data.get("quan", {})
    if "stock" in q or "reputation" in q:
        raise BadInput("--mode day cấm quan.stock và quan.reputation (dùng gather.hold)")
    if "gather" in data:
        _validate_gather(data["gather"], tuning)
    d = data.get("day", {})
    if not isinstance(d, dict) or set(d) - {"money", "earned", "reputation", "upgrades", "day_plan"}:
        raise BadInput("khối day chỉ nhận money, earned, reputation, upgrades, day_plan")

    def _int(name, v):
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise BadInput(f"day.{name} phải là số nguyên ≥ 0")

    money, earned = d.get("money", 0), d.get("earned", 0)
    _int("money", money)
    _int("earned", earned)
    if ("money" in d) != ("earned" in d) and (money or earned):
        raise BadInput("day: khai cả money và earned khi có tiền đầu kỳ")
    if money > earned:
        raise BadInput("day: cần 0 ≤ money ≤ earned")
    if "reputation" in d:
        r, qt = d["reputation"], tuning["quan"]
        if isinstance(r, bool) or not isinstance(r, (int, float)) or not qt["reputation_min"] <= r <= qt["reputation_max"]:
            raise BadInput("day.reputation ngoài miền")
    ups = d.get("upgrades", {})
    shop = tuning["shop"]["upgrades"]
    if not isinstance(ups, dict):
        raise BadInput("day.upgrades phải là object")
    for uid, lv in ups.items():
        if uid not in shop:
            raise BadInput(f"day.upgrades.{uid} không hỗ trợ")
        _int(f"upgrades.{uid}", lv)
        if lv > len(shop[uid]):
            raise BadInput(f"day.upgrades.{uid} vượt cấp tối đa")
    plans = d.get("day_plan", [])
    if not isinstance(plans, list):
        raise BadInput("day.day_plan phải là mảng")
    seen = set()
    for p in plans:
        if not isinstance(p, dict) or set(p) - {"day", "dishes", "ingredients"} or "dishes" not in p:
            raise BadInput("day.day_plan[]: cần {day, dishes[, ingredients]}")
        if p.get("day") not in (1, 2, 3, 4, 5) or p["day"] in seen:
            raise BadInput("day.day_plan[].day phải là 1..5 và không trùng")
        seen.add(p["day"])
        dishes = p["dishes"]
        if not isinstance(dishes, dict) or not dishes or any(
                k not in tuning["menu"] or isinstance(n, bool) or not isinstance(n, int) or n <= 0
                for k, n in dishes.items()):
            raise BadInput("day.day_plan[].dishes phải là map id món → số nguyên dương")
        if "ingredients" in p and p["ingredients"] != plan_ingredients(tuning["menu"], dishes):
            raise BadInput("day.day_plan[].ingredients không khớp công thức × số suất")
    # quan template: kiểm bằng bộ kiểm của quán với kho rỗng tạm (kho thực kiểm lúc mở quán trong DaySim)
    if q:
        _validate_quan(dict(q), tuning)
    return data
