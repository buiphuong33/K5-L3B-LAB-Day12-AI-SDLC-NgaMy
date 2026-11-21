# Ma trận truy vết Phase 3

Commit code: `3973760`, contract v1.2. Bằng chứng: [`integration.md`](../proof/phase-3/integration.md), [`regression-baseline.md`](../proof/phase-3/regression-baseline.md), [`migration-precheck.md`](../proof/phase-3/migration-precheck.md). Quyết định đổi schema: [`ADR 0001`](../adr/0001-kho-ca-the-v12.md).

| AC / phạm vi | Cách kiểm chứng | Kết quả |
|---|---|---|
| Contract v1.2 và khối `freshness` | `game.contract.json`, `chonoi/contract.py` | Đạt |
| Kho cá thể qua file, ghi đúng schema, snapshot quán khớp chính xác | `test_p3_quan.Handoff`, `integration.md` | Đạt |
| Kho đếm, sai schema, id trùng, `fresh` ngoài miền trả mã 2 | `test_p3_inventory`, `test_p3_quan.Handoff` | Đạt |
| Bàn giao trong `day` cùng tick, id mới ở Ngày kế | `test_p3_smoke`, `integration.md` | Đạt |
| Gather hao 0.5/s từ bước sau, `spoiled` tại `hold` | `test_p3_gather`, `integration.md` | Đạt |
| Quán hao 0.25/s, `spoiled` tại `stock` đúng tick, theo id | `test_p3_quan.QuanFreshness` | Đạt |
| Giá trị đọc lại từ file giữ đúng nhánh ở ngưỡng 30 | `test_reloaded_value_keeps_threshold_branch` | Đạt |
| Giữ chỗ theo id, tươi nhất rồi id nhỏ | `test_default_reservation_takes_freshest_then_id` | Đạt |
| Nhả và giữ lại khi hàng vừa ươn, thiếu thì `unfulfillable` | `test_reservation_retries_*`, `test_unfulfillable_*` | Đạt |
| Giá theo độ tươi, `cook_started.items` sắp theo kind rồi id | `test_price_floor_from_average_fresh` | Đạt |
| `lost` là mảng cá thể LIFO | `test_p3_smoke.MigrationSmoke` | Đạt |
| Tất định qua 5 Ngày | `integration.md` | Đạt |
| Regression P1–P2 | Toàn bộ test, 115/115 | Đạt |
| HUD độ tươi trên trình duyệt | Có mã hiển thị, chưa chơi thử | **Chưa xác nhận** |

## Test và khung đổi vì luật mới

- Fixture P1–P2 chuyển sang cá thể theo `contract_version` (Huyền).
- `chonoi/contract.py` đưa `contract_version` vào tuning, vì `gather` chọn schema kho theo phiên bản (ADR 0001).
- `chonoi/jsonl.py` không làm tròn `fresh`, vì v1.2 yêu cầu so chính xác snapshot quán với file kho.
- `chonoi/items.py` khôi phục giá trị chính xác trên lưới 1/240 khi đọc lại, để giữ đúng nhánh ở ngưỡng 30.
