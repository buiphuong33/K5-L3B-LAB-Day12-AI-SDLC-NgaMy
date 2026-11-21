# Ma trận truy vết Phase 3

Bằng chứng hiện có: [`regression-baseline.md`](../proof/phase-3/regression-baseline.md) và
[`migration-precheck.md`](../proof/phase-3/migration-precheck.md).

| AC / phạm vi | Cách kiểm chứng | Phụ thuộc | Kết quả |
|---|---|---|---|
| Regression trên `main` sau khi có `items.py` | Toàn bộ `unittest` | Không | Đạt: 92/92 |
| `monster_hit.lost` là mảng cá thể LIFO, giữ `id/kind/fresh` | `test_p3_smoke.MigrationSmoke` | Không | Đạt |
| Contract v1.2 và khối `freshness` | Đọc `game.contract.json` | Phương | Có khối `freshness`; contract còn 1.1 đúng kế hoạch tích hợp |
| Fixture P1–P2 dùng schema cá thể | Helper chọn schema theo contract; chạy toàn suite | gather và quan v1.2 | Đã chuẩn bị; chờ chạy bản tích hợp |
| Ngưỡng 30: chỉ ươn sau khi đi xuống dưới ngưỡng, phát một lần | `test_p3_smoke.MigrationSmoke` | Không | Đạt |
| Gather hao 0.5/s từ bước sau; `spoiled` tại hold | `test_p3_gather.GatherFreshUnit` | Tâm | Nhánh `p3-gather-fresh` chưa nhập `main` |
| Quán hao 0.25/s; `spoiled` tại stock | Test ngưỡng 7200 quanh hai tick | Nga | Chưa chạy |
| File kho cá thể round-trip; kho đếm cũ bị từ chối ở v1.2 | `test_p3_smoke.MigrationSmoke` | Không | Đạt ở lớp đọc/ghi; smoke tiến trình chờ tích hợp |
| Bàn giao gather → day → quan cùng tick, không hao thêm | Smoke `day --days 1` | Phương/Tâm/Nga | Chưa chạy |
| Id `I` tăng liên tục xuyên pha và Ngày | Đọc event/snapshot nhiều Ngày | Phương | Chưa chạy |
| Giá món theo độ tươi và `cook_started.items` | Fixture quán v1.2 | Nga | Chưa chạy |

## Đánh giá ngắn

- Phase 2 đã tích hợp cá, Cá Sấu, quán và vòng ngày; tag `phase-2` có bằng chứng 78/78 test đạt.
- `chonoi/items.py`, schema file và bàn giao `day` đã có trên `main`; contract vẫn giữ 1.1 để nhánh chính xanh trong lúc chờ hai module luật.
- QA đã chuyển fixture P1–P2 theo `contract_version`, thêm smoke ngưỡng 30/file và xác nhận 92/92. Chưa thể kết luận Phase 3 tích hợp cho tới khi gather, quan và contract 1.2 được nhập cùng nhau.
