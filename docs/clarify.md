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
