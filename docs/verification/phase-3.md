# Ma trận truy vết Phase 3

Bằng chứng hiện có: [`regression-baseline.md`](../proof/phase-3/regression-baseline.md).

| AC / phạm vi | Cách kiểm chứng | Phụ thuộc | Kết quả |
|---|---|---|---|
| Regression tại tag Phase 2 và test migration sớm | Toàn bộ `unittest` | Không | Đạt: 79/79 |
| `monster_hit.lost` là mảng cá thể LIFO, giữ `id/kind/fresh` | `test_p3_smoke.MigrationSmoke` | Không | Đạt |
| Contract v1.2 và khối `freshness` | Đọc `game.contract.json` | Phương | Chờ phụ thuộc |
| Fixture P1–P2 dùng schema cá thể | Chạy toàn suite sau migration | `items.py`, gather và quan v1.2 | Chưa chạy |
| Gather hao 0.5/s từ bước sau; `spoiled` tại hold | Test ngưỡng 7200 quanh hai tick | Tâm | Chưa chạy |
| Quán hao 0.25/s; `spoiled` tại stock | Test ngưỡng 7200 quanh hai tick | Nga | Chưa chạy |
| File kho cá thể và kho đếm cũ trả mã 2 | Smoke hai tiến trình | Phương/Tâm/Nga | Chưa chạy |
| Bàn giao gather → day → quan cùng tick, không hao thêm | Smoke `day --days 1` | Phương/Tâm/Nga | Chưa chạy |
| Id `I` tăng liên tục xuyên pha và Ngày | Đọc event/snapshot nhiều Ngày | Phương | Chưa chạy |
| Giá món theo độ tươi và `cook_started.items` | Fixture quán v1.2 | Nga | Chưa chạy |

## Đánh giá ngắn

- Phase 2 đã tích hợp cá, Cá Sấu, quán và vòng ngày; tag `phase-2` có bằng chứng 78/78 test đạt.
- Phase 3 chưa có `chonoi/items.py`, contract vẫn v1.1. Chỉ triển khai test migration không phụ thuộc trước; không tự tạo schema ngoài giao diện đã chốt trong `TEAM.md`.
