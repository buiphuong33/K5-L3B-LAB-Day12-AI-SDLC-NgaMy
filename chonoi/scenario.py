"""Nạp và kiểm scenario (Contract D), gồm mâu thuẫn luật trong dữ liệu quán."""

import json
import math

from .errors import BadInput
from .inventory import hold_to_items, validate_items

GATHER_KEYS = {"player", "hold", "nodes", "fish", "random_fish", "time_left_ticks", "monsters"}
GATHER_PLAYER_KEYS = {"pos", "vel", "heading_deg", "hp", "oxygen_ticks", "zero_oxy_ticks",
                      "invuln_ticks", "catch_cd_ticks", "attack_cd_ticks"}
QUAN_PLAYER_KEYS = {"pos", "vel"}
QUAN_KEYS = {"player", "stock", "hand", "stoves", "tables", "customers", "random_customers",
             "reputation", "time_left_ticks"}
DAY_KEYS = {"money", "earned", "reputation", "upgrades", "day_plan"}


def _check_ids(name, arr):
    if not isinstance(arr, list):
        raise BadInput(f"{name} phải là mảng")
    seen = set()
    for e in arr:
        if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"]:
            raise BadInput(f"{name}: mỗi phần tử cần id (chuỗi khác rỗng)")
        if e["id"] in seen:
            raise BadInput(f"{name}: id trùng {e['id']}")
        seen.add(e["id"])


def load_scenario(path, mode: str, tuning: dict) -> dict:
    if path is None:
        return {"day": {}, "gather": {}, "quan": {}} if mode == "day" else {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được scenario {path}: {e}")
    if not isinstance(data, dict):
        raise BadInput("scenario phải là object")
    if mode == "day":
        extra = set(data) - {"day", "gather", "quan"}
        if extra:
            raise BadInput(f"trường lạ trong scenario day: {sorted(extra)}")
        day = data.get("day", {})
        gather = data.get("gather", {})
        quan = data.get("quan", {})
        if not all(isinstance(block, dict) for block in (day, gather, quan)):
            raise BadInput("các khối day, gather, quan phải là object")
        gather_extra = set(gather) - GATHER_KEYS
        quan_extra = set(quan) - QUAN_KEYS
        if gather_extra:
            raise BadInput(f"trường lạ/chưa hỗ trợ trong gather: {sorted(gather_extra)}")
        if quan_extra:
            raise BadInput(f"trường lạ/chưa hỗ trợ trong quan: {sorted(quan_extra)}")
        _validate_day(day, tuning)
        _validate_time_left(gather, "gather", tuning)
        _validate_gather(gather, tuning)
        if "stock" in quan or "reputation" in quan:
            raise BadInput("mode day không nhận quan.stock hoặc quan.reputation")
        planned_dishes = _scenario_day_dishes(day, tuning)
        _validate_time_left(quan, "quan", tuning)
        _validate_quan(quan, tuning, menu_ids=set(planned_dishes))
        _validate_day_opening_stock(gather, quan, tuning)
        return {"day": day, "gather": gather, "quan": quan}
    if mode not in ("gather", "quan"):
        raise BadInput(f"mode scenario không hỗ trợ: {mode}")
    if not set(data) <= {mode}:
        raise BadInput(f"khối sai mode: chạy --mode {mode} chỉ nhận khối '{mode}'")
    block = data.get(mode, {})
    if not isinstance(block, dict):
        raise BadInput(f"khối {mode} phải là object")
    allowed = GATHER_KEYS if mode == "gather" else QUAN_KEYS
    extra = set(block) - allowed
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong {mode}: {sorted(extra)}")
    _validate_time_left(block, mode, tuning)
    if mode == "gather":
        _validate_gather(block, tuning)
    else:
        _validate_quan(block, tuning)
    return block


def _validate_time_left(block, mode, tuning):
    if "time_left_ticks" not in block:
        return
    dur = int(round(tuning[mode]["duration_s"] * 60))
    ticks = block["time_left_ticks"]
    if isinstance(ticks, bool) or not isinstance(ticks, int) or not (1 <= ticks <= dur):
        raise BadInput(f"time_left_ticks phải là số nguyên trong [1, {dur}]")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _nonneg_int(name, v):
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise BadInput(f"{name} phải là số nguyên không âm")


def _pos(name, pos, bounds, axes=("x", "d")):
    if not (isinstance(pos, list) and len(pos) == 2 and all(_num(c) for c in pos)):
        raise BadInput(f"{name} phải là [{axes[0]}, {axes[1]}]")
    for c, axis in zip(pos, axes):
        lo, hi = bounds[axis]
        if not (lo <= c <= hi):
            raise BadInput(f"{name} nằm ngoài vùng nước ({axis} ∈ [{lo}, {hi}])")


def _validate_gather(b, tuning):
    g = tuning["gather"]
    bounds = g["bounds"]
    ingredients = _ingredient_kinds(tuning)
    node_kinds = {node["kind"] for node in g.get("nodes", [])}
    fish_kinds = set(g.get("fish_yield", {}))
    node_keys = {"id", "kind", "pos", "regrow_ticks"}
    fish_keys = {"id", "kind", "pos", "heading_deg", "age_ticks"}
    for arr in ("nodes", "fish"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "random_fish" in b and not isinstance(b["random_fish"], bool):
        raise BadInput("random_fish phải là boolean")
    if "hold" in b:
        h = b["hold"]
        if not isinstance(h, list) or any(k not in ingredients for k in h):
            raise BadInput("hold phải là mảng id nguyên liệu hợp lệ")
        if len(h) > g["hold_capacity"]:
            raise BadInput("hold vượt sức chứa")
    p = b.get("player", {})
    if not isinstance(p, dict):
        raise BadInput("player phải là object")
    extra = set(p) - GATHER_PLAYER_KEYS
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong gather.player: {sorted(extra)}")
    if "pos" in p:
        _pos("player.pos", p["pos"], bounds)
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, d]")
    if "heading_deg" in p and not _num(p["heading_deg"]):
        raise BadInput("player.heading_deg phải là số")
    for key in ("invuln_ticks", "attack_cd_ticks", "catch_cd_ticks", "zero_oxy_ticks", "oxygen_ticks", "hp"):
        if key in p:
            _nonneg_int(f"player.{key}", p[key])
    omax = int(round(g["oxygen_max_s"] * 60))
    if "oxygen_ticks" in p and p["oxygen_ticks"] > omax:
        raise BadInput("player.oxygen_ticks vượt oxy tối đa")
    if "hp" in p and not (1 <= p["hp"] <= g["hp_max"]):
        raise BadInput("player.hp phải trong [1, hp_max]")
    if "zero_oxy_ticks" in p:
        pos = p.get("pos", g["start_pos"])
        oxy = p.get("oxygen_ticks", omax)
        if p["zero_oxy_ticks"] > 59:
            raise BadInput("player.zero_oxy_ticks phải trong [0, 59]")
        if p["zero_oxy_ticks"] > 0 and not (oxy == 0 and pos[1] > g["surface_depth"]):
            raise BadInput("player.zero_oxy_ticks > 0 chỉ khi oxy = 0 và đang dưới nước")
    for n in b.get("nodes", []):
        extra = set(n) - node_keys
        if extra:
            raise BadInput(f"nodes.{n['id']}: trường lạ {sorted(extra)}")
        if n.get("kind") not in node_kinds:
            raise BadInput(f"nodes.{n['id']}: kind phải là một trong {sorted(node_kinds)}")
        _pos(f"nodes.{n['id']}.pos", n.get("pos"), bounds)
        if n["pos"][1] != 0:
            raise BadInput(f"nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
        if "regrow_ticks" in n:
            _nonneg_int(f"nodes.{n['id']}.regrow_ticks", n["regrow_ticks"])
    for f in b.get("fish", []):
        extra = set(f) - fish_keys
        if extra:
            raise BadInput(f"fish.{f['id']}: trường lạ {sorted(extra)}")
        if f.get("kind") not in fish_kinds:
            raise BadInput(f"fish.{f['id']}: kind phải là một trong {sorted(fish_kinds)}")
        _pos(f"fish.{f['id']}.pos", f.get("pos"), bounds)
        if f["pos"][1] <= g["surface_depth"]:
            raise BadInput(f"fish.{f['id']}: đàn cá phải ở dưới nước")
        if "heading_deg" in f and not _num(f["heading_deg"]):
            raise BadInput(f"fish.{f['id']}.heading_deg phải là số")
        if "age_ticks" in f:
            _nonneg_int(f"fish.{f['id']}.age_ticks", f["age_ticks"])
    if "monsters" in b:
        _validate_monsters(b["monsters"], g, bounds)


def _validate_monsters(monsters, gather_tuning, bounds):
    _check_ids("monsters", monsters)
    config = gather_tuning.get("monsters")
    if not isinstance(config, dict) or not isinstance(config.get("species"), dict):
        raise BadInput("tuning.gather.monsters.species thiếu hoặc sai schema")
    species = config["species"]
    fields = {"id", "kind", "pos", "waypoints", "target_idx", "state", "state_ticks_left", "recoil_dir"}
    for monster in monsters:
        extra = set(monster) - fields
        if extra:
            raise BadInput(f"monsters.{monster['id']}: trường lạ {sorted(extra)}")
        kind = monster.get("kind")
        if kind not in species:
            raise BadInput(f"monsters.{monster['id']}: kind không có trong tuning")
        setting = species[kind]
        depths = setting.get("depths")
        if not (isinstance(depths, list) and len(depths) == 2 and all(_num(v) for v in depths)
                and depths[0] <= depths[1]):
            raise BadInput(f"tuning species {kind}.depths không hợp lệ")
        _pos(f"monsters.{monster['id']}.pos", monster.get("pos"), bounds, axes=("x", "d"))
        if not depths[0] <= monster["pos"][1] <= depths[1]:
            raise BadInput(f"monsters.{monster['id']}.pos ngoài dải độ sâu của loài")
        waypoints = monster.get("waypoints")
        if not isinstance(waypoints, list) or len(waypoints) != 2:
            raise BadInput(f"monsters.{monster['id']}.waypoints cần đúng hai điểm")
        for index, waypoint in enumerate(waypoints):
            _pos(f"monsters.{monster['id']}.waypoints[{index}]", waypoint, bounds, axes=("x", "d"))
            if not depths[0] <= waypoint[1] <= depths[1]:
                raise BadInput(f"monsters.{monster['id']}.waypoints[{index}] ngoài dải độ sâu của loài")
        target = monster.get("target_idx", 1)
        if isinstance(target, bool) or not isinstance(target, int) or target not in (0, 1):
            raise BadInput(f"monsters.{monster['id']}.target_idx phải là 0 hoặc 1")
        state = monster.get("state", "patrol")
        if state not in {"patrol", "chase", "recoil", "stunned"}:
            raise BadInput(f"monsters.{monster['id']}.state không hợp lệ")
        timer = monster.get("state_ticks_left", 0)
        _nonneg_int(f"monsters.{monster['id']}.state_ticks_left", timer)
        if state in {"recoil", "stunned"} and timer <= 0:
            raise BadInput(f"monsters.{monster['id']}: recoil/stunned cần timer dương")
        direction = monster.get("recoil_dir")
        if state == "recoil":
            if not (isinstance(direction, list) and len(direction) == 2 and all(_num(v) for v in direction)
                    and math.isclose(math.hypot(*direction), 1.0, abs_tol=1e-6)):
                raise BadInput(f"monsters.{monster['id']}.recoil_dir phải là vector đơn vị")
        elif direction is not None:
            raise BadInput(f"monsters.{monster['id']}.recoil_dir chỉ dùng khi state=recoil")


def _validate_quan(b, tuning, menu_ids=None):
    q = tuning["quan"]
    full_menu = tuning["menu"]
    if menu_ids is None:
        menu = full_menu
    else:
        unknown_menu = set(menu_ids) - set(full_menu)
        if unknown_menu:
            raise BadInput(f"day_plan chứa món không có trong menu: {sorted(unknown_menu)}")
        menu = {dish_id: full_menu[dish_id] for dish_id in sorted(menu_ids)}
    ingredients = _ingredient_kinds(tuning)
    for arr in ("stoves", "tables", "customers"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "stock" in b:
        validate_items(b["stock"], ingredients)
    p = b.get("player", {})
    if not isinstance(p, dict) or set(p) - QUAN_PLAYER_KEYS:
        raise BadInput("quan.player chỉ có pos và vel")
    qb = tuning["quan"]["bounds"]
    if "pos" in p:
        _pos("player.pos", p["pos"], qb, axes=("x", "z"))
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, z]")
    def merged(defaults, updates, kind):
        values = {item["id"]: dict(item) for item in defaults}
        for item in updates:
            if item["id"] not in values:
                raise BadInput(f"id {kind} không tồn tại: {item['id']}")
            values[item["id"]].update(item)
        return values

    tables = merged(q["tables"], b.get("tables", []), "bàn")
    stoves = merged(q["stoves"], b.get("stoves", []), "bếp")
    known = set(tables)
    table_keys = {"id", "pos"}
    stove_keys = {"id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks"}
    customer_keys = {"id", "table_id", "dish_id", "order_tick", "state", "patience_ticks_left",
                     "eat_ticks_left", "order_status", "reserved", "base_price", "tip"}
    for group, objects, allowed in (("tables", tables.values(), table_keys),
                                    ("stoves", stoves.values(), stove_keys)):
        for e in objects:
            extra = set(e) - allowed
            if extra:
                raise BadInput(f"{group}.{e['id']}: trường lạ {sorted(extra)}")
            _pos(f"{group}.{e['id']}.pos", e.get("pos"), qb, axes=("x", "z"))
    occupied = set()
    customers = {}
    payloads = {}
    for c in b.get("customers", []):
        extra = set(c) - customer_keys
        if extra:
            raise BadInput(f"customers.{c['id']}: trường lạ {sorted(extra)}")
        if not isinstance(c.get("table_id"), str) or c["table_id"] not in known:
            raise BadInput(f"customers.{c['id']}: table_id phải là bàn có thật")
        if c["table_id"] in occupied:
            raise BadInput("hai khách cùng bàn")
        occupied.add(c["table_id"])
        customers[c["id"]] = c
        state = c.get("state", "waiting")
        status = c.get("order_status", "reserved")
        if state not in {"waiting", "eating"}:
            raise BadInput(f"customers.{c['id']}: state không hợp lệ")
        if status not in {"reserved", "assigned", "unfulfillable", "served"}:
            raise BadInput(f"customers.{c['id']}: order_status không hợp lệ")
        if "order_tick" in c:
            _nonneg_int(f"customers.{c['id']}.order_tick", c["order_tick"])
        if "patience_ticks_left" in c:
            _nonneg_int(f"customers.{c['id']}.patience_ticks_left", c["patience_ticks_left"])
            if c["patience_ticks_left"] > int(round(q["patience_s"] * 60)):
                raise BadInput(f"customers.{c['id']}.patience_ticks_left vượt mức tối đa")
        if "eat_ticks_left" in c:
            _nonneg_int(f"customers.{c['id']}.eat_ticks_left", c["eat_ticks_left"])
            if c["eat_ticks_left"] > int(round(q["eat_s"] * 60)):
                raise BadInput(f"customers.{c['id']}.eat_ticks_left vượt mức tối đa")
        dish_id = c.get("dish_id")
        if status in {"reserved", "assigned", "served"}:
            if not isinstance(dish_id, str) or dish_id not in menu:
                raise BadInput(f"customers.{c['id']}: {status} cần dish_id hợp lệ")
        elif dish_id is not None:
            raise BadInput(f"customers.{c['id']}: đơn unfulfillable không có món")
        if "reserved" in c:
            validate_items(c["reserved"], ingredients)
        reserve = c.get("reserved")
        if status == "reserved":
            if reserve is not None and reserve != menu[dish_id]["recipe"]:
                raise BadInput(f"customers.{c['id']}.reserved khác công thức")
        elif reserve not in (None, {}):
            raise BadInput(f"customers.{c['id']}: đơn {status} phải nhả giữ chỗ")
        if status == "unfulfillable" and (state != "waiting" or c.get("reserved", {}) != {}):
            raise BadInput(f"customers.{c['id']}: unfulfillable phải chờ và không giữ nguyên liệu")
        if status == "served":
            if state != "eating" or c.get("eat_ticks_left", 0) <= 0:
                raise BadInput(f"customers.{c['id']}: served cần state eating và timer ăn dương")
            if not _int_price(c.get("base_price")) or not _int_price(c.get("tip"), allow_zero=True):
                raise BadInput(f"customers.{c['id']}: eating cần base_price và tip")
            if c["base_price"] != menu[dish_id]["price"]:
                raise BadInput(f"customers.{c['id']}: base_price khác giá món")
            max_tip = int(c["base_price"] * q["tip_rate"])
            if c["tip"] not in {0, max_tip}:
                raise BadInput(f"customers.{c['id']}: tip không khớp contract")
        elif state == "eating":
            raise BadInput(f"customers.{c['id']}: eating phải có order_status served")
        if status == "reserved" and state != "waiting":
            raise BadInput(f"customers.{c['id']}: reserved phải ở state waiting")
        if status == "assigned" and state != "waiting":
            raise BadInput(f"customers.{c['id']}: assigned phải ở state waiting")
        if status == "assigned" and c.get("base_price") != menu[dish_id]["price"]:
            raise BadInput(f"customers.{c['id']}: assigned cần base_price theo món")
        if status in {"reserved", "assigned", "unfulfillable"} and c.get("eat_ticks_left", 0) != 0:
            raise BadInput(f"customers.{c['id']}: đơn chưa served không có timer ăn")
    for stove_id, s in stoves.items():
        state = s.get("state", "idle")
        if state not in {"idle", "cooking", "ready"}:
            raise BadInput(f"stoves.{stove_id}: state không hợp lệ")
        for key in ("cook_ticks_left", "ready_ticks"):
            if key in s:
                _nonneg_int(f"stoves.{stove_id}.{key}", s[key])
        dish = s.get("dish")
        if state == "idle":
            if dish is not None or s.get("cook_ticks_left", 0) != 0 or s.get("ready_ticks", 0) != 0:
                raise BadInput(f"stoves.{stove_id}: bếp idle không có món/timer nấu")
        elif state in {"cooking", "ready"}:
            if not isinstance(dish, dict) or set(dish) != {"order_id", "dish_id", "base_price"}:
                raise BadInput(f"stoves.{stove_id}.dish phải là payload món")
            _validate_dish_payload(f"stoves.{stove_id}.dish", dish, menu)
            if state == "cooking" and not (1 <= s.get("cook_ticks_left", 0) <= int(round(menu[dish["dish_id"]]["cook_s"] * 60))):
                raise BadInput(f"stoves.{stove_id}: cooking cần timer dương hợp lệ")
            if state == "cooking" and s.get("ready_ticks", 0) != 0:
                raise BadInput(f"stoves.{stove_id}: cooking có ready_ticks = 0")
            if state == "ready" and s.get("cook_ticks_left", 0) != 0:
                raise BadInput(f"stoves.{stove_id}: ready có cook_ticks_left = 0")
            payloads.setdefault(dish["order_id"], []).append(("stove", stove_id, dish))
    hand = b.get("hand")
    if hand is not None:
        if not isinstance(hand, dict) or set(hand) != {"order_id", "dish_id", "base_price"}:
            raise BadInput("hand phải là payload món hoặc null")
        _validate_dish_payload("hand", hand, menu)
        payloads.setdefault(hand["order_id"], []).append(("hand", None, hand))
    for order_id, held in payloads.items():
        c = customers.get(order_id)
        if c is None or c.get("order_status", "reserved") != "assigned" or len(held) != 1:
            raise BadInput(f"payload đơn {order_id} không có đúng một đơn assigned")
        dish = held[0][2]
        if dish["dish_id"] != c.get("dish_id") or dish["base_price"] != menu[c["dish_id"]]["price"]:
            raise BadInput(f"payload đơn {order_id} không khớp khách")
    for c in b.get("customers", []):
        status = c.get("order_status", "reserved")
        held = payloads.get(c["id"], [])
        if status == "assigned" and len(held) != 1:
            raise BadInput(f"customers.{c['id']}: đơn assigned phải có đúng một món ở bếp hoặc tay")
        if status != "assigned" and held:
            raise BadInput(f"customers.{c['id']}: đơn {status} không được có món đang giữ")
    if "stock" in b:
        reserved_totals = {}
        for c in b.get("customers", []):
            if c.get("order_status", "reserved") != "reserved":
                continue
            if "reserved" not in c:
                continue
            reserved = c["reserved"]
            for kind, amount in reserved.items():
                reserved_totals[kind] = reserved_totals.get(kind, 0) + amount
        for kind, amount in reserved_totals.items():
            if amount > b["stock"].get(kind, 0):
                raise BadInput(f"customers giữ chỗ {kind} vượt kho")
    if "random_customers" in b and not isinstance(b["random_customers"], bool):
        raise BadInput("random_customers phải là boolean")
    if "reputation" in b and (not _num(b["reputation"]) or not q["reputation_min"] <= b["reputation"] <= q["reputation_max"]):
        raise BadInput("reputation nằm ngoài giới hạn contract")


def _ingredient_kinds(tuning):
    return {kind for dish in tuning.get("menu", {}).values()
            for kind in dish.get("recipe", {})}


def _validate_day(day, tuning):
    extra = set(day) - DAY_KEYS
    if extra:
        raise BadInput(f"day: trường lạ {sorted(extra)}")
    if "money" in day:
        _nonneg_int("day.money", day["money"])
    if "earned" in day:
        _nonneg_int("day.earned", day["earned"])
    money, earned = day.get("money", 0), day.get("earned", 0)
    if money > earned:
        raise BadInput("day.money không thể lớn hơn day.earned")
    if (money > 0 or earned > 0) and not {"money", "earned"} <= set(day):
        raise BadInput("khi có tiền đầu kỳ cần khai cả day.money và day.earned")
    quan = tuning.get("quan", {})
    if "reputation" in day and (not _num(day["reputation"]) or
                                  not quan.get("reputation_min", 0) <= day["reputation"] <=
                                  quan.get("reputation_max", 5)):
        raise BadInput("day.reputation nằm ngoài giới hạn contract")
    if "upgrades" in day:
        upgrades = day["upgrades"]
        shop = tuning.get("shop")
        if not isinstance(upgrades, dict) or not isinstance(shop, dict) or not isinstance(shop.get("upgrades"), dict):
            raise BadInput("day.upgrades cần map theo tuning.shop.upgrades")
        unknown = set(upgrades) - set(shop["upgrades"])
        if unknown:
            raise BadInput(f"upgrade không có trong contract: {sorted(unknown)}")
        for name, level in upgrades.items():
            _nonneg_int(f"day.upgrades.{name}", level)
            entries = shop["upgrades"][name]
            max_level = max((entry.get("level", 0) for entry in entries), default=0)
            if level > max_level:
                raise BadInput(f"day.upgrades.{name} vượt cấp tối đa {max_level}")
    if "day_plan" in day:
        overrides = day["day_plan"]
        if not isinstance(overrides, dict):
            raise BadInput("day.day_plan phải là map số Ngày → kế hoạch")
        base = _contract_day_plans(tuning)
        valid_days = {str(day_no) for day_no in base}
        for day_no, plan in overrides.items():
            if day_no not in valid_days:
                raise BadInput(f"day.day_plan có ngày không hợp lệ: {day_no}")
            _validate_plan_entry(f"day.day_plan.{day_no}", plan, tuning)
            if "day" in plan and plan["day"] != int(day_no):
                raise BadInput(f"day.day_plan.{day_no}.day không khớp khóa ngày")


def _contract_day_plans(tuning):
    plans = tuning.get("day_plan")
    if not isinstance(plans, list) or len(plans) != 5:
        raise BadInput("tuning.day_plan phải có đủ 5 kế hoạch ngày")
    out = {}
    for plan in plans:
        if not isinstance(plan, dict):
            raise BadInput("tuning.day_plan: mỗi kế hoạch phải là object")
        day_no = plan.get("day")
        if isinstance(day_no, bool) or not isinstance(day_no, int) or day_no < 1 or day_no in out:
            raise BadInput("tuning.day_plan.day phải là số Ngày nguyên dương duy nhất")
        _validate_plan_entry(f"tuning.day_plan.{day_no}", plan, tuning)
        out[day_no] = plan
    if set(out) != {1, 2, 3, 4, 5}:
        raise BadInput("tuning.day_plan phải khai báo đủ Ngày 1 đến Ngày 5")
    return out


def _validate_plan_entry(name, plan, tuning):
    if not isinstance(plan, dict) or set(plan) - {"day", "dishes", "ingredients"}:
        raise BadInput(f"{name} chỉ nhận day, dishes, ingredients")
    dishes = plan.get("dishes")
    menu = tuning.get("menu", {})
    if not isinstance(dishes, dict) or not dishes:
        raise BadInput(f"{name}.dishes phải là map món không rỗng")
    ingredients = {}
    for dish_id, servings in dishes.items():
        if dish_id not in menu:
            raise BadInput(f"{name}.dishes chứa món ngoài menu: {dish_id}")
        if isinstance(servings, bool) or not isinstance(servings, int) or servings <= 0:
            raise BadInput(f"{name}.dishes.{dish_id} phải là số nguyên dương")
        for kind, amount in menu[dish_id]["recipe"].items():
            ingredients[kind] = ingredients.get(kind, 0) + amount * servings
    declared = plan.get("ingredients")
    if declared is not None:
        if not isinstance(declared, dict):
            raise BadInput(f"{name}.ingredients phải là map nguyên liệu")
        validate_items(declared, _ingredient_kinds(tuning))
        if declared != ingredients:
            raise BadInput(f"{name}.ingredients không khớp tổng công thức × số suất")


def _scenario_day_dishes(day, tuning):
    plans = _contract_day_plans(tuning)
    plan = day.get("day_plan", {}).get("1", plans[1])
    return plan["dishes"]


def _validate_day_opening_stock(gather, quan, tuning):
    """Check that opening gather hold can cover reserved evening orders."""
    stock = hold_to_items(gather.get("hold", []))
    menu = tuning["menu"]
    required = {}
    for customer in quan.get("customers", []):
        if customer.get("order_status", "reserved") != "reserved":
            continue
        dish_id = customer.get("dish_id")
        reserve = customer.get("reserved", menu[dish_id]["recipe"])
        for kind, amount in reserve.items():
            required[kind] = required.get(kind, 0) + amount
    for kind, amount in required.items():
        if amount > stock.get(kind, 0):
            raise BadInput(f"day opening: khách giữ {kind} vượt gather.hold")


def _int_price(value, allow_zero=False):
    return (isinstance(value, int) and not isinstance(value, bool) and
            value >= (0 if allow_zero else 1))


def _validate_dish_payload(name, value, menu):
    if not isinstance(value.get("order_id"), str) or not value["order_id"]:
        raise BadInput(f"{name}.order_id phải là id khách")
    dish_id = value.get("dish_id")
    if dish_id not in menu:
        raise BadInput(f"{name}.dish_id không có trong menu")
    if not _int_price(value.get("base_price")) or value["base_price"] != menu[dish_id]["price"]:
        raise BadInput(f"{name}.base_price khác giá món trong contract")
