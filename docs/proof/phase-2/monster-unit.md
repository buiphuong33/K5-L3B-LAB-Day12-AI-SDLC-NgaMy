# Kiểm chứng lát cá sấu Phase 2

- Ngày: 2026-11-21 (Asia/Bangkok)
- Commit code được kiểm: `da4ed57`
- Môi trường: Windows, Python 3.10.1
- Contract tại thời điểm kiểm: v1.0; test dùng tuning fixture truyền vào module

## Lệnh và kết quả

```bash
PYTHONPATH=tests:. python3 -m unittest tests.test_p2_monsters -v
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

- Test tập trung cá sấu: **6 chạy, 0 trượt, 0 lỗi**.
- Toàn bộ regression: **57 chạy, 0 trượt, 0 lỗi**.

## Phạm vi đã kiểm

- Snapshot sắp id số (`M2` trước `M10`), patrol phản xạ ở mép và chase hướng tới người chơi.
- Mỗi tick tối đa một hit, ưu tiên id nhỏ; rơi đồ LIFO; gán đúng `invuln_ticks` từ tuning.
- Recoil sau va chạm; hit chí mạng phát `faint` do quái, xóa giỏ và kết thúc gather khi player cung cấp `_finish`.
- Thiếu tuning bắt buộc bị từ chối, không có số gameplay hard-code trong luật.

## Bàn giao tích hợp

Khởi tạo `MonsterSet(monsters, settings, bounds)`. `settings` cần các khóa `tick_hz`, `patrol_speed`, `chase_speed`, `chase_radius`, `hit_radius`, `recoil_distance`, `hit_damage`, `drop_count`, `invuln_ticks`; mỗi quái cần `id`, `pos`, `patrol_x` và có thể có `kind`, `heading_deg`, `state`. Tâm gọi `step(player, events)` và ghép `snapshot()` vào snapshot gather. Headless v1.1 và scenario `monsters[]` vẫn chờ contract/integration của Phương, Tâm và Nga.
