# Ma trận truy vết Phase 4

Bằng chứng QA: [`benchmark.md`](../proof/phase-4/benchmark.md),
[`bench.json`](../proof/phase-4/bench.json), [`regression.md`](../proof/phase-4/regression.md)
và [`integration-progress.md`](../proof/phase-4/integration-progress.md).

| AC / phạm vi | Cách kiểm chứng | Chủ / phụ thuộc | Kết quả |
|---|---|---|---|
| `bench_cmd --seed --duration --out` | `test_p4_bench.BenchUnit` | Huyền | Đạt |
| Render đúng cảnh gather mặc định ở 1280×720 | Browser thật, viewport được trình duyệt báo lại | Huyền | Đạt |
| Làm nóng 3 s, đo 30 s | Instrument `requestAnimationFrame`; `measured_s` trong artifact | Huyền | Đạt: 30,068 s |
| JSON đúng 5 trường, ghi nguyên tử, artifact đo đủ 30 s | Unit test và `BenchArtifact` | Huyền | Đạt |
| Hiệu năng renderer | Chrome headless trên UI commit `2587be3` | Huyền / Phương | 13,569 FPS; 1% low 8,351 FPS - rủi ro release |
| Regression P1–P3 và các lát P4 hiện có | Toàn bộ `unittest` | Cả nhóm | Đạt: 125/125 |
| Contract v1.3 khai `bench_cmd`, `soak_cmd` | Đọc `game.contract.json`, test contract | Phương | Chờ tích hợp |
| Ngày 6–10 lặp kế hoạch D1–D5 | `test_p4_contract.py` | Phương | Chờ tích hợp |
| Ba cảnh báo và tương phản cao | Review mã UI | Phương, Huyền review | Chưa đạt: có thanh/màu cảnh báo, chưa thấy chế độ tương phản cao |
| Soak 10 Ngày, đúng 5 trường | `test_p4_soak.py`, chạy chéo và so `soak.json` | Nga, Huyền review | Đạt: 10/10 ngày, 0 crash, kết quả khớp |
| Clone sạch và gói release tối đa 3 lệnh | `test_p4_package.py` | Tâm | Có trên `origin/p4-package`, chưa nhập `main` |

## Kết luận QA hiện tại

Benchmark và soak đã hoàn thành, regression xanh. FPS giảm rõ sau thay đổi đồ họa chi tiết; đây không phải lỗi schema nhưng cần Phương cân nhắc giảm chi phí vẽ trước khi chốt release. Chưa thể kết luận toàn Phase 4 cho tới khi contract v1.3, package và cảnh báo/tương phản cao được nhập `main`.
