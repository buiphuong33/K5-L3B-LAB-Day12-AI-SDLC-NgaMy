# Kiểm chứng lát cá sấu Phase 2

- Ngày: 2026-11-21 (Asia/Bangkok)
- Commit code được kiểm: `ee2ee05`
- Môi trường: Windows, Python 3.10.1
- Contract tại thời điểm kiểm: v1.1; test đọc trực tiếp `tuning.gather.monsters`

## Lệnh và kết quả

```bash
PYTHONPATH=tests:. python3 -m unittest tests.test_p2_monsters -v
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

- Test tập trung cá sấu: **8 chạy, 0 trượt, 0 lỗi**.
- Toàn bộ regression: **66 chạy, 0 trượt, 0 lỗi**.

## Phạm vi đã kiểm

- M1 có từ Ngày 1, M2 có từ Ngày 3; snapshot sắp id số (`M2` trước `M10`).
- Patrol theo hai waypoint, chase dùng hysteresis `detect_radius`/`exit_radius`.
- Mỗi tick tối đa một hit, ưu tiên id nhỏ; rơi `ceil(loss_ratio × số đồ)` theo LIFO; bất tử đọc từ contract.
- Recoil chạy đủ `recoil_ticks` và tổng `recoil_dist`; hit chí mạng phát `faint` do quái, xóa giỏ và kết thúc gather khi player cung cấp `_finish`.
- Scenario quái thiếu waypoint bị headless từ chối với mã 2.

## Bàn giao tích hợp

Khởi tạo `MonsterSet(gather_tuning["monsters"], gather_tuning["bounds"], tuning["tick_hz"], current_day, scenario.get("monsters"))`. Tâm gọi `step(player, events)` và ghép `snapshot()` vào snapshot gather. Contract/scenario v1.1 đã sẵn sàng; headless có quái vẫn chờ Tâm ráp module vào `gather.py` cùng lát cá.
