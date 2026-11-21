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
| 8 | 2026-11-21 | P2 cá: cá bơi theo trục nào? `fish_depths` dùng để làm gì? | **Giả định:** cá chỉ bơi ngang (hướng 0°/180°, tốc độ `fish_speed`) và giữ nguyên độ sâu. `fish_depths` là dải hợp lệ theo loài, dùng khi kiểm `fish[]` trong scenario. | Tâm (chờ TICKET-02) |
| 9 | 2026-11-21 | P2 cá: chạm mép `fish_x` thì sao? | **Giả định:** gập phần vượt mép vào trong và đảo hướng, cùng cách patrol của quái. | Tâm (chờ TICKET-02) |
| 10 | 2026-11-21 | P2 cá: mỗi `fish_turn_ticks` thì đổi hướng thế nào? | **Giả định:** duyệt cá theo id, mỗi đàn rút 1 số từ luồng `fish_turn`; số < 0.5 thì đảo chiều. | Tâm (chờ TICKET-02) |
| 11 | 2026-11-21 | P2 cá: sinh cá rút số theo thứ tự nào? | **Giả định:** luồng `fish_spawn`, lần lượt rút: loài (theo `fish_weights`, duyệt loài theo tên) → độ sâu (đều trong `fish_spawn_depths[loài]`) → x (chọn đều trong các ô `fish_spawn_x` cách mọi đàn ≥ `fish_spawn_clearance`) → hướng (0/180). Không còn ô hợp lệ thì bỏ lượt. | Tâm (chờ TICKET-02) |
| 12 | 2026-11-21 | P2 cá: `data` của `fish_spawned`? `random_fish:false` có tắt sinh cá không? | **Giả định:** `{fish_id, kind, pos, heading_deg}`. `random_fish:false` tắt cả cá mặc định lẫn sinh cá. | Tâm (chờ TICKET-02) |
| 13 | 2026-11-21 | P2: cá bơi ở đâu trong thứ tự một bước của gather? | **Giả định:** ngay sau đồng hồ và nút mọc lại, trước khi người chơi bơi. Quái ráp sau, khi `monsters.py` khớp v1.1. | Tâm (chờ TICKET-02 mục 4.5) |
