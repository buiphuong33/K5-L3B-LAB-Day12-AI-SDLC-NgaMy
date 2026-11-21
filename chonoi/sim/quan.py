"""Buổi tối — mô phỏng quán theo PRD-0, mục F."""

import math

from ..errors import BadInput
from ..ids import id_key, sort_by_id
from .ramp import ramp_velocity

TICK = 60.0


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None):
        self.t = tuning["quan"]
        self.menu = tuning["menu"]
        self.rng = streams
        self.ids = ids
        player = scenario.get("player", {})
        self.pos = [float(c) for c in player.get("pos", self.t["start_pos"])]
        self.vel = [float(c) for c in player.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
        self.hand = scenario.get("hand")
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(self.t["duration_s"] * TICK)))
        self._elapsed_ticks = 0
        self.reputation = scenario.get("reputation", self.t["reputation_initial"])
        self.stoves = self._merge(self.t["stoves"], scenario.get("stoves", []))
        for stove in self.stoves:
            stove.setdefault("state", "idle")
            stove.setdefault("dish", None)
            stove.setdefault("cook_ticks_left", 0)
            stove.setdefault("ready_ticks", 0)
        self.tables = self._merge(self.t["tables"], scenario.get("tables", []))
        self.customers = []
        self._reserved = {}
        missing_reservations = []
        for raw in scenario.get("customers", []):
            customer = dict(raw)
            customer.setdefault("state", "waiting")
            customer.setdefault("order_tick", 0)
            customer.setdefault("order_status", "reserved")
            customer.setdefault("patience_ticks_left", int(round(self.t["patience_s"] * TICK)))
            customer.setdefault("eat_ticks_left", 0)
            customer.setdefault("base_price", None)
            customer.setdefault("tip", None)
            if customer["order_status"] == "reserved" and "reserved" not in customer:
                missing_reservations.append(customer)
                customer["reserved"] = {}
            else:
                customer.setdefault("reserved", {})
                self._add_reservation(customer["reserved"])
            self.customers.append(customer)
            ids.reserve(customer["id"])
        for customer in sorted(missing_reservations,
                               key=lambda c: (c["order_tick"], id_key(c["table_id"]))):
            recipe = self.menu[customer["dish_id"]]["recipe"]
            if not all(self._available(kind) >= amount for kind, amount in recipe.items()):
                raise BadInput(f"khách {customer['id']}: giữ chỗ {customer['dish_id']} vượt kho")
            customer["reserved"] = dict(recipe)
            self._add_reservation(recipe)
        for kind, amount in self._reserved.items():
            if amount > self.stock.get(kind, 0):
                raise BadInput(f"customers giữ chỗ {kind} vượt kho")
        self.random_customers = scenario.get("random_customers", True)
        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    @staticmethod
    def _merge(defaults, updates):
        by_id = {item["id"]: dict(item) for item in defaults}
        for update in updates:
            if update["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {update['id']}")
            by_id[update["id"]].update(update)
        return sort_by_id(list(by_id.values()))

    def _add_reservation(self, reservation):
        for kind, amount in reservation.items():
            self._reserved[kind] = self._reserved.get(kind, 0) + amount

    def _available(self, kind):
        return self.stock.get(kind, 0) - self._reserved.get(kind, 0)

    def snapshot(self) -> dict:
        occupied = {customer["table_id"]: customer["id"] for customer in self.customers}
        return {
            "player": {"pos": self.pos, "vel": self.vel},
            "stock": {kind: self.stock[kind] for kind in sorted(self.stock) if self.stock[kind] > 0},
            "hand": self.hand,
            "stoves": [{key: stove.get(key) for key in
                        ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for stove in self.stoves],
            "tables": [{"id": table["id"], "pos": table["pos"],
                        "customer_id": occupied.get(table["id"])} for table in self.tables],
            "customers": sort_by_id(self.customers),
        }

    def step(self, inp):
        if self.done:
            return []
        events = []
        self._elapsed_ticks += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        ready_at_start = {stove["id"] for stove in self.stoves if stove["state"] == "ready"}
        self._advance_clocks(events, ready_at_start)
        self._move(inp)
        if inp.pressed("interact"):
            self._interact(events)
        closing = self.time_left_ticks == 0
        self._settle_customers(events, closing)
        if not closing and self.random_customers:
            first = int(self.t["first_customer_tick"])
            interval = max(1, int(round(self.t["customer_interval_s"] * TICK)))
            if self._elapsed_ticks >= first and (self._elapsed_ticks - first) % interval == 0:
                self._arrive_customer(events)
        if closing:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                         "shift_earned": self.shift_earned, "reputation": self.reputation}))
        return events

    def _advance_clocks(self, events, ready_at_start):
        for customer in self.customers:
            if customer["state"] == "eating":
                customer["eat_ticks_left"] = max(0, customer["eat_ticks_left"] - 1)
            elif customer["state"] == "waiting":
                customer["patience_ticks_left"] = max(0, customer["patience_ticks_left"] - 1)
        for stove in self.stoves:
            if stove["state"] == "cooking":
                stove["cook_ticks_left"] = max(0, stove["cook_ticks_left"] - 1)
                if stove["cook_ticks_left"] == 0:
                    stove["state"] = "ready"
                    stove["ready_ticks"] = 0
                    dish = stove["dish"]
                    events.append(("dish_ready", {"stove_id": stove["id"], "order_id": dish["order_id"],
                                                   "dish_id": dish["dish_id"]}))
            elif stove["state"] == "ready" and stove["id"] in ready_at_start:
                stove["ready_ticks"] += 1

    def _arrive_customer(self, events):
        occupied = {customer["table_id"] for customer in self.customers}
        free = [table for table in self.tables if table["id"] not in occupied]
        if not free:
            return
        available_dishes = [dish_id for dish_id in sorted(self.menu)
                            if all(self._available(kind) >= amount
                                   for kind, amount in self.menu[dish_id]["recipe"].items())]
        if not available_dishes:
            events.append(("no_dish", {}))
            return
        table = free[0]
        dish_id = self.rng.get("customer_dish").choice(available_dishes)
        recipe = dict(self.menu[dish_id]["recipe"])
        customer = {
            "id": self.ids.new("C"), "table_id": table["id"], "dish_id": dish_id,
            "order_tick": self._elapsed_ticks, "state": "waiting",
            "patience_ticks_left": int(round(self.t["patience_s"] * TICK)),
            "eat_ticks_left": 0, "order_status": "reserved", "reserved": recipe,
            "base_price": None, "tip": None,
        }
        self._add_reservation(recipe)
        self.customers.append(customer)
        events.append(("customer_arrived", {"order_id": customer["id"], "table_id": table["id"],
                                             "dish_id": dish_id}))

    def _interact(self, events):
        candidates = []
        for stove in self.stoves:
            distance = self._distance(stove["pos"])
            if distance <= self.t["interact_radius"]:
                candidates.append((distance, 0, stove["id"], "stove", stove))
        for table in self.tables:
            distance = self._distance(table["pos"])
            if distance <= self.t["interact_radius"]:
                candidates.append((distance, 1, table["id"], "table", table))
        if not candidates:
            return
        _, _, _, kind, target = min(candidates, key=lambda entry: entry[:3])
        if kind == "stove":
            self._interact_stove(target, events)
        else:
            self._interact_table(target, events)

    def _interact_stove(self, stove, events):
        if stove["state"] == "ready":
            if self.hand is None:
                dish = stove["dish"]
                self.hand = dish
                stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
                events.append(("dish_picked", {"stove_id": stove["id"], "order_id": dish["order_id"],
                                               "dish_id": dish["dish_id"]}))
            return
        if stove["state"] != "idle":
            return
        orders = sorted((customer for customer in self.customers
                         if customer["order_status"] == "reserved"),
                        key=lambda customer: (customer["order_tick"], id_key(customer["table_id"])))
        if not orders:
            return
        customer = orders[0]
        recipe = customer["reserved"]
        if any(self.stock.get(kind, 0) < amount for kind, amount in recipe.items()):
            return
        for kind, amount in recipe.items():
            self.stock[kind] -= amount
            self._reserved[kind] = max(0, self._reserved.get(kind, 0) - amount)
        dish_id = customer["dish_id"]
        base_price = self.menu[dish_id]["price"]
        dish = {"order_id": customer["id"], "dish_id": dish_id, "base_price": base_price}
        customer["reserved"] = {}
        customer["order_status"] = "assigned"
        customer["base_price"] = base_price
        cook_ticks = max(1, int(round(self.menu[dish_id]["cook_s"] * TICK)))
        stove.update(state="cooking", dish=dish, cook_ticks_left=cook_ticks, ready_ticks=0)
        events.append(("cook_started", {"stove_id": stove["id"], "order_id": customer["id"],
                                         "dish_id": dish_id, "items": sorted(
                                             kind for kind, amount in recipe.items() for _ in range(amount)),
                                         "base_price": base_price}))

    def _interact_table(self, table, events):
        if self.hand is None:
            return
        customer = next((item for item in self.customers
                         if item["table_id"] == table["id"] and item["id"] == self.hand["order_id"]), None)
        if customer is None or customer["order_status"] != "assigned":
            return
        dish = self.hand
        if dish["dish_id"] != customer["dish_id"]:
            return
        patience_max = int(round(self.t["patience_s"] * TICK))
        tip = (math.floor(dish["base_price"] * self.t["tip_rate"])
               if customer["patience_ticks_left"] / patience_max >= self.t["tip_min_patience_ratio"] else 0)
        self.hand = None
        customer["state"] = "eating"
        customer["order_status"] = "served"
        customer["eat_ticks_left"] = max(1, int(round(self.t["eat_s"] * TICK)))
        customer["reserved"] = {}
        customer["base_price"] = dish["base_price"]
        customer["tip"] = tip
        events.append(("served", {"order_id": customer["id"], "table_id": table["id"],
                                   "dish_id": dish["dish_id"],
                                   "patience_ticks_left": customer["patience_ticks_left"],
                                   "base_price": customer["base_price"], "tip": tip}))

    def _settle_customers(self, events, closing):
        for table in self.tables:
            customer = next((item for item in self.customers if item["table_id"] == table["id"]), None)
            if customer is None:
                continue
            if customer["state"] == "eating" and (closing or customer["eat_ticks_left"] == 0):
                self._pay(customer, "finished_eating" if customer["eat_ticks_left"] == 0 else "closing", events)
            elif customer["state"] == "waiting" and closing:
                self._remove_customer(customer)
                events.append(("customer_left", {"order_id": customer["id"], "table_id": table["id"],
                                                  "reason": "closing", "reputation": self.reputation}))
            elif customer["state"] == "waiting" and customer["patience_ticks_left"] == 0:
                self._change_reputation(self.t["left_reputation_delta"])
                self._remove_customer(customer)
                events.append(("customer_left", {"order_id": customer["id"], "table_id": table["id"],
                                                  "reason": "patience", "reputation": self.reputation}))

    def _pay(self, customer, reason, events):
        base_price = customer["base_price"]
        tip = customer["tip"]
        amount = base_price + tip
        self.money += amount
        self.earned += amount
        self.shift_earned += amount
        if tip > 0:
            self._change_reputation(self.t["tip_reputation"])
        table_id = customer["table_id"]
        order_id = customer["id"]
        self._remove_customer(customer)
        events.append(("paid", {"order_id": order_id, "table_id": table_id, "base_price": base_price,
                                 "tip": tip, "amount": amount, "reason": reason}))

    def _remove_customer(self, customer):
        self._release_reservation(customer)
        order_id = customer["id"]
        self.customers.remove(customer)
        for stove in self.stoves:
            dish = stove.get("dish")
            if dish is not None and dish["order_id"] == order_id:
                stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
        if self.hand is not None and self.hand["order_id"] == order_id:
            self.hand = None

    def _release_reservation(self, customer):
        for kind, amount in customer.get("reserved", {}).items():
            self._reserved[kind] = max(0, self._reserved.get(kind, 0) - amount)
        customer["reserved"] = {}

    def _change_reputation(self, delta):
        # làm tròn để cộng dồn số thực không làm floor(uy tín) hụt một bậc (1.9999... thay vì 2)
        self.reputation = min(self.t["reputation_max"],
                              max(self.t["reputation_min"], round(self.reputation + delta, 9)))

    def _distance(self, position):
        return math.hypot(self.pos[0] - position[0], self.pos[1] - position[1])

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        bounds = self.t["bounds"]
        for index, axis in enumerate(("x", "z")):
            self.pos[index] += self.vel[index] / TICK
            lo, hi = bounds[axis]
            if self.pos[index] <= lo:
                self.pos[index], self.vel[index] = lo, max(0.0, self.vel[index])
            elif self.pos[index] >= hi:
                self.pos[index], self.vel[index] = hi, min(0.0, self.vel[index])
