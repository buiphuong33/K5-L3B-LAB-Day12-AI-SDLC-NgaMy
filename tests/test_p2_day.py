"""Phase 2 — lát 4: vòng ngày, Shop, pause (chủ: Phương). Chạy hộp đen qua headless_cmd."""

import unittest

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

DOCK_NOW = {"gather": {"random_fish": False}, "quan": {"random_customers": False}}
GATHER_TICKS = 1            # interact ở tick 0 trong bến → docked
QUAN_TICKS = 180 * 60
SHOP_OPEN = GATHER_TICKS + QUAN_TICKS   # tick phase_start(shop)


def day_run(w, scenario, inputs, days=1, ticks=40000, name="d"):
    sc = write_json(w.path(name + "-sc.json"), scenario)
    ip = write_json(w.path(name + "-in.json"), inputs)
    out = w.path(name + ".jsonl")
    args = ["--mode", "day", "--seed", "7", "--scenario", sc, "--inputs", ip, "--ticks", str(ticks), "--out", out]
    if days != 1:
        args += ["--days", str(days)]
    code, err = run_headless(*args)
    return code, err, out


class DayLoop(unittest.TestCase):
    def test_p2_day_01_phase_order_and_plan(self):
        """AC: day_start → day_plan → phase_start(gather) ở tick 0; gather_end → phase_start(quan) cùng tick."""
        with Workdir() as w:
            code, err, out = day_run(w, DOCK_NOW, frames({"tick": 0, "interact": True}))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(out)
            ev = [r for r in rows if r["type"] == "event"]
            self.assertEqual([e["name"] for e in ev[:3]], ["day_start", "day_plan", "phase_start"])
            self.assertTrue(all(e["tick"] == 0 and e["day"] == 1 for e in ev[:3]))
            self.assertEqual(ev[1]["data"], {"dishes": {"ca_loc_nuong_trui": 3, "goi_bong_sung": 3},
                                             "ingredients": {"bong_sung": 6, "ca_loc": 3}})
            ge = events(rows, "gather_end")[0]
            ps = [e for e in events(rows, "phase_start") if e["phase"] == "quan"][0]
            self.assertEqual(ge["tick"], ps["tick"])
            self.assertEqual(ge["phase"], "gather")
            end = rows[-1]
            self.assertEqual((end["reason"], end["days_completed"]), ("days_complete", 1))
            self.assertLessEqual(end["ticks"], 22200)

    def test_p2_day_02_plans_d1_to_d5(self):
        with Workdir() as w:
            fr = [{"tick": 0, "interact": True}]
            code, err, out = day_run(w, DOCK_NOW, frames(*fr), days=5, ticks=200000)
            self.assertEqual(code, 0, err)
            rows = read_jsonl(out)
            plans = [e["data"]["ingredients"] for e in events(rows, "day_plan")]
            self.assertEqual(len(plans), 5)
            self.assertEqual([sum(p.values()) for p in plans], [9, 10, 12, 9, 10])
            self.assertEqual(rows[-1]["days_completed"], 5)

    def test_p2_day_03_buy_applies_next_day(self):
        """AC: mua oxygen ở Shop Ngày 1 → upgrades ngay, active_upgrades và oxy 45 s từ Ngày 2."""
        with Workdir() as w:
            sc = dict(DOCK_NOW, day={"money": 450, "earned": 450})
            fr = frames({"tick": 0, "interact": True}, {"tick": 1, "interact": False},
                        {"tick": SHOP_OPEN + 1, "buy": "oxygen"}, {"tick": SHOP_OPEN + 2, "buy": "oxygen"},
                        {"tick": SHOP_OPEN + 3, "buy": "hp"}, {"tick": SHOP_OPEN + 4, "buy": "laser"},
                        {"tick": SHOP_OPEN + 5, "shop_done": True})
            code, err, out = day_run(w, sc, fr, days=2)
            self.assertEqual(code, 0, err)
            rows = read_jsonl(out)
            self.assertEqual(events(rows, "bought")[0]["data"], {"upgrade": "oxygen", "level": 1, "price": 200, "money": 250})
            self.assertEqual([e["data"]["reason"] for e in events(rows, "buy_failed")], ["funds", "unknown"])
            self.assertEqual(events(rows, "bought")[1]["data"]["money"], 0)
            self.assertEqual(events(rows, "shop_end")[0]["data"], {"reason": "done"})
            d2 = [s for s in snapshots(rows) if s.get("day") == 2 and s["phase"] == "gather"][0]
            self.assertEqual(d2["phase_tick"], 0)
            self.assertEqual(d2["active_upgrades"], {"hp": 1, "oxygen": 1})
            self.assertEqual(d2["player"]["oxygen_max_ticks"], 2700)
            self.assertEqual(d2["player"]["hp_max"], 4)
            d1 = [s for s in snapshots(rows) if s.get("day") == 1 and s["phase"] == "shop"][-1]
            self.assertEqual(d1["active_upgrades"], {})
            self.assertEqual(rows[-1]["earned"], 450)

    def test_p2_day_04_shop_timeout(self):
        with Workdir() as w:
            code, err, out = day_run(w, DOCK_NOW, frames({"tick": 0, "interact": True}))
            rows = read_jsonl(out)
            se = events(rows, "shop_end")[0]
            self.assertEqual((se["data"]["reason"], se["tick"]), ("time", SHOP_OPEN + 600))

    def test_p2_day_05_pause_freezes_sim(self):
        with Workdir() as w:
            fr = frames({"tick": 0, "interact": True}, {"tick": 5, "pause": True}, {"tick": 6, "pause": False},
                        {"tick": 25, "pause": True})
            code, err, out = day_run(w, DOCK_NOW, fr)
            self.assertEqual(code, 0, err)
            rows = read_jsonl(out)
            self.assertEqual(events(rows, "paused")[0]["tick"], 6)
            self.assertEqual(events(rows, "resumed")[0]["tick"], 26)
            paused = [s for s in snapshots(rows) if s["state"] == "paused"]
            self.assertTrue(paused)
            self.assertEqual(len({s["sim_tick"] for s in paused}), 1)
            self.assertEqual(rows[-1]["ticks"] - rows[-1]["sim_tick"], 20)

    def test_p2_day_06_bad_flags_exit_2(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            for args in (["--mode", "day", "--days", "0"], ["--mode", "day", "--days", "6"],
                         ["--mode", "gather", "--days", "1"]):
                self.assertEqual(run_headless(*args, "--seed", "1", "--ticks", "1", "--out", out)[0], 2, args)
            for sc in ({"day": {"money": 10}}, {"day": {"money": 20, "earned": 10}},
                       {"quan": {"stock": {"ca_loc": 1}}}, {"day": {"upgrades": {"oxygen": 3}}}):
                p = write_json(w.path("s.json"), sc)
                self.assertEqual(run_headless("--mode", "day", "--seed", "1", "--ticks", "1", "--scenario", p,
                                              "--out", out)[0], 2, sc)

    def test_p2_day_07_deterministic(self):
        with Workdir() as w:
            fr = frames({"tick": 0, "move": [1, 0.3]}, {"tick": 400, "interact": True})
            a = day_run(w, {}, fr, ticks=3000, name="a")[2]
            b = day_run(w, {}, fr, ticks=3000, name="b")[2]
            with open(a, "rb") as fa, open(b, "rb") as fb:
                self.assertEqual(fa.read(), fb.read())


if __name__ == "__main__":
    unittest.main()
