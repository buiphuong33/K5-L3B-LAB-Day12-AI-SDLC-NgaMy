"""Vòng tick (Contract B, mô hình tick). KHUNG — thường không cần sửa.

Thứ tự ghi: snapshot tick 0 -> với mỗi bước: sự kiện (theo thứ tự xử lý) rồi snapshot (nếu tới lượt
hoặc buổi kết thúc) -> dòng 'end'. Mỗi tick tối đa một snapshot.

`Session` là API bước tick gọn dùng chung cho headless (`run`) và cửa sổ chơi trực tiếp (`chonoi.live`):
cả hai chạy CÙNG một lớp sim, không nhân đôi logic.
"""

import math

from .ids import IdAllocator
from .inputs import InputPlayer
from .inventory import write_inventory
from .items import reserve_ids
from .jsonl import JsonlWriter
from .rng import Streams
from .sim.gather import GatherSim
from .sim.quan import QuanSim
from .sim.day import DaySim


def build_sim(mode, tuning, scenario, seed, inventory, days=1):
    streams, ids = Streams(seed), IdAllocator()
    if mode == "gather":
        return GatherSim(tuning, scenario, streams, ids)
    if mode == "day":
        return DaySim(tuning, scenario, streams, days)
    if isinstance(inventory, list):  # v1.2: kho cá thể → id mới nối sau hậu tố lớn nhất đã nạp
        reserve_ids(ids, inventory)
    return QuanSim(tuning, scenario, streams, ids, inventory=inventory)


def _live(sim):
    return sim.live() if hasattr(sim, "live") else (sim.money, sim.earned, sim.reputation)


def _score(sim, tuning):
    _, earned, rep = _live(sim)
    return earned + tuning["score"]["reputation_multiplier"] * math.floor(rep)


class Session:
    """Một lượt chơi: dựng sim, bước từng tick, lấy snapshot / dòng end.

    v1.1: pause ở cả ba mode. Bước vào pause chỉ tăng `tick` (bước ngoài) và phát `paused`;
    khi đang pause bỏ qua mọi hành động; cạnh pause kế tiếp phát `resumed` rồi chạy gameplay ngay bước đó.
    """

    def __init__(self, mode, tuning, scenario, seed, inventory=None, days=1):
        self.mode = mode
        self.tuning = tuning
        self.sim = build_sim(mode, tuning, scenario, seed, inventory, days)
        self.tick = 0
        self.sim_tick = 0
        self.paused = False
        self.phase_changed = False

    @property
    def done(self) -> bool:
        return self.sim.done

    @property
    def phase_tick(self):
        return self.sim.phase_tick if self.mode == "day" else self.sim_tick

    def _row(self, name, data, phase=None, day=None):
        r = {"type": "event", "tick": self.tick, "phase": phase or self.sim.phase}
        if self.mode == "day":
            r["day"] = self.sim.day if day is None else day
        r.update({"name": name, "data": data})
        return r

    def initial_events(self) -> list:
        """Event tick 0 (day_start, day_plan, phase_start) — ghi trước snapshot tick 0."""
        pend = getattr(self.sim, "pending", [])
        rows = [self._row(n, d, ph, dy) for n, d, ph, dy in pend]
        pend.clear()
        return rows

    def snapshot(self) -> dict:
        sim = self.sim
        money, earned, rep = _live(sim)
        state = "finished" if sim.done else ("paused" if self.paused else "playing")
        s = {"type": "snapshot", "tick": self.tick, "sim_tick": self.sim_tick, "mode": self.mode,
             "phase": sim.phase, "phase_tick": self.phase_tick, "state": state,
             "time_left_ticks": sim.time_left_ticks, "money": money, "earned": earned,
             "reputation": rep, "score": _score(sim, self.tuning)}
        s.update(sim.snapshot())
        return s

    def step(self, inp) -> list:
        """Chạy một bước với `inp` (chonoi.inputs.InputState); trả các dòng event (tick = k + 1)."""
        self.tick += 1
        rows = []
        self.phase_changed = False
        if inp.pressed("pause"):
            if not self.paused:
                self.paused = True
                return [self._row("paused", {})]
            self.paused = False
            rows.append(self._row("resumed", {}))
        elif self.paused:
            return rows
        before = (self.sim.phase, getattr(self.sim, "day", 0))
        events = self.sim.step(inp)
        self.sim_tick += 1
        for ev in events:
            rows.append(self._row(*ev) if len(ev) == 4 else self._row(ev[0], ev[1]))
        self.phase_changed = before != (self.sim.phase, getattr(self.sim, "day", 0))
        return rows

    def end_row(self) -> dict:
        sim = self.sim
        money, earned, rep = _live(sim)
        r = {"type": "end", "ticks": self.tick, "sim_tick": self.sim_tick, "mode": self.mode,
             "state": "finished" if sim.done else ("paused" if self.paused else "playing"),
             "reason": sim.reason if sim.done else "tick_limit",
             "money": money, "earned": earned, "reputation": rep, "score": _score(sim, self.tuning)}
        if self.mode == "day":
            r["days_completed"] = sim.days_completed
        return r

    def write_inventory_if_done(self, inventory_out):
        """File kho: ghi MỘT lần khi có gather_end; chưa kết thúc thì giữ nguyên file đích."""
        if self.mode == "gather" and self.sim.done and inventory_out:
            write_inventory(inventory_out, self.sim.inventory_items())


def run(mode, tuning, scenario, seed, frames, ticks, out_path, snapshot_every, inventory=None, inventory_out=None,
        days=1):
    sess = Session(mode, tuning, scenario, seed, inventory, days)
    player = InputPlayer(frames)
    w = JsonlWriter(out_path)
    try:
        for row in sess.initial_events():
            w.write(row)
        w.write(sess.snapshot())  # tick 0: sau khi dựng scenario, trước mọi input
        last_snapped = 0
        while sess.tick < ticks and not sess.done:
            inp = player.advance(sess.tick)  # bước k đọc input có tick == k
            for row in sess.step(inp):
                w.write(row)
            if sess.tick % snapshot_every == 0 or sess.done or sess.phase_changed:
                w.write(sess.snapshot())
                last_snapped = sess.tick
        if last_snapped != sess.tick:
            w.write(sess.snapshot())
        w.write(sess.end_row())
    finally:
        w.close()
    sess.write_inventory_if_done(inventory_out)
    return sess.sim
