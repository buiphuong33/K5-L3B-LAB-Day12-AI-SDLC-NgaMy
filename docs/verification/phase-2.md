# Ma trận truy vết Phase 2

Nguồn yêu cầu khả dụng: TICKET-02 và giao diện chốt trong [`TEAM.md`](../../TEAM.md). Bằng chứng hiện có: [`regression-baseline.md`](../proof/phase-2/regression-baseline.md), [`monster-unit.md`](../proof/phase-2/monster-unit.md).

| AC / phạm vi | Cách kiểm chứng dự kiến | Phụ thuộc | Kết quả |
|---|---|---|---|
| Regression toàn bộ Phase 1/2 hiện có | `python3 -m unittest discover -s tests -v` | Không | Đạt: 66/66 |
| Test Contract v1.1 và số chuẩn cá sấu | Đọc `contract_version`, `tuning.gather.monsters` | Không | Đạt |
| Khởi tạo M1/M2 theo Ngày và snapshot sắp theo id | `tests/test_p2_monsters.py` | Ráp vào gather | Đạt unit |
| Patrol waypoint, chase hysteresis và recoil đúng tick/khoảng cách | Fixture đọc contract thật, snapshot mỗi tick | Ráp vào gather | Đạt unit |
| Tối đa một `monster_hit` mỗi tick | Đặt M1/M2 cùng chạm người chơi, kiểm id ưu tiên | Không | Đạt unit |
| Trúng đòn mất Máu, rơi `ceil(loss_ratio × giỏ)` LIFO, bất tử 90 tick | Kiểm event, `hp`, `hold`, `invuln_ticks` | Không | Đạt unit |
| Máu về 0 phát `faint` do quái và kết thúc gather | Kiểm event, kho rỗng, `gather_end` | Tâm ráp `MonsterSet` vào `gather.py` | Đạt unit; chờ headless |
| Scenario `monsters[]` sai trả mã 2 | `test_bad_monster_scenario_exits_2` qua `headless_cmd` | Không | Đạt |
| Cùng seed cho chuyển động/snapshot giống từng byte | Chạy fixture cá sấu hai lần | Tích hợp gather hoàn tất | Chưa chạy |
| Smoke `gather --inventory-out` sang `quan --inventory` | `test_smoke_p1.Integration` | Không | Đạt, chưa có quái |
| Smoke `day --days 1` và nhiều Ngày | `tests/test_p2_day.py` | Không | Đạt, chưa có quái |

## Đánh giá ngắn

- Phase 1 vẫn xanh sau khi contract đổi sang v1.1; test cũ đã đọc số đàn cá từ contract và chấp nhận mode `day`.
- `MonsterSet` đọc trực tiếp schema v1.1; 8/8 test cá sấu và 66/66 toàn suite đạt.
- Khi Tâm ráp `MonsterSet.step(player, events)` vào `gather.py`, chạy lại toàn bộ regression trước smoke tích hợp.
