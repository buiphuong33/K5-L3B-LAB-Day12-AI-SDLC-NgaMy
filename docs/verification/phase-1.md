# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| CON-01: snapshot tick 0 và đúng một dòng end | `tests.test_smoke_p1.Contract.test_con_01_ticks_zero_and_end_line` | [`qa-baseline.md`](../proof/phase-1/qa-baseline.md) | Đạt |
| CON-02: cùng seed cho output giống từng byte | `tests.test_determinism` cho `gather` và `quan` | [`qa-baseline.md`](../proof/phase-1/qa-baseline.md) | Đạt |
| CON-03: input/mode sai trả mã 2, không tạo output | Các test `test_con_03_*` trong `tests/test_smoke_p1.py` | [`qa-baseline.md`](../proof/phase-1/qa-baseline.md) | Đạt |
| MOVE-01..03: tốc độ, hướng và chặn biên | `tests.test_smoke_p1.Movement` | [`qa-baseline.md`](../proof/phase-1/qa-baseline.md) | Đạt |
| TIME: hết giờ đúng tick và giữ kho | `Movement.test_time_ends_gather_and_keeps_hold` | [`qa-baseline.md`](../proof/phase-1/qa-baseline.md) | Đạt |
| INV-01: gather xuất kho, quan đọc đúng | `tests.test_smoke_p1.Integration` | [`qa-baseline.md`](../proof/phase-1/qa-baseline.md) | Đạt |
| Scenario/fixture ngoài miền bị từ chối | `Contract.test_scenario_out_of_domain_exit_2` và `ScenarioModes` | [`qa-baseline.md`](../proof/phase-1/qa-baseline.md) | Đạt |

## Đánh giá ngắn
- Yêu cầu nào đạt / chưa đạt: Các AC công khai của Phase 1 trong ma trận đều đạt; toàn bộ 33 test hiện có chạy xanh.
- Điều cần chỉnh cho phase sau: bổ sung hàng AC ngay khi yêu cầu phase mở; chạy lại toàn suite sau mỗi lát luật và trước khi gắn tag.
