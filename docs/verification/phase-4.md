# Ma trận truy vết Phase 4

Bằng chứng QA: [`benchmark.md`](../proof/phase-4/benchmark.md),
[`bench.json`](../proof/phase-4/bench.json) và [`regression.md`](../proof/phase-4/regression.md).

| AC / phạm vi | Cách kiểm chứng | Chủ / phụ thuộc | Kết quả |
|---|---|---|---|
| `bench_cmd --seed --duration --out` | `test_p4_bench.BenchUnit` | Huyền | Đạt |
| Render đúng cảnh gather mặc định ở 1280×720 | Browser thật, viewport được trình duyệt báo lại | Huyền | Đạt |
| Làm nóng 3 s, đo 30 s | Instrument `requestAnimationFrame`; `measured_s` trong artifact | Huyền | Đạt: 30,068 s |
| JSON đúng 5 trường, ghi nguyên tử | Unit test và đọc `bench.json` | Huyền | Đạt |
| Hiệu năng renderer | Chrome headless trên UI commit `2587be3` | Huyền / Phương | 13,569 FPS; 1% low 8,351 FPS - rủi ro release |
| Regression P1–P3 | Toàn bộ `unittest` | Cả nhóm | Đạt: 120/120 |
| Contract v1.3 khai `bench_cmd`, `soak_cmd` | Đọc `game.contract.json`, test contract | Phương | Chờ tích hợp |
| Ngày 6–10 lặp kế hoạch D1–D5 | `test_p4_contract.py` | Phương | Chờ tích hợp |
| Ba cảnh báo và tương phản cao | Review/chơi thử UI | Phương, Huyền review | Chờ tích hợp |
| Soak 10 Ngày, đúng 5 trường | `test_p4_soak.py`, `soak.json` | Nga | Chờ tích hợp |
| Clone sạch và gói release tối đa 3 lệnh | `test_p4_package.py` | Tâm | Chờ tích hợp |

## Kết luận QA hiện tại

Lát benchmark đã hoàn thành và regression xanh. FPS giảm rõ sau thay đổi đồ họa chi tiết; đây không phải lỗi schema nhưng cần Phương cân nhắc giảm chi phí vẽ trước khi chốt release. Chưa thể kết luận toàn Phase 4 cho tới khi contract, soak, package và cảnh báo được nhập `main`.
