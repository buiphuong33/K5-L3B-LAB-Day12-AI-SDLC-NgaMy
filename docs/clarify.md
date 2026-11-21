# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21 | Tick oxy vừa về 0 có tính vào bộ đếm ngạt không? | **Theo PRD-0 mục F:** có, ngạt lần đầu ở t+59. | PRD |
| 2 | 2026-11-21 | Lên mặt nước có reset bộ đếm ngạt không? | **Theo PRD-0 mục F:** có. | PRD |
| 3 | 2026-11-21 | `data` của `oxygen_empty` / `choke` / `faint` gồm gì? | **Theo PRD-0 mục E:** `{oxygen_ticks:0}`, `{hp}`, `{cause:"choke",lost,hp:0}`, `lost` là mảng LIFO. | PRD |
| 4 | 2026-11-21 | `invuln_ticks` có chặn trừ Máu do ngạt không? | **Giả định:** không. `invuln_ticks` dành cho sát thương của phase sau, còn ngạt vẫn trừ Máu. | Tâm (chờ GV xác nhận) |
| 5 | 2026-11-21 | Fixture khách thiếu `reserved` mà kho không đủ thì xử lý sao? | **Giả định:** mã 2, theo quy tắc "giữ quá tồn" ở mục D. Chưa hỏi Anh Năm. | Nhóm (chờ xác nhận) |
| 6 | 2026-11-21 | Tay đang bưng món có được bắt đầu nấu đơn khác không? | **Giả định:** được, mục F chỉ yêu cầu tay trống khi lấy món từ bếp. Chưa hỏi Anh Năm. | Nhóm (chờ xác nhận) |
| 7 | 2026-11-21 | Khách ăn xong đúng tick đóng ca thì `paid.reason` là gì? | **Giả định:** `finished_eating`; `closing` dành cho khách còn đang ăn. Chưa hỏi Anh Năm. | Nhóm (chờ xác nhận) |
| 8 | 2026-11-21 | Cá đổi hướng và hướng ban đầu theo phân phối nào? | **Giả định:** đều trong [0°, 360°) theo seed. Chưa hỏi Anh Năm. | Nhóm (chờ xác nhận) |
| 9 | 2026-11-21 | 8 đàn đầu ca chọn loài và điểm thế nào? | **Giả định:** dùng cùng trọng số và điều kiện cách > 1 m như sinh theo lịch. Chưa hỏi Anh Năm. | Nhóm (chờ xác nhận) |
| 10 | 2026-11-21 | JSONL có làm tròn `fresh` 3 chữ số như tọa độ không? | **Giả định:** không, vì mục smoke của TICKET-03 yêu cầu so chính xác độ tươi giữa snapshot quán và file. Chưa hỏi Anh Năm. | Nhóm (chờ xác nhận) |
| 11 | 2026-11-21 | (Kiểm lại #10) Bàn giao file kho có giữ đúng độ tươi không? | **Đã kiểm trên `main` (2587be3):** smoke của TICKET-03 (fresh 100, cập bến ở frame 0, `quan --ticks 0`) cho file `fresh: 99.99166666666666` và snapshot `stock` cùng giá trị — khớp chính xác, trong dung sai ±0.01 của ticket. | Tâm (đã kiểm) |
| 12 | 2026-11-21 | P4: "chạy được trong tối đa 3 lệnh" tính những gì? | **Giả định:** tính lệnh gõ trong terminal từ máy chưa có repo: `git clone`, `cd`, `python3 -m chonoi.live --mode day`. Mở trình duyệt theo địa chỉ in ra không tính là lệnh. Có test `tests/test_p4_package.py` giữ README ≤ 3 lệnh. | Tâm (chờ GV xác nhận) |
| 13 | 2026-11-21 | P4: "bản đóng gói chạy được" là gì khi game là Python thuần? | **Giả định:** file zip mã nguồn từ đúng commit bàn giao (`tools/package_release.py`, `git archive`), chạy bằng Python ≥ 3.10 có sẵn, không cần cài gói; không đóng băng thành file thực thi. Có `--check` giải nén và chạy headless từ bản zip. | Tâm (chờ GV xác nhận) |
| 14 | 2026-11-21 | P4: yêu cầu môi trường tối thiểu? | **Giả định:** Python 3.10+ (QA chạy đạt trên 3.10.1, Tâm trên 3.13.7), chỉ thư viện chuẩn; trình duyệt hiện đại. Lệnh chấm dùng `python3` trên macOS/Linux; Windows không có `python3` nên README ghi dùng `python` và `PYTHONPATH=tests;.`. | Tâm |
| 15 | 2026-11-21 | P4: giấy phép phát hành? | **Quyết định:** MIT cho phần của nhóm; khung starter, nhân vật, bối cảnh ghi nguồn lab trong `LICENSE` và `CREDITS.md`. Không dùng asset ngoài (đã rà `chonoi/web/`). | Tâm (PO) |
| 16 | 2026-11-21 | P4: lệnh `bench_cmd` / `soak_cmd` cụ thể? | **Tạm theo TEAM.md:** `python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json`, `python3 -m chonoi.soak --seed 7 --days 10 --out soak.json`. Phương khai chính thức trong contract v1.3; khác thì sửa README. | Phương chốt |
