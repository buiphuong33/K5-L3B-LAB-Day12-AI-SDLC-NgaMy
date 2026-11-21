# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21 | Gather lát 1: tick oxy vừa về 0 có tính vào bộ đếm ngạt không? | **Giả định:** có. Đếm khi oxy = 0 sau cập nhật và còn dưới nước, nên `choke` xảy ra 60 tick sau tick có `oxygen_empty` (khớp `zero_oxy_ticks` ∈ [0, 59] trong `scenario.py`). Cần đối chiếu PRD-0 mục 13.8. | Tâm (chờ GV xác nhận) |
| 2 | 2026-11-21 | Lên mặt nước có reset bộ đếm ngạt không? | **Giả định:** có, `zero_oxy_ticks = 0` khi ở mặt nước hoặc khi oxy > 0. | Tâm (chờ GV xác nhận) |
| 3 | 2026-11-21 | `data` của các sự kiện `oxygen_empty` / `choke` / `faint` gồm gì? | **Giả định:** `oxygen_empty {pos}`, `choke {hp}` (Máu sau khi trừ), `faint {pos, lost:{items}}`. `dive`/`surface` dùng `{pos}` theo khung. Cần đối chiếu PRD-0 mục E. | Tâm (chờ GV xác nhận) |
| 4 | 2026-11-21 | `invuln_ticks` có chặn trừ Máu do ngạt không? | **Giả định:** không. `invuln_ticks` dành cho sát thương của phase sau, còn ngạt vẫn trừ Máu. | Tâm (chờ GV xác nhận) |
| 5 | 2026-11-21 | Gather lát 2: giỏ còn chỗ nhưng không đủ cho cả mẻ (ví dụ cá linh cho 3, giỏ còn 2) thì sao? | **Giả định:** không lấy một phần. Phát `hold_full`, đàn cá hoặc nút giữ nguyên. | Tâm (chờ GV xác nhận) |
| 6 | 2026-11-21 | Bấm `catch` trượt (không có cá trong `catch_radius`) có tốn hồi chiêu không? | **Giả định:** có. Mỗi lần `catch` hợp lệ (dưới nước, hết hồi chiêu) đều đặt `catch_cd_ticks`, kể cả bắt trượt hoặc `hold_full`. | Tâm (chờ GV xác nhận) |
| 7 | 2026-11-21 | Đàn cá bị bắt thì còn trên sông không? | **Giả định:** biến mất khỏi `fish[]`. Phase 1 chưa có cá sinh lại. | Tâm (chờ GV xác nhận) |
| 8 | 2026-11-21 | `data` của `gather` / `fish_caught` / `hold_full`? | **Giả định:** `gather {node_id, kind, count}`, `fish_caught {fish_id, kind, count}`, `hold_full {target_id, kind}`. | Tâm (chờ GV xác nhận) |
